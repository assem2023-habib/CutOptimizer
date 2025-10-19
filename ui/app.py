import json
import traceback
import copy
import os
from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog,
                               QLabel, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QProgressBar, QFrame, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QIntValidator, QPixmap, QBrush, QPalette
from data_io.excel_io import read_input_excel, write_output_excel, exhaustively_regroup
from data_io.pdf_report import SimplePDFReport
from core.grouping import group_carpets_greedy, group_carpets_optimized
from core.validation import validate_config, validate_carpets
from data_io.remainder_optimizer import process_remainder_complete

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
            # مرحلة القراءة
            self.signals.progress.emit(10)
            self.signals.log.emit("📖 بدء قراءة ملف البيانات...")
            carpets = read_input_excel(self.input_path)

            # تحقق سريع
            errs = validate_carpets(carpets)
            if errs:
                for e in errs:
                    self.signals.log.emit(f"⚠️ {e}")

            # التجميع الأولي
            self.signals.progress.emit(30)
            self.signals.log.emit("🔄 تشكيل المجموعات الأولية...")
            originals_copy = [
                # نفس الهوية والأبعاد مع الكمية الأصلية
                type(c)(c.id, c.width, c.length, c.qty) if hasattr(c, 'id') else c
                for c in carpets
            ]
            groups, remaining = group_carpets_greedy(
                carpets,
                min_width=self.min_width,
                max_width=self.max_width,
                tolerance_length=self.tolerance_len,
                start_with_largest=self.cfg.get('start_with_largest', True),
            )
            self.signals.log.emit(f"✅ تم تشكيل {len(groups)} مجموعة أولية")

            # إعادة تجميع البواقي
            self.signals.progress.emit(60)
            self.signals.log.emit("🔄 إعادة تجميع البواقي...")
            rem_groups, rem_final_remaining, quantity_stats = process_remainder_complete(
                remaining,
                min_width=self.min_width,
                max_width=self.max_width,
                tolerance_length=self.tolerance_len,
                start_group_id=max([g.id for g in groups] + [0]) + 1,
                merge_after=True,
                verbose=False
            )
            self.signals.log.emit(f"✅ تم تشكيل {len(rem_groups)} مجموعة إضافية")

            # حفظ
            self.signals.progress.emit(80)
            self.signals.log.emit("💾 حفظ النتائج...")
            write_output_excel(self.output_path, groups, rem_final_remaining,
                               remainder_groups=rem_groups,
                               min_width=self.min_width, max_width=self.max_width,
                               tolerance_length=self.tolerance_len,
                               originals=originals_copy)
            # pdf_path = os.path.splitext(self.output_path)[0] + "_report.pdf"
            # pdf = SimplePDFReport(title="تقرير مجموعات السجاد")
            # pdf.groups_to_pdf(groups, pdf_path)
            # self.signals.log.emit(f"✅ حفظ Excel وPDF")

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

        # إنشاء شريط أدوات مع أزرار التحكم في النافذة
        self.create_window_controls()

        # تحميل تفضيل السمة من ملف التكوين
        self.load_theme_preference()

        # متغير لحفظ حالة السمة (داكن/فاتح)
        self.is_dark_theme = True

        # متغير لحفظ حالة التشغيل
        self.is_running = False

        # إنشاء منطقة التمرير للمحتوى الرئيسي
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1A1A1A;
            }
        """)

        # الويدجيت الداخلي للمنطقة القابلة للتمرير
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1A1A1A;")

        # تخطيط المحتوى الرئيسي مع المسافات والحشو المناسبين
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)

        # رأس التطبيق
        header_layout = QHBoxLayout()

        title_label = QLabel("🏠 تجميع السجاد")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # أزرار الإجراءات السريعة في الرأس
        self.quick_action_layout = QHBoxLayout()
        self.quick_action_layout.setSpacing(15)

        header_layout.addLayout(self.quick_action_layout)
        content_layout.addLayout(header_layout)

        # قسم إعدادات الملفات
        files_section, files_layout = self._create_section_card("📁 إعدادات الملفات")
        files_layout.setSpacing(12)

        # ملف الإدخال
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
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

        # ملف الإخراج
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
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

        # قسم إعدادات المعالجة - تخطيط أفقي واحد يحتوي على جميع العناصر
        settings_section, settings_layout = self._create_section_card("⚙️ إعدادات المعالجة")

        # تخطيط أفقي واحد لجميع العناصر
        main_settings_layout = QHBoxLayout()
        main_settings_layout.setSpacing(20)

        # العرض الأدنى
        min_width_label = QLabel("العرض الأدنى:")
        min_width_label.setFixedWidth(100)
        min_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.min_width_edit = QLineEdit()
        self.min_width_edit.setText(str(self.config.get('min_width', 370)))
        self.min_width_edit.setPlaceholderText("370")
        self.min_width_edit.setFixedWidth(120)
        self.min_width_edit.setAlignment(Qt.AlignCenter)

        # العرض الأقصى
        max_width_label = QLabel("العرض الأقصى:")
        max_width_label.setFixedWidth(100)
        max_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.max_width_edit = QLineEdit()
        self.max_width_edit.setText(str(self.config.get('max_width', 400)))
        self.max_width_edit.setPlaceholderText("400")
        self.max_width_edit.setFixedWidth(120)
        self.max_width_edit.setAlignment(Qt.AlignCenter)

        # هامش التسامح
        tolerance_label = QLabel("هامش التسامح:")
        tolerance_label.setFixedWidth(100)
        tolerance_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tolerance_edit = QLineEdit()
        self.tolerance_edit.setText(str(self.config.get('tolerance_length', 100)))
        self.tolerance_edit.setPlaceholderText("100")
        self.tolerance_edit.setFixedWidth(120)
        self.tolerance_edit.setAlignment(Qt.AlignCenter)

        # إضافة العناصر للتخطيط بالترتيب
        main_settings_layout.addWidget(self.tolerance_edit)
        main_settings_layout.addWidget(tolerance_label)
        main_settings_layout.addWidget(self.max_width_edit)
        main_settings_layout.addWidget(max_width_label)
        main_settings_layout.addWidget(self.min_width_edit)
        main_settings_layout.addWidget(min_width_label)
        
        settings_layout.addLayout(main_settings_layout)

        # إضافة QIntValidator للحقول الرقمية
        int_validator = QIntValidator(1, 100000, self)
        self.min_width_edit.setValidator(int_validator)
        self.max_width_edit.setValidator(int_validator)
        self.tolerance_edit.setValidator(QIntValidator(0, 100000, self))

        content_layout.addWidget(settings_section)

        # قسم التحكم والتقدم
        control_section, control_layout = self._create_section_card("🚀 لوحة التحكم")

        # أزرار التحكم الرئيسية
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.run_btn = QPushButton("▶️ بدء المعالجة")
        self.run_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.run_btn.setMinimumHeight(35)
        self.run_btn.clicked.connect(self.run_grouping)
        buttons_layout.addWidget(self.run_btn)

        # زر إلغاء العملية
        self.cancel_btn = QPushButton("⏹️ إلغاء")
        self.cancel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.cancel_btn.setEnabled(False)  # معطل في البداية
        buttons_layout.addWidget(self.cancel_btn)

        # شريط التقدم
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

        # قسم السجل والنتائج
        results_section, results_layout = self._create_section_card("📊 النتائج والسجل")
        results_layout.setSpacing(25)  # زيادة المسافات بين العناصر

        # منطقة السجل
        log_label = QLabel("📝 سجل النشاطات:")
        log_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_layout.addWidget(log_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(550)
        results_layout.addWidget(self.log)

        # جدول النتائج
        table_label = QLabel("📋 ملخص المجموعات:")
        table_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_layout.addWidget(table_label)

        self.summary_table = QTableWidget(0, 4)
        self.summary_table.setHorizontalHeaderLabels(["رقم المجموعة", "عدد الأنواع", "العرض الإجمالي", "الطول المرجعي"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.summary_table.setMinimumHeight(300)  # حد أدنى للارتفاع لعرض أفضل
        results_layout.addWidget(self.summary_table)

        # زر فتح ملف Excel
        open_excel_layout = QHBoxLayout()
        open_excel_layout.addStretch()

        self.open_excel_btn = QPushButton("📊 فتح ملف Excel")
        self.open_excel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.open_excel_btn.setMinimumHeight(35)
        self.open_excel_btn.setMinimumWidth(150)
        self.open_excel_btn.clicked.connect(self.open_excel_file)
        self.open_excel_btn.setVisible(False)  # مخفي في البداية
        open_excel_layout.addWidget(self.open_excel_btn)

        open_excel_layout.addStretch()
        results_layout.addLayout(open_excel_layout)

        content_layout.addWidget(results_section)

        # تعيين التخطيط للويدجيت الداخلي
        content_widget.setLayout(content_layout)

        # تعيين الويدجيت الداخلي كمحتوى لمنطقة التمرير
        scroll_area.setWidget(content_widget)

        # تعيين منطقة التمرير كتخطيط رئيسي للنافذة
        main_window_layout = QVBoxLayout(self)
        main_window_layout.setContentsMargins(0, 0, 0, 0)
        main_window_layout.addWidget(scroll_area)

        self.setLayout(main_window_layout)

        # إضافة الرسوم المتحركة للأزرار
        self.setup_button_animations()
        self.showMaximized()
    def set_background_image(self):
        """تعيين صورة الخلفية للنافذة الرئيسية"""
        try:
            # الحصول على المسار المطلق للصورة
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)  # المشروع الرئيسي
            image_path = os.path.join(project_dir, 'assets', 'images', 'backgrounds', 'background_image_light.png')

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # إنشاء فرشاة للصورة
                    brush = QBrush(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

                    # تعيين الفرشاة كخلفية للوحة الألوان
                    palette = self.palette()
                    palette.setBrush(QPalette.Window, brush)
                    self.setPalette(palette)

                    # تعيين الخلفية لتكون ثابتة أثناء التمرير
                    self.setAutoFillBackground(True)
                    print(f"✅ تم تعيين صورة الخلفية من: {image_path}")
                else:
                    print(f"❌ فشل في تحميل الصورة من: {image_path}")
            else:
                print(f"❌ مسار الصورة غير موجود: {image_path}")
        except Exception as e:
            print(f"❌ خطأ في تعيين صورة الخلفية: {e}")

    def create_window_controls(self):
        """إنشاء شريط أدوات مع أزرار التحكم في النافذة"""
        # شريط الأدوات العلوي
        self.toolbar = QWidget()
        self.toolbar.setFixedHeight(40)
        self.toolbar.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-bottom: 2px solid #007bff;
            }
        """)

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)

        # عنوان التطبيق في الشريط
        title_label = QLabel("🏠 تجميع السجاد - نظام محسن")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")
        toolbar_layout.addWidget(title_label)

        # زر تغيير السمة (الوضع الليلي/النهاري)
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(35, 30)
        self.theme_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: #fff;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a359a;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar_layout.addWidget(self.theme_btn)

        toolbar_layout.addStretch()

        # أزرار التحكم في النافذة
        # زر تصغير
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(30, 25)
        self.minimize_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #000;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.minimize_btn.clicked.connect(self.showMinimized)
        toolbar_layout.addWidget(self.minimize_btn)

        # زر تكبير/استعادة
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 25)
        self.maximize_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #fff;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize_restore)
        toolbar_layout.addWidget(self.maximize_btn)

        # زر إغلاق
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 25)
        self.close_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: #fff;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(self.close_btn)

    def toggle_maximize_restore(self):
        """تبديل بين التكبير والاستعادة"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

    def toggle_theme(self):
        """تبديل بين السمة الداكنة والفاتحة"""
        self.is_dark_theme = not self.is_dark_theme

        if self.is_dark_theme:
            # تطبيق السمة الداكنة
            self.theme_btn.setText("🌙")
            self.apply_dark_theme()
        else:
            # تطبيق السمة الفاتحة
            self.theme_btn.setText("☀️")
            self.apply_light_theme()

        # حفظ الإعداد في ملف التكوين
        self.save_theme_preference()

    def apply_dark_theme(self):
        """تطبيق السمة الداكنة"""
        dark_stylesheet = """
            QWidget {
                background-color: #1A1A1A;
                color: #E0E0E0;
                font-family: 'Segoe UI', 'Roboto', 'Inter', sans-serif;
                font-size: 10pt;
            }

            /* خلفية مع صورة للنافذة الرئيسية */
            QWidget#mainWindow {
                background-image: url(./assets/images/backgrounds/background_image_light.png);
                background-repeat: no-repeat;
                background-position: center center;
                background-attachment: fixed;
                background-color: #1A1A1A;
            }

            /* الأزرار الأساسية */
            QPushButton {
                background-color: #007bff;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 9pt;
                min-height: 35px;
            }

            QPushButton:hover {
                background-color: #0056b3;
                margin-top: -1px;
                border: 2px solid #ffffff;
            }

            QPushButton:pressed {
                background-color: #004085;
                margin-top: 0px;
                border: 2px solid #ffffff;
            }

            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }

            /* مربعات الإدخال */
            QLineEdit {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 10pt;
                selection-background-color: #007bff;
            }

            QLineEdit:focus {
                border-color: #007bff;
            }

            QLineEdit::placeholder {
                color: #888;
            }

            /* منطقة السجل */
            QTextEdit {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border: 2px solid #404040;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }

            /* شريط التقدم */
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                background-color: #2C2C2C;
            }

            QProgressBar::chunk {
                background: linear-gradient(90deg, #007bff, #0056b3);
                border-radius: 4px;
            }

            /* الجداول */
            QTableWidget {
                background-color: #2C2C2C;
                color: #E0E0E0;
                border: 2px solid #404040;
                border-radius: 6px;
                gridline-color: #404040;
                selection-background-color: #007bff;
                selection-color: #FFFFFF;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }

            QTableWidget::item:selected {
                background-color: #007bff;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #363636;
                color: #E0E0E0;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #007bff;
                font-weight: 600;
                font-size: 10pt;
            }

            /* التسميات */
            QLabel {
                color: #E0E0E0;
                font-weight: 500;
            }

            /* الإطارات */
            QFrame {
                background-color: #2C2C2C;
                border: 2px solid #404040;
                border-radius: 8px;
            }

            /* شريط التمرير */
            QScrollBar:vertical {
                background-color: #2C2C2C;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background-color: #2C2C2C;
                border-radius: 6px;
            }

            /* رسائل الخطأ والنجاح */
            QMessageBox {
                background-color: #1A1A1A;
            }

            /* منطقة التمرير */
            QScrollArea {
                border: none;
                background-color: #1A1A1A;
            }

            QScrollArea QWidget {
                background-color: #1A1A1A;
            }
        """
        self.setStyleSheet(dark_stylesheet)

        # تحديث ألوان شريط الأدوات
        self.toolbar.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-bottom: 2px solid #007bff;
            }
        """)

    def apply_light_theme(self):
        """تطبيق السمة الفاتحة"""
        light_stylesheet = """
            QWidget {
                background-color: #FFFFFF;
                color: #333333;
                font-family: 'Segoe UI', 'Roboto', 'Inter', sans-serif;
                font-size: 10pt;
            }

            /* خلفية مع صورة للنافذة الرئيسية */
            QWidget#mainWindow {
                background-image: url(./assets/images/backgrounds/background_image_light.png);
                background-repeat: no-repeat;
                background-position: center center;
                background-attachment: fixed;
                background-color: #FFFFFF;
            }

            /* الأزرار الأساسية */
            QPushButton {
                background-color: #007bff;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 9pt;
                min-height: 35px;
            }

            QPushButton:hover {
                background-color: #0056b3;
                margin-top: -1px;
                border: 2px solid #000000;
            }

            QPushButton:pressed {
                background-color: #004085;
                margin-top: 0px;
                border: 2px solid #000000;
            }

            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }

            /* مربعات الإدخال */
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #CCCCCC;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 10pt;
                selection-background-color: #007bff;
            }

            QLineEdit:focus {
                border-color: #007bff;
            }

            QLineEdit::placeholder {
                color: #888;
            }

            /* منطقة السجل */
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #CCCCCC;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }

            /* شريط التقدم */
            QProgressBar {
                border: 2px solid #CCCCCC;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                background-color: #FFFFFF;
            }

            QProgressBar::chunk {
                background: linear-gradient(90deg, #007bff, #0056b3);
                border-radius: 4px;
            }

            /* الجداول */
            QTableWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #CCCCCC;
                border-radius: 6px;
                gridline-color: #CCCCCC;
                selection-background-color: #007bff;
                selection-color: #FFFFFF;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #CCCCCC;
            }

            QTableWidget::item:selected {
                background-color: #007bff;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #F8F9FA;
                color: #333333;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #007bff;
                font-weight: 600;
                font-size: 10pt;
            }

            /* التسميات */
            QLabel {
                color: #333333;
                font-weight: 500;
            }

            /* الإطارات */
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
            }

            /* شريط التمرير */
            QScrollBar:vertical {
                background-color: #F8F9FA;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #CCCCCC;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #AAAAAA;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background-color: #F8F9FA;
                border-radius: 6px;
            }

            /* رسائل الخطأ والنجاح */
            QMessageBox {
                background-color: #FFFFFF;
            }

            /* منطقة التمرير */
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }

            QScrollArea QWidget {
                background-color: #FFFFFF;
            }
        """
        self.setStyleSheet(light_stylesheet)

        # تحديث ألوان شريط الأدوات
        self.toolbar.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-bottom: 2px solid #007bff;
            }
        """)

    def save_theme_preference(self):
        """حفظ تفضيل السمة في ملف التكوين"""
        try:
            config = self.load_config()
            config['theme'] = 'dark' if self.is_dark_theme else 'light'
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطأ في حفظ تفضيل السمة: {e}")

    def setup_button_animations(self):
        """إعداد الرسوم المتحركة للأزرار للحصول على تأثير انتقال سلس"""
        # رسم متحرك لزر اختيار الملف
        self.input_animation = QPropertyAnimation(self.input_btn, b"geometry")
        self.input_animation.setDuration(300)

        # رسم متحرك لزر حفظ الإخراج
        self.output_animation = QPropertyAnimation(self.output_btn, b"geometry")
        self.output_animation.setDuration(300)

        # رسم متحرك لزر بدء المعالجة
        self.run_animation = QPropertyAnimation(self.run_btn, b"geometry")
        self.run_animation.setDuration(300)

        # رسم متحرك لزر فتح ملف Excel
        self.open_excel_animation = QPropertyAnimation(self.open_excel_btn, b"geometry")
        self.open_excel_animation.setDuration(300)

        # رسم متحرك لزر إلغاء العملية
        self.cancel_animation = QPropertyAnimation(self.cancel_btn, b"geometry")
        self.cancel_animation.setDuration(300)

        # ربط إشارات الماوس بالرسوم المتحركة
        self.input_btn.enterEvent = lambda event: self.animate_button_up(self.input_btn, self.input_animation)
        self.input_btn.leaveEvent = lambda event: self.animate_button_down(self.input_btn, self.input_animation)

        self.output_btn.enterEvent = lambda event: self.animate_button_up(self.output_btn, self.output_animation)
        self.output_btn.leaveEvent = lambda event: self.animate_button_down(self.output_btn, self.output_animation)

        self.run_btn.enterEvent = lambda event: self.animate_button_up(self.run_btn, self.run_animation)
        self.run_btn.leaveEvent = lambda event: self.animate_button_down(self.run_btn, self.run_animation)

        self.cancel_btn.enterEvent = lambda event: self.animate_button_up(self.cancel_btn, self.cancel_animation)
        self.cancel_btn.leaveEvent = lambda event: self.animate_button_down(self.cancel_btn, self.cancel_animation)

        self.open_excel_btn.enterEvent = lambda event: self.animate_button_up(self.open_excel_btn, self.open_excel_animation)
        self.open_excel_btn.leaveEvent = lambda event: self.animate_button_down(self.open_excel_btn, self.open_excel_animation)

    def animate_button_up(self, button, animation):
        """تحريك الزر لأعلى عند دخول الماوس"""
        start_rect = button.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y() - 2, start_rect.width(), start_rect.height())
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.start()

    def animate_button_down(self, button, animation):
        """إعادة الزر لوضعه الطبيعي عند خروج الماوس"""
        start_rect = button.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y() + 2, start_rect.width(), start_rect.height())
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.start()

    def _create_primary_button(self, text, callback):
        """إنشاء زر أساسي بتصميم عصري"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.setMinimumHeight(35)
        btn.clicked.connect(callback)
        return btn

    def _create_section_card(self, title):
        """إنشاء بطاقة قسم مع تصميم حديث"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setLineWidth(2)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin-bottom: 10px;")
        layout.addWidget(title_label)

        return frame, layout

    def generate_output_path(self, input_path):
        """إنشاء مسار ملف الإخراج التلقائي بناءً على ملف الإدخال"""
        if not input_path:
            return ""

        # استخراج المجلد والاسم الكامل
        dir_path = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)

        # فصل الاسم عن اللاحقة
        name_without_ext, _ = os.path.splitext(file_name)

        # إنشاء الاسم الجديد مع _result واللاحقة xlsx
        new_file_name = f"{name_without_ext}_result.xlsx"

        # دمج المسار الكامل
        return os.path.join(dir_path, new_file_name)

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف الاكسل","", 
                                            "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            self.input_edit.setText(path)
            output_path = self.generate_output_path(path)
            self.output_edit.setText(output_path)

    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف الإخراج", "", 
                                            "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            # إضافة امتداد إذا لم يكن موجوداً
            if not path.lower().endswith(('.xlsx', '.xls')):
                path += '.xlsx'  # افتراضي xlsx
            self.output_edit.setText(path)

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                return {}
            return cfg
        except Exception as e:
            # لا ترجع قائمة؛ ارجع قاموس فارغ لتجنب AttributeError عند استخدام .get
            QMessageBox.warning(self, "Config", f"خطأ بتحميل الإعدادات : {e}")
            return {}

    def load_theme_preference(self):
        """تحميل تفضيل السمة من ملف التكوين"""
        try:
            config = self.load_config()
            theme = config.get('theme', 'dark')
            if theme == 'light':
                self.is_dark_theme = False
                self.apply_light_theme()
                if hasattr(self, 'theme_btn'):
                    self.theme_btn.setText("☀️")
            else:
                self.is_dark_theme = True
                self.apply_dark_theme()
                if hasattr(self, 'theme_btn'):
                    self.theme_btn.setText("🌙")
        except Exception as e:
            # في حالة وجود خطأ، استخدم السمة الداكنة كافتراضي
            self.is_dark_theme = True
            self.apply_dark_theme()
            if hasattr(self, 'theme_btn'):
                self.theme_btn.setText("🌙")

    def log_append(self, text):
        self.log.append(text)

    def run_grouping(self):
        # التحقق من عدم وجود عملية قيد التشغيل
        if self.is_running:
            QMessageBox.information(self, "عملية قيد التشغيل",
                                  "هناك عملية معالجة قيد التشغيل حالياً.\nيرجى انتظار انتهائها أو إلغاؤها أولاً.")
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
            tolerance_len = int(self.tolerance_edit.text().strip())

            # Get quantity limits (optional)
            min_quantity = None
            max_quantity = None

            if min_width <= 0 or max_width <= 0:
                QMessageBox.warning(self, "قيم خاطئة", "العرض الأدنى والأقصى يجب أن يكونا أكبر من 0")
                return
            if min_width >= max_width:
                QMessageBox.warning(self, "قيم خاطئة", "العرض الأدنى يجب أن يكون أقل من العرض الأقصى")
                return
            if tolerance_len < 0:
                QMessageBox.warning(self, "قيم خاطئة", "هامش التسامح يجب أن يكون صفراً أو رقماً موجباً")
                return
        except ValueError:
            QMessageBox.warning(self, "قيم خاطئة", "يرجى إدخال أرقام صحيحة للعرض الأدنى والأقصى وهامش التسامح")
            return

       # read config validation
        cfg = self.config
        ok, err = validate_config(min_width, max_width, tolerance_len)
        if not ok:
            QMessageBox.warning(self, "إعدادات خاطئة", err)
            return

        # إعداد شريط التقدم والحالة
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔄 بدء المعالجة...")
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)  # تفعيل زر الإلغاء
        self.open_excel_btn.setVisible(False)  # إخفاء زر فتح Excel
        self.is_running = True  # تعيين حالة التشغيل

        # تشغيل المعالجة في ثريد منفصل
        self.worker = GroupingWorker(input_path, output_path, min_width, max_width, tolerance_len, cfg)
        self.worker.signals.progress.connect(lambda v: self.progress_bar.setValue(v))
        self.worker.signals.log.connect(self.log_append)
        self.worker.signals.data_ready.connect(self.update_summary_table)
        self.worker.signals.finished.connect(self.on_worker_finished)
        self.worker.signals.error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_finished(self):
        """معالجة انتهاء الـ worker بنجاح"""
        self.status_label.setText("✅ اكتملت المعالجة بنجاح!")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)  # تعطيل زر الإلغاء
        self.open_excel_btn.setVisible(True)  # إظهار زر فتح Excel
        self.is_running = False  # إعادة تعيين حالة التشغيل
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

    def on_worker_error(self, tb_str):
        """معالجة خطأ الـ worker"""
        self.log_append("❌ خطأ في المعالجة:\n" + tb_str)
        self.status_label.setText("❌ حدث خطأ في المعالجة")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)  # تعطيل زر الإلغاء
        self.progress_bar.setVisible(False)
        self.is_running = False  # إعادة تعيين حالة التشغيل

    def update_summary_table(self, groups, remaining, stats):
        """تحديث جدول النتائج بالبيانات المُعالجة"""
        try:
            # مسح الجدول الحالي
            self.summary_table.setRowCount(0)

            # إضافة المجموعات
            for g in groups:
                row = self.summary_table.rowCount()
                self.summary_table.insertRow(row)
                self.summary_table.setItem(row, 0, QTableWidgetItem(f"مجموعة {g.id}"))
                self.summary_table.setItem(row, 1, QTableWidgetItem(str(len(g.items))))
                self.summary_table.setItem(row, 2, QTableWidgetItem(str(g.total_width())))
                self.summary_table.setItem(row, 3, QTableWidgetItem(str(g.ref_length())))

            # إضافة السجاد المتبقي إذا كان موجوداً
            if remaining:
                self.log_append(f"📦 السجاد المتبقي ({len(remaining)} أنواع):")
                for carpet in remaining:
                    self.log_append(f"  • معرف {carpet.id}: {carpet.width}×{carpet.length} (كمية متبقية: {carpet.qty})")
            else:
                self.log_append("🎉 لا يوجد سجاد متبقي - تم استخدام جميع القطع!")

            # إضافة معلومات الإحصائيات
            if stats:
                utilization = stats.get('utilization_percentage', 0)
                self.log_append(f"📊 إحصائيات الكميات: استغلال {utilization:.2f}% من الكمية الإجمالية")

        except Exception as e:
            self.log_append(f"❌ خطأ في تحديث الجدول: {str(e)}")

    def cancel_operation(self):
        """إلغاء العملية الحالية"""
        if not self.is_running or not hasattr(self, 'worker'):
            return

        try:
            # إيقاف الـ worker
            if hasattr(self.worker, '_is_interrupted'):
                self.worker._is_interrupted = True

            # تحديث واجهة المستخدم
            self.status_label.setText("⏹️ تم إلغاء العملية")
            self.run_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.is_running = False

            # تسجيل الإلغاء في السجل
            self.log_append("⏹️ تم إلغاء العملية بواسطة المستخدم")

            # إخفاء زر فتح Excel إذا كان مرئياً
            self.open_excel_btn.setVisible(False)

        except Exception as e:
            self.log_append(f"❌ خطأ أثناء إلغاء العملية: {str(e)}")

    def open_excel_file(self):
        """فتح ملف Excel المُنشأ"""
        try:
            import subprocess
            import platform

            output_path = self.output_edit.text().strip()
            if not output_path:
                QMessageBox.warning(self, "مسار غير محدد", "لم يتم تحديد مسار ملف الإخراج بعد.")
                return

            if not os.path.exists(output_path):
                QMessageBox.warning(self, "ملف غير موجود", f"لم يتم العثور على ملف الإخراج في المسار:\n{output_path}")
                return

            # فتح الملف حسب نظام التشغيل
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_path])
            else:  # Linux وغيرها
                subprocess.run(["xdg-open", output_path])

            self.log_append(f"✅ تم فتح ملف Excel: {output_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ في فتح الملف",
                               f"حدث خطأ أثناء محاولة فتح ملف Excel:\n{str(e)}")
            self.log_append(f"❌ خطأ في فتح ملف Excel: {str(e)}")