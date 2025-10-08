import json
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
                               QLabel, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox, QTableWidget, 
                               QTableWidgetItem, QComboBox, QProgressBar, QGroupBox, QGridLayout,
                               QFrame, QSplitter, QTabWidget, QSpinBox, QCheckBox, QStatusBar)

from PySide6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from data_io.excel_io import read_input_excel, write_output_excel, exhaustively_regroup
from data_io.pdf_report import SimplePDFReport
# from core.grouping import group_carpets_greedy, generate_groups_from_remaining
from core.grouping import group_carpets_greedy
from core.validation import validate_config, validate_carpets, validate_file_path
from core.logger import logger
from data_io.advanced_export import exporter
from ui.settings_dialog import AdvancedSettingsDialog

class RectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()
        self.setWindowTitle("🧩 RectPack - أداة تجميع السجاد المتقدمة")
        self.resize(1200, 800)
        self.config_path = config_path
        self.config = self.load_config()
        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit, QSpinBox {
                border: 2px solid #e1e1e1;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #0078d4;
            }
            QTextEdit {
                border: 2px solid #e1e1e1;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QProgressBar {
                border: 2px solid #e1e1e1;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # File selection group
        file_group = QGroupBox("📁 اختيار الملفات")
        file_layout = QGridLayout(file_group)
        
        # Input file
        file_layout.addWidget(QLabel("ملف الإدخال:"), 0, 0)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("اختر ملف Excel للإدخال...")
        file_layout.addWidget(self.input_edit, 0, 1)
        
        btn_browse = QPushButton("📂 استعراض")
        btn_browse.clicked.connect(self.browse_input)
        file_layout.addWidget(btn_browse, 0, 2)
        
        # Output file
        file_layout.addWidget(QLabel("ملف الإخراج:"), 1, 0)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("اختر مكان حفظ النتائج...")
        file_layout.addWidget(self.output_edit, 1, 1)
        
        btn_out = QPushButton("💾 حفظ باسم")
        btn_out.clicked.connect(self.browes_output)
        file_layout.addWidget(btn_out, 1, 2)
        
        left_layout.addWidget(file_group)
        
        # Parameters group
        params_group = QGroupBox("⚙️ معاملات التجميع")
        params_layout = QGridLayout(params_group)
        
        # Width range
        params_layout.addWidget(QLabel("العرض الأدنى:"), 0, 0)
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setRange(1, 9999)
        self.min_width_spin.setValue(self.config.get('min_width', 370))
        self.min_width_spin.setSuffix(" سم")
        params_layout.addWidget(self.min_width_spin, 0, 1)
        
        params_layout.addWidget(QLabel("العرض الأقصى:"), 1, 0)
        self.max_width_spin = QSpinBox()
        self.max_width_spin.setRange(1, 9999)
        self.max_width_spin.setValue(self.config.get('max_width', 400))
        self.max_width_spin.setSuffix(" سم")
        params_layout.addWidget(self.max_width_spin, 1, 1)
        
        params_layout.addWidget(QLabel("هامش التسامح:"), 2, 0)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 9999)
        self.tolerance_spin.setValue(self.config.get('tolerance_length', 100))
        self.tolerance_spin.setSuffix(" سم")
        params_layout.addWidget(self.tolerance_spin, 2, 1)
        
        # Advanced options
        self.start_largest_check = QCheckBox("البدء بالأكبر عرضاً")
        self.start_largest_check.setChecked(self.config.get('start_with_largest', True))
        params_layout.addWidget(self.start_largest_check, 3, 0, 1, 2)
        
        self.allow_split_check = QCheckBox("السماح بتقسيم الصفوف")
        self.allow_split_check.setChecked(self.config.get('allow_split_rows', True))
        params_layout.addWidget(self.allow_split_check, 4, 0, 1, 2)
        
        left_layout.addWidget(params_group)
        
        # Control buttons
        control_group = QGroupBox("🎮 التحكم")
        control_layout = QVBoxLayout(control_group)
        
        self.run_btn = QPushButton("🚀 تشغيل التجميع")
        self.run_btn.clicked.connect(self.run_grouping)
        self.run_btn.setMinimumHeight(40)
        control_layout.addWidget(self.run_btn)
        
        # Settings and export buttons
        buttons_layout = QHBoxLayout()
        
        self.settings_btn = QPushButton("⚙️ إعدادات")
        self.settings_btn.clicked.connect(self.show_settings)
        buttons_layout.addWidget(self.settings_btn)
        
        self.export_btn = QPushButton("📤 تصدير متقدم")
        self.export_btn.clicked.connect(self.show_export_options)
        self.export_btn.setEnabled(False)  # Enabled after processing
        buttons_layout.addWidget(self.export_btn)
        
        control_layout.addLayout(buttons_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("جاهز للعمل")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        control_layout.addWidget(self.status_label)
        
        left_layout.addWidget(control_group)
        left_layout.addStretch()
        
        # Right panel with tabs
        right_panel = QTabWidget()
        
        # Log tab
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("📋 سجل العمليات:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log)
        right_panel.addTab(log_widget, "📋 السجل")
        
        # Results tab
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.addWidget(QLabel("📊 ملخص النتائج:"))
        self.summary_table = QTableWidget(0, 4)
        self.summary_table.setHorizontalHeaderLabels(["رقم المجموعة", "عدد الأنواع", "العرض الإجمالي", "الطول المرجعي"])
        self.summary_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.summary_table)
        right_panel.addTab(results_widget, "📊 النتائج")
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Store results for export
        self.last_groups = []
        self.last_remaining = []
        self.last_config = {}

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            return cfg
        except Exception as e:
            QMessageBox.warning(self, "Config", f"خطأ بتحميل الإعدادات : {e}")
            return []
        
    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف الاكسل","", 
                                             "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            self.input_edit.setText(path)

    def browes_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف الإخراج", "", 
                                             "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            # إضافة امتداد إذا لم يكن موجوداً
            if not path.lower().endswith(('.xlsx', '.xls')):
                path += '.xlsx'  # افتراضي xlsx
            self.output_edit.setText(path)

    def log_append(self, text):
        self.log.append(text)

    def run_grouping(self):
        input_path = self.input_edit.text().strip()
        output_path = self.output_edit.text().strip()
        
        if not input_path or not output_path:
            QMessageBox.warning(self, "خطأ في المدخلات", "يرجى اختيار ملف الإدخال ومسار الإخراج.")
            return
        
        # Validate input file
        valid_input, input_error = validate_file_path(input_path, check_exists=True)
        if not valid_input:
            QMessageBox.warning(self, "خطأ في ملف الإدخال", input_error)
            return
        
        # Validate output file
        valid_output, output_error = validate_file_path(output_path, check_exists=False)
        if not valid_output:
            QMessageBox.warning(self, "خطأ في ملف الإخراج", output_error)
            return
       
        # Get values from spinboxes
        min_width = self.min_width_spin.value()
        max_width = self.max_width_spin.value()
        tolerance_len = self.tolerance_spin.value()
        
        # Validate parameters
        if min_width >= max_width:
            QMessageBox.warning(self, "خطأ في القيم", "العرض الأدنى يجب أن يكون أقل من العرض الأقصى")
            return
        
        # Show progress and disable button
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("جاري المعالجة...")
        
        try:
            logger.log_operation_start("تجميع السجاد", f"الملف: {os.path.basename(input_path)}")
            
            # read config validation
            cfg = self.config
            ok, err = validate_config(min_width, max_width, tolerance_len)
            if not ok:
                logger.error(f"خطأ في التحقق من الإعدادات: {err}")
                QMessageBox.warning(self, "خطأ في الإعدادات", err)
                return 
            
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(10)
            self.status_label.setText("قراءة الملف...")
            self.log_append(f"📖 قراءة الملف: {input_path}")
            logger.log_file_operation("قراءة الملف", input_path)
            
            carpets = read_input_excel(input_path)
            self.progress_bar.setValue(20)
            logger.info(f"تم قراءة {len(carpets)} نوع من السجاد")
            
            # احتفظ بنسخة من الأصليات قبل أي تعديل
            originals_copy = [
                # نفس الهوية والأبعاد مع الكمية الأصلية
                type(c)(c.id, c.width, c.length, c.qty) if hasattr(c, 'id') else c
                for c in carpets
            ]
            
            self.status_label.setText("التحقق من صحة البيانات...")
            errs = validate_carpets(carpets)
            if errs:
                self.log_append("⚠️ تحذيرات في البيانات:")
                for e in errs:
                    self.log_append(" - " + e)
            
            self.progress_bar.setValue(30)
            self.status_label.setText("تشغيل خوارزمية التجميع...")
            self.log_append(f"🔄 بدء التجميع مع المعاملات: العرض ({min_width}-{max_width})، التسامح: {tolerance_len}")
            
            groups, remaining = group_carpets_greedy(
                carpets,
                min_width=min_width,
                max_width=max_width,
                tolerance_length=tolerance_len,
                start_with_largest=self.start_largest_check.isChecked(),
                allow_split_rows=self.allow_split_check.isChecked()
            )
            
            self.progress_bar.setValue(60)
            
            self.log_append(f"✅ تم تشكيل {len(groups)} مجموعة. المتبقي: {len(remaining)} أنواع (مع كميات).")

            # محاولة إعادة تجميع البواقي إلى مجموعات إضافية مع السماح بالتكرار داخل المجموعة
            self.status_label.setText("إعادة تجميع البواقي...")
            self.progress_bar.setValue(70)
            
            rem_groups, rem_final_remaining = exhaustively_regroup(
                remaining,
                min_width=min_width,
                max_width=max_width,
                tolerance_length=tolerance_len,
                start_group_id=max([g.id for g in groups] + [0]) + 1,
                max_rounds=100
            )
            self.log_append(f"♻️ تم تشكيل {len(rem_groups)} مجموعة إضافية من البواقي. تبقّى بعد ذلك: {len(rem_final_remaining)} أنواع.")

            # write excel
            self.status_label.setText("حفظ ملف Excel...")
            self.progress_bar.setValue(80)
            
            try:
                # نمرر مجموعات البواقي لتُدمج في جداول المجموعات، ونكتب البواقي النهائية بعد إعادة التجميع
                write_output_excel(
                    output_path,
                    groups,
                    rem_final_remaining,
                    remainder_groups=rem_groups,
                    min_width=min_width,
                    max_width=max_width,
                    tolerance_length=tolerance_len,
                    originals=originals_copy
                )
                self.log_append(f"💾 تم حفظ الملف: {output_path}")
            except Exception as e:
                self.log_append(f"❌ خطأ بحفظ Excel: {e}")
                QMessageBox.critical(self, "خطأ", f"فشل في حفظ ملف Excel:\n{e}")

            # create pdf
            self.status_label.setText("إنشاء تقرير PDF...")
            self.progress_bar.setValue(90)
            
            try:
                pdf_path = os.path.splitext(output_path)[0] + "_report.pdf"
                pdf = SimplePDFReport(title="تقرير مجموعات السجاد")
                pdf.groups_to_pdf(groups, pdf_path)
                self.log_append(f"📄 تم إنشاء تقرير PDF: {pdf_path}")
            except Exception as e:
                self.log_append("❌ خطأ عند إنشاء PDF: " + str(e))

            # update summary table
            self.status_label.setText("تحديث النتائج...")
            self.summary_table.setRowCount(0)
            
            # إضافة المجموعات
            all_groups = groups + rem_groups
            for g in all_groups:
                row = self.summary_table.rowCount()
                self.summary_table.insertRow(row)
                self.summary_table.setItem(row, 0, QTableWidgetItem(f"المجموعة_{g.id}"))
                self.summary_table.setItem(row, 1, QTableWidgetItem(str(len(g.items))))
                self.summary_table.setItem(row, 2, QTableWidgetItem(str(g.total_width())))
                self.summary_table.setItem(row, 3, QTableWidgetItem(str(g.ref_length())))
            
            # إضافة السجاد المتبقي
            if rem_final_remaining:
                self.log_append(f"📋 السجاد المتبقي ({len(rem_final_remaining)} أنواع):")
                for carpet in rem_final_remaining:
                    self.log_append(f"  - معرف {carpet.id}: {carpet.width}x{carpet.length} (كمية متبقية: {carpet.qty})")
            else:
                self.log_append("🎉 لا يوجد سجاد متبقي - تم استخدام جميع القطع!")
            
            # Show completion
            self.progress_bar.setValue(100)
            self.status_label.setText(f"✅ اكتمل! تم إنشاء {len(all_groups)} مجموعة")
            
            # Store results for export
            self.last_groups = all_groups
            self.last_remaining = rem_final_remaining
            self.last_config = {
                'min_width': min_width,
                'max_width': max_width,
                'tolerance_length': tolerance_len,
                'start_with_largest': self.start_largest_check.isChecked(),
                'allow_split_rows': self.allow_split_check.isChecked(),
                'input_file': os.path.basename(input_path),
                'output_file': os.path.basename(output_path),
                'processing_time': self.export_timestamp.isoformat() if hasattr(self, 'export_timestamp') else datetime.now().isoformat()
            }
            
            # Enable export button
            self.export_btn.setEnabled(True)
            
            # Show success message
            QMessageBox.information(self, "اكتمل بنجاح", 
                                  f"تم الانتهاء من التجميع بنجاح!\n\n"
                                  f"📊 عدد المجموعات: {len(all_groups)}\n"
                                  f"📋 العناصر المتبقية: {len(rem_final_remaining)}\n"
                                  f"💾 تم حفظ النتائج في: {output_path}\n\n"
                                  f"يمكنك الآن استخدام 'تصدير متقدم' للحصول على تقارير إضافية.")
            
        except Exception as e:
            self.log_append(f"❌ خطأ عام: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء المعالجة:\n{e}")
        
        finally:
            # Reset UI state
            self.run_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            if not hasattr(self, '_processing_completed'):
                self.status_label.setText("جاهز للعمل")
    
    def show_settings(self):
        """Show advanced settings dialog."""
        try:
            # Get current configuration
            current_config = {
                'min_width': self.min_width_spin.value(),
                'max_width': self.max_width_spin.value(),
                'tolerance_length': self.tolerance_spin.value(),
                'start_with_largest': self.start_largest_check.isChecked(),
                'allow_split_rows': self.allow_split_check.isChecked(),
            }
            current_config.update(self.config)
            
            # Show settings dialog
            dialog = AdvancedSettingsDialog(current_config, self)
            dialog.settings_changed.connect(self.apply_settings)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"خطأ في عرض نافذة الإعدادات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض نافذة الإعدادات:\n{e}")
    
    def apply_settings(self, settings: dict):
        """Apply settings from the advanced settings dialog."""
        try:
            # Update UI controls
            self.min_width_spin.setValue(settings.get('min_width', 370))
            self.max_width_spin.setValue(settings.get('max_width', 400))
            self.tolerance_spin.setValue(settings.get('tolerance_length', 100))
            self.start_largest_check.setChecked(settings.get('start_with_largest', True))
            self.allow_split_check.setChecked(settings.get('allow_split_rows', True))
            
            # Update internal config
            self.config.update(settings)
            
            # Save to config file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.log_append("✅ تم تطبيق الإعدادات الجديدة")
            logger.info("تم تطبيق الإعدادات المتقدمة")
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق الإعدادات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تطبيق الإعدادات:\n{e}")
    
    def show_export_options(self):
        """Show export options dialog."""
        if not self.last_groups:
            QMessageBox.information(self, "لا توجد نتائج", 
                                  "يرجى تشغيل التجميع أولاً للحصول على نتائج للتصدير.")
            return
        
        try:
            # Create export options dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("📤 خيارات التصدير المتقدم")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Export format selection
            format_group = QGroupBox("اختر صيغ التصدير:")
            format_layout = QVBoxLayout(format_group)
            
            csv_check = QCheckBox("CSV - ملف قيم مفصولة بفواصل")
            json_check = QCheckBox("JSON - ملف بيانات منظم")
            detailed_check = QCheckBox("تقرير نصي مفصل")
            
            format_layout.addWidget(csv_check)
            format_layout.addWidget(json_check)
            format_layout.addWidget(detailed_check)
            
            layout.addWidget(format_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            cancel_btn = QPushButton("إلغاء")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            export_btn = QPushButton("تصدير")
            export_btn.clicked.connect(lambda: self.perform_advanced_export(
                dialog, csv_check.isChecked(), json_check.isChecked(), detailed_check.isChecked()))
            button_layout.addWidget(export_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"خطأ في عرض خيارات التصدير: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض خيارات التصدير:\n{e}")
    
    def perform_advanced_export(self, dialog, export_csv, export_json, export_detailed):
        """Perform advanced export based on selected options."""
        if not any([export_csv, export_json, export_detailed]):
            QMessageBox.warning(dialog, "لم يتم اختيار صيغة", "يرجى اختيار صيغة واحدة على الأقل للتصدير.")
            return
        
        try:
            # Get base output path
            base_path = self.output_edit.text().strip()
            if not base_path:
                QMessageBox.warning(dialog, "مسار غير محدد", "يرجى تحديد مسار الإخراج أولاً.")
                return
            
            base_name = os.path.splitext(base_path)[0]
            exported_files = []
            
            # Export CSV
            if export_csv:
                csv_path = f"{base_name}_detailed.csv"
                if exporter.export_to_csv(self.last_groups, self.last_remaining, csv_path, self.last_config):
                    exported_files.append(csv_path)
                    self.log_append(f"📄 تم تصدير CSV: {csv_path}")
            
            # Export JSON
            if export_json:
                json_path = f"{base_name}_data.json"
                if exporter.export_to_json(self.last_groups, self.last_remaining, json_path, self.last_config):
                    exported_files.append(json_path)
                    self.log_append(f"📄 تم تصدير JSON: {json_path}")
            
            # Export detailed report
            if export_detailed:
                txt_path = f"{base_name}_detailed_report.txt"
                if exporter.export_detailed_report(self.last_groups, self.last_remaining, txt_path, self.last_config):
                    exported_files.append(txt_path)
                    self.log_append(f"📄 تم تصدير التقرير المفصل: {txt_path}")
            
            if exported_files:
                QMessageBox.information(dialog, "تم التصدير بنجاح", 
                                      f"تم تصدير {len(exported_files)} ملف بنجاح:\n\n" + 
                                      "\n".join([os.path.basename(f) for f in exported_files]))
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "فشل التصدير", "فشل في تصدير الملفات المحددة.")
            
        except Exception as e:
            logger.error(f"خطأ في التصدير المتقدم: {e}")
            QMessageBox.critical(dialog, "خطأ", f"فشل في التصدير:\n{e}")