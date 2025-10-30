import json
import traceback
import os
import copy
import subprocess
import platform
from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout
                               , QFileDialog, QLabel, QLineEdit,
                                 QTextEdit, QHBoxLayout, QMessageBox, 
                                 QTableWidget, QTableWidgetItem, 
                                 QProgressBar, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QIntValidator
from data_io.excel_io import read_input_excel, write_output_excel
from core.grouping_algorithm import build_groups
from core.validation import validate_config, validate_carpets
from .ui_utils import ( setup_button_animations,
                       _create_section_card)
from .theme_manager import  (apply_dark_theme, apply_light_theme, 
                             save_theme_preference, load_theme_preference)

class WorkerSignals(QObject):
    progress = Signal(int)              # 0-100
    log = Signal(str)
    finished = Signal()
    error = Signal(str)
    data_ready = Signal(list, list, dict)  # groups, remaining, stats

class GroupingWorker(QThread):
    def __init__(self, input_path, output_path, min_width, max_width, tolerance_len, cfg):
        super().__init__()
        self.signals = WorkerSignals()
        self.input_path = input_path
        self.output_path = output_path
        self.min_width = min_width
        self.max_width = max_width
        self.tolerance_len = tolerance_len
        self.cfg = cfg
        self._is_interrupted = False

    def run(self):
        try:
            #  مرحلة 1: القراءة
            self.signals.progress.emit(10)
            self.signals.log.emit("📖 بدء قراءة ملف البيانات...")
            carpets = read_input_excel(self.input_path)
            self.signals.log.emit(f"✅ تم قراءة {len(carpets)} نوع من السجاد")

            # تحقق سريع
            errs = validate_carpets(carpets)
            if errs:
                for e in errs:
                    self.signals.log.emit(f"⚠️ {e}")

            self.signals.progress.emit(20)
            original_carpets = copy.deepcopy(carpets)

            # إعادة تجميع البواقي أولاً
            self.signals.progress.emit(40)
            self.signals.log.emit("🔄 بدء تشكيل المجموعات..")
            groups = build_groups(
                carpets=carpets,
                min_width=self.min_width,
                max_width=self.max_width,
                max_partner=self.cfg.get('max_partner', 5)
            )
            self.signals.log.emit(f"✅ تم تشكيل {len(groups)} مجموعة")

            # ✅ حساب المتبقيات
            self.signals.progress.emit(70)
            remaining = [c for  c in carpets if c.rem_qty > 0]
            self.signals.log.emit(f"📦 السجاد المتبقي: {len(remaining)} نوع")

            total_original = sum(c.qty for c in original_carpets)
            total_used = sum(g.total_qty() for g in groups)
            utilization = (total_used / total_original * 100) if  total_original > 0 else 0

            quantity_stats = {
                'total_original': total_original,
                'total_used': total_used,
                'total_remaining': total_original - total_used,
                'utilization_percentage': utilization
            }

            # حفظ
            self.signals.progress.emit(80)
            self.signals.log.emit("💾 حفظ النتائج...")
            write_output_excel(
                path=self.output_path,
                groups=groups,
                remaining=remaining,
                min_width=self.min_width,
                max_width=self.max_width,
                originals=original_carpets
            )
                               
            self.signals.log.emit(f"✅ تم حفظ النتائج في: {self.output_path}")

            # انتهى
            self.signals.progress.emit(100)
            self.signals.data_ready.emit(groups, remaining, quantity_stats)
            self.signals.finished.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit(str(tb))

class RectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()
        self.setObjectName("mainWindow")  # Set object name for CSS selector
        self.setWindowTitle("تجميع السجاد - نظام محسن")

        self.config_path = config_path
        self.config = self.load_config()

        self.create_window_controls()

        try:
            load_theme_preference(self)
        except:
            self.is_dark_theme = True

        self.is_running = False

        # إنشاء منطقة التمرير للمحتوى الرئيسي
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        content_widget = QWidget()
        # content_widget.setStyleSheet("")

        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        title_label = QLabel("🏠 تجميع السجاد")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        # self.quick_action_layout = QHBoxLayout()
        # self.quick_action_layout.setSpacing(12)

        # header_layout.addLayout(self.quick_action_layout)
        # content_layout.addLayout(header_layout)

        files_section, files_layout = _create_section_card(self, "📁 إعدادات الملفات")
        files_layout.setSpacing(10)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)  # تقليل المساحات في تخطيط الإدخال
        self.input_edit = QLineEdit()
        self.input_edit.setMinimumWidth(400)
        self.input_edit.setPlaceholderText("اختر ملف Excel للبيانات...")
        self.input_edit.setToolTip("اختر ملف Excel يحتوي على بيانات السجاد (الأعمدة: ID، العرض، الطول، الكمية)")
        self.input_btn = QPushButton("📂 اختيار الإدخال")
        self.input_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.input_btn.setMinimumHeight(40)
        self.input_btn.clicked.connect(self.browse_input)
        self.input_btn.setToolTip("فتح نافذة اختيار الملف لتحديد ملف البيانات")
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.input_btn)
        files_layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        self.output_edit = QLineEdit()
        self.output_edit.setMinimumWidth(400)
        self.output_edit.setPlaceholderText("حدد مكان حفظ النتائج...")
        self.output_edit.setToolTip("مسار حفظ ملفات النتائج (Excel و PDF)")
        self.output_btn = QPushButton("💾 حفظ الإخراج")
        self.output_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.output_btn.setMinimumHeight(40)
        self.output_btn.clicked.connect(self.browse_output)
        self.output_btn.setToolTip("فتح نافذة حفظ الملف لتحديد مكان حفظ النتائج")
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_btn)
        files_layout.addLayout(output_layout)

        content_layout.addWidget(files_section)

        settings_section, settings_layout = _create_section_card(self, "⚙️ إعدادات المعالجة")

        main_settings_layout = QHBoxLayout()
        main_settings_layout.setSpacing(18)

        # العرض الأدنى
        min_width_label = QLabel("العرض الأدنى:")
        min_width_label.setFixedWidth(100)
        min_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.min_width_edit = QLineEdit()
        self.min_width_edit.setText(str(self.config.get('min_width', 370)))
        self.min_width_edit.setPlaceholderText("370")
        self.min_width_edit.setFixedWidth(120)
        self.min_width_edit.setAlignment(Qt.AlignCenter)
        self.min_width_edit.setValidator(QIntValidator(1, 1000, self))

        # العرض الأقصى
        max_width_label = QLabel("العرض الأقصى:")
        max_width_label.setFixedWidth(100)
        max_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.max_width_edit = QLineEdit()
        self.max_width_edit.setText(str(self.config.get('max_width', 400)))
        self.max_width_edit.setPlaceholderText("400")
        self.max_width_edit.setFixedWidth(120)
        self.max_width_edit.setAlignment(Qt.AlignCenter)
        self.min_width_edit.setValidator(QIntValidator(1, 1000, self))

        # هامش التسامح
        tolerance_label = QLabel("هامش التسامح:")
        tolerance_label.setFixedWidth(100)
        tolerance_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tolerance_edit = QLineEdit()
        self.tolerance_edit.setText(str(self.config.get('tolerance_length', 0)))
        self.tolerance_edit.setPlaceholderText("100")
        self.tolerance_edit.setFixedWidth(120)
        self.tolerance_edit.setAlignment(Qt.AlignCenter)
        self.tolerance_edit.setValidator(QIntValidator(0, 100, self))

        # main_settings_layout.addWidget(self.tolerance_edit)
        # main_settings_layout.addWidget(tolerance_label)
        main_settings_layout.addWidget(self.max_width_edit)
        main_settings_layout.addWidget(max_width_label)
        main_settings_layout.addWidget(self.min_width_edit)
        main_settings_layout.addWidget(min_width_label)
        
        settings_layout.addLayout(main_settings_layout)
        content_layout.addWidget(settings_section)

        control_section, control_layout = _create_section_card(self, "🚀 لوحة التحكم")

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(18)

        self.run_btn = QPushButton("▶️ بدء المعالجة")
        self.run_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.run_btn.setMinimumHeight(35)
        self.run_btn.clicked.connect(self.run_grouping)
        buttons_layout.addWidget(self.run_btn)

        self.cancel_btn = QPushButton("⏹️ إلغاء")
        self.cancel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.cancel_btn.setEnabled(False)  # معطل في البداية
        buttons_layout.addWidget(self.cancel_btn)

        progress_layout = QVBoxLayout()
        progress_label = QLabel("حالة المعالجة:")
        progress_label.setFont(QFont("Segoe UI", 9, QFont.Normal))
        progress_layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        progress_layout.addWidget(self.progress_bar)

        buttons_layout.addLayout(progress_layout)
        control_layout.addLayout(buttons_layout)

        # حالة التطبيق
        self.status_label = QLabel("✅ جاهز للتشغيل")
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #20c997;
                background-color: rgba(32, 201, 151, 0.1);
                border: 1px solid #20c997;
                border-radius: 4px;
                padding: 8px 16px;
                text-align: center;
            }
        """)
        control_layout.addWidget(self.status_label)

        content_layout.addWidget(control_section)

        results_section, results_layout = _create_section_card(self, "📊 النتائج والسجل")
        results_layout.setSpacing(20)

        log_label = QLabel("📝 سجل النشاطات:")
        log_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_layout.addWidget(log_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(400)
        self.log.setMinimumHeight(350)
        results_layout.addWidget(self.log)

        table_label = QLabel("📋 ملخص المجموعات:")
        table_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_layout.addWidget(table_label)

        self.summary_table = QTableWidget(0, 4)
        self.summary_table.setHorizontalHeaderLabels(["رقم المجموعة", "عدد الأنواع", "العرض الإجمالي", "الطول المرجعي"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.summary_table.setMinimumHeight(350)
        results_layout.addWidget(self.summary_table)

        open_excel_layout = QHBoxLayout()
        open_excel_layout.addStretch()

        self.open_excel_btn = QPushButton("📊 فتح ملف Excel")
        self.open_excel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.open_excel_btn.setMinimumHeight(35)
        self.open_excel_btn.setMinimumWidth(150)
        self.open_excel_btn.clicked.connect(self.open_excel_file)
        self.open_excel_btn.setVisible(False)
        open_excel_layout.addWidget(self.open_excel_btn)

        open_excel_layout.addStretch()
        results_layout.addLayout(open_excel_layout)
        content_layout.addWidget(results_section)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        main_window_layout = QVBoxLayout(self)
        main_window_layout.setContentsMargins(0, 0, 0, 0)
        main_window_layout.addWidget(self.toolbar)
        main_window_layout.addWidget(scroll_area)
        self.setLayout(main_window_layout)

        try:
            setup_button_animations(self)
        except:
            pass

        self.showMaximized()

        if self.is_dark_theme:
            apply_dark_theme(self)
        else:
            apply_light_theme(self)

    def create_window_controls(self):
        """إنشاء شريط أدوات مع زر التبديل بين السمات فقط"""
        self.toolbar = QWidget()
        self.toolbar.setFixedHeight(50)
        self.toolbar.setStyleSheet("""
            QWidget {
                border-bottom: 2px solid #007bff;
                border-radius: 8px;
                margin: 5px;
            }
        """)

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(15, 8, 15, 8)
        toolbar_layout.setSpacing(20)

        # عنوان التطبيق في الشريط
        title_label = QLabel("🏠 تجميع السجاد - نظام محسن")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #007bff;
                margin: 0;
                padding: 8px 16px;
                background-color: rgba(0, 123, 255, 0.1);
                border-radius: 6px;
            }
        """)
        toolbar_layout.addWidget(title_label)

        toolbar_layout.addStretch()

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(45, 35)
        self.theme_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #260F8FFF;
                color: #fff;
                border: 2px solid #007bff;
                border-radius: 8px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #1B15CEFF;
                border-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #090058FF;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar_layout.addWidget(self.theme_btn)

    def toggle_theme(self):
        """تبديل بين السمة الداكنة والفاتحة"""
        self.is_dark_theme = not self.is_dark_theme

        if self.is_dark_theme:
            # تطبيق السمة الداكنة
            self.theme_btn.setText("🌙")
            apply_dark_theme(self)
        else:
            # تطبيق السمة الفاتحة
            self.theme_btn.setText("☀️")
            apply_light_theme(self)
        try:
            save_theme_preference(self)
        except:
            pass
        
    def generate_output_path(self, input_path):
        """إنشاء مسار الإخراج التلقائي"""
        if not input_path:
            return ""

        dir_path = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)
        name_without_ext, _ = os.path.splitext(file_name)
        new_file_name = f"{name_without_ext}_result.xlsx"   
        return os.path.join(dir_path, new_file_name)

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف الاكسل","", 
                                            "Excel Files (*.xlsx *.xls);;All Files (*)"
                                            )
        if path:
            self.input_edit.setText(path)
            output_path = self.generate_output_path(path)
            self.output_edit.setText(output_path)

    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف الإخراج", "", 
                                            "Excel Files (*.xlsx *.xls);;All Files (*)"
                                            )
        if path:
            if not path.lower().endswith(('.xlsx', '.xls')):
                path += '.xlsx'
            self.output_edit.setText(path)

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                return {}
            return cfg
        except Exception as e:
            QMessageBox.warning(self, "Config", f"خطأ بتحميل الإعدادات : {e}")
            return {}

    def log_append(self, text):
        self.log.append(text)

    def run_grouping(self):
        if self.is_running:
            QMessageBox.information(self, "عملية قيد التشغيل",
                                  "هناك عملية معالجة قيد التشغيل حالياً."
                                  )
            return

        input_path = self.input_edit.text().strip()
        output_path = self.output_edit.text().strip()
        if not input_path or not output_path:
            QMessageBox.warning(self, "بيانات ناقصة", "يرجى اختيار ملف الإدخال وتحديد مكان حفظ الإخراج.")
            return

        # Get width values from input
        try:
            min_width = int(self.min_width_edit.text().strip())
            max_width = int(self.max_width_edit.text().strip())
            # tolerance_len = int(self.tolerance_edit.text().strip())

            if min_width <= 0 or max_width <= 0:
                QMessageBox.warning(self, "قيم خاطئة", "العرض الأدنى والأقصى يجب أن يكونا أكبر من 0")
                return
            if min_width >= max_width:
                QMessageBox.warning(self, "قيم خاطئة", "العرض الأدنى يجب أن يكون أقل من العرض الأقصى")
                return
            # if tolerance_len < 0:
            #     QMessageBox.warning(self, "قيم خاطئة", "هامش التسامح يجب أن يكون صفراً أو رقماً موجباً")
                return
        except ValueError:
            QMessageBox.warning(self, "قيم خاطئة", "يرجى إدخال أرقام صحيحة للعرض الأدنى والأقصى وهامش التسامح")
            return

       # read config validation
        cfg = self.config
        # ok, err = validate_config(min_width, max_width, tolerance_len)
        ok, err = validate_config(min_width, max_width,0)
        if not ok:
            QMessageBox.warning(self, "إعدادات خاطئة", err)
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔄 بدء المعالجة...")
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)  
        self.open_excel_btn.setVisible(False)
        self.is_running = True

        self.worker = GroupingWorker(input_path, output_path, min_width, max_width,0, cfg)
        self.worker.signals.progress.connect(lambda v: self.progress_bar.setValue(v))
        self.worker.signals.log.connect(self.log_append)
        self.worker.signals.data_ready.connect(self.update_summary_table)
        self.worker.signals.finished.connect(self.on_worker_finished)
        self.worker.signals.error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_finished(self):
        self.status_label.setText("✅ اكتملت المعالجة بنجاح!")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_excel_btn.setVisible(True)  
        self.is_running = False  
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

    def on_worker_error(self, tb_str):
        self.log_append("❌ خطأ في المعالجة:\n" + tb_str)
        self.status_label.setText("❌ حدث خطأ في المعالجة")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.is_running = False

    def update_summary_table(self, groups, remaining, stats):
        try:
            self.summary_table.setRowCount(0)

            for g in groups:
                row = self.summary_table.rowCount()
                self.summary_table.insertRow(row)
                self.summary_table.setItem(row, 0, QTableWidgetItem(f"مجموعة {g.group_id}"))
                self.summary_table.setItem(row, 1, QTableWidgetItem(str(len(g.items))))
                self.summary_table.setItem(row, 2, QTableWidgetItem(str(g.total_width())))
                self.summary_table.setItem(row, 3, QTableWidgetItem(str(g.total_height())))

            if remaining:
                self.log_append(f"📦 السجاد المتبقي ({len(remaining)} أنواع):")
                for carpet in remaining:
                    self.log_append(
                        f"  • معرف {carpet.id}: {carpet.width}×{carpet.height} "
                        f"(كمية متبقية: {carpet.rem_qty})"
                    )
            else:
                self.log_append("🎉 لا يوجد سجاد متبقي - تم استخدام جميع القطع!")

            if stats:
                utilization = stats.get('utilization_percentage', 0)
                self.log_append(f"📊 إحصائيات الكميات: استغلال {utilization:.2f}% من الكمية الإجمالية")

        except Exception as e:
            self.log_append(f"❌ خطأ في تحديث الجدول: {str(e)}")

    def cancel_operation(self):
        if not self.is_running or not hasattr(self, 'worker'):
            return
        try:
            if hasattr(self.worker, '_is_interrupted'):
                self.worker._is_interrupted = True

            self.status_label.setText("⏹️ تم إلغاء العملية")
            self.run_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.is_running = False

            self.log_append("⏹️ تم إلغاء العملية بواسطة المستخدم")

            self.open_excel_btn.setVisible(False)

        except Exception as e:
            self.log_append(f"❌ خطأ أثناء إلغاء العملية: {str(e)}")

    def open_excel_file(self):
        try:
            output_path = self.output_edit.text().strip()
            if not output_path:
                QMessageBox.warning(self, "مسار غير محدد", "لم يتم تحديد مسار ملف الإخراج بعد.")
                return

            if not os.path.exists(output_path):
                QMessageBox.warning(self, "ملف غير موجود", f"لم يتم العثور على ملف الإخراج في المسار:\n{output_path}")
                return

            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", output_path])
            else:
                subprocess.run(["xdg-open", output_path])

            self.log_append(f"✅ تم فتح ملف Excel: {output_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ في فتح الملف",
                               f"حدث خطأ أثناء محاولة فتح ملف Excel:\n{str(e)}")
            self.log_append(f"❌ خطأ في فتح ملف Excel: {str(e)}")