"""
Advanced settings dialog for RectPack application.
"""

import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QWidget, QLabel, QSpinBox, QCheckBox, QPushButton,
                               QGroupBox, QGridLayout, QComboBox, QLineEdit,
                               QTextEdit, QMessageBox, QFileDialog, QSlider)
from PySide6.QtCore import Qt, pyqtSignal
from PySide6.QtGui import QFont
from core.logger import logger


class AdvancedSettingsDialog(QDialog):
    """Advanced settings dialog with multiple configuration options."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.current_config = current_config.copy()
        self.setWindowTitle("⚙️ الإعدادات المتقدمة - RectPack")
        self.setModal(True)
        self.resize(600, 500)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #e1e1e1;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Algorithm settings tab
        self.algorithm_tab = self.create_algorithm_tab()
        self.tab_widget.addTab(self.algorithm_tab, "🔧 الخوارزمية")
        
        # Performance settings tab
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "⚡ الأداء")
        
        # Export settings tab
        self.export_tab = self.create_export_tab()
        self.tab_widget.addTab(self.export_tab, "📤 التصدير")
        
        # Advanced settings tab
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "🔬 متقدم")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("🔄 إعادة تعيين")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("💾 حفظ")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def create_algorithm_tab(self) -> QWidget:
        """Create algorithm settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Basic parameters group
        basic_group = QGroupBox("المعاملات الأساسية")
        basic_layout = QGridLayout(basic_group)
        
        # Width range
        basic_layout.addWidget(QLabel("العرض الأدنى:"), 0, 0)
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setRange(1, 9999)
        self.min_width_spin.setSuffix(" سم")
        basic_layout.addWidget(self.min_width_spin, 0, 1)
        
        basic_layout.addWidget(QLabel("العرض الأقصى:"), 1, 0)
        self.max_width_spin = QSpinBox()
        self.max_width_spin.setRange(1, 9999)
        self.max_width_spin.setSuffix(" سم")
        basic_layout.addWidget(self.max_width_spin, 1, 1)
        
        basic_layout.addWidget(QLabel("هامش التسامح:"), 2, 0)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 9999)
        self.tolerance_spin.setSuffix(" سم")
        basic_layout.addWidget(self.tolerance_spin, 2, 1)
        
        layout.addWidget(basic_group)
        
        # Algorithm behavior group
        behavior_group = QGroupBox("سلوك الخوارزمية")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.start_largest_check = QCheckBox("البدء بالأكبر عرضاً")
        behavior_layout.addWidget(self.start_largest_check)
        
        self.allow_split_check = QCheckBox("السماح بتقسيم الصفوف")
        behavior_layout.addWidget(self.allow_split_check)
        
        self.optimize_area_check = QCheckBox("تحسين استخدام المساحة")
        behavior_layout.addWidget(self.optimize_area_check)
        
        layout.addWidget(behavior_group)
        
        # Area constraints group
        area_group = QGroupBox("قيود المساحة (اختياري)")
        area_layout = QGridLayout(area_group)
        
        area_layout.addWidget(QLabel("الحد الأدنى للمساحة:"), 0, 0)
        self.min_area_spin = QSpinBox()
        self.min_area_spin.setRange(0, 999999999)
        self.min_area_spin.setSuffix(" سم²")
        self.min_area_spin.setSpecialValueText("غير محدد")
        area_layout.addWidget(self.min_area_spin, 0, 1)
        
        area_layout.addWidget(QLabel("الحد الأقصى للمساحة:"), 1, 0)
        self.max_area_spin = QSpinBox()
        self.max_area_spin.setRange(0, 999999999)
        self.max_area_spin.setSuffix(" سم²")
        self.max_area_spin.setSpecialValueText("غير محدد")
        area_layout.addWidget(self.max_area_spin, 1, 1)
        
        layout.addWidget(area_group)
        layout.addStretch()
        
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """Create performance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance group
        perf_group = QGroupBox("إعدادات الأداء")
        perf_layout = QGridLayout(perf_group)
        
        perf_layout.addWidget(QLabel("الحد الأقصى للتكرارات:"), 0, 0)
        self.max_iterations_spin = QSpinBox()
        self.max_iterations_spin.setRange(100, 100000)
        self.max_iterations_spin.setValue(10000)
        perf_layout.addWidget(self.max_iterations_spin, 0, 1)
        
        perf_layout.addWidget(QLabel("فترة تقرير التقدم:"), 1, 0)
        self.progress_interval_spin = QSpinBox()
        self.progress_interval_spin.setRange(10, 1000)
        self.progress_interval_spin.setValue(100)
        perf_layout.addWidget(self.progress_interval_spin, 1, 1)
        
        perf_layout.addWidget(QLabel("عدد جولات إعادة التجميع:"), 2, 0)
        self.regroup_rounds_spin = QSpinBox()
        self.regroup_rounds_spin.setRange(1, 1000)
        self.regroup_rounds_spin.setValue(100)
        perf_layout.addWidget(self.regroup_rounds_spin, 2, 1)
        
        layout.addWidget(perf_group)
        
        # Memory group
        memory_group = QGroupBox("إدارة الذاكرة")
        memory_layout = QVBoxLayout(memory_group)
        
        self.enable_caching_check = QCheckBox("تفعيل التخزين المؤقت")
        self.enable_caching_check.setChecked(True)
        memory_layout.addWidget(self.enable_caching_check)
        
        self.cleanup_temp_check = QCheckBox("تنظيف الملفات المؤقتة تلقائياً")
        self.cleanup_temp_check.setChecked(True)
        memory_layout.addWidget(self.cleanup_temp_check)
        
        layout.addWidget(memory_group)
        layout.addStretch()
        
        return widget
    
    def create_export_tab(self) -> QWidget:
        """Create export settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Export formats group
        formats_group = QGroupBox("صيغ التصدير")
        formats_layout = QVBoxLayout(formats_group)
        
        self.export_excel_check = QCheckBox("Excel (.xlsx)")
        self.export_excel_check.setChecked(True)
        self.export_excel_check.setEnabled(False)  # Always enabled
        formats_layout.addWidget(self.export_excel_check)
        
        self.export_pdf_check = QCheckBox("PDF Report")
        self.export_pdf_check.setChecked(True)
        formats_layout.addWidget(self.export_pdf_check)
        
        self.export_csv_check = QCheckBox("CSV")
        formats_layout.addWidget(self.export_csv_check)
        
        self.export_json_check = QCheckBox("JSON")
        formats_layout.addWidget(self.export_json_check)
        
        self.export_detailed_check = QCheckBox("تقرير نصي مفصل")
        formats_layout.addWidget(self.export_detailed_check)
        
        layout.addWidget(formats_group)
        
        # File naming group
        naming_group = QGroupBox("تسمية الملفات")
        naming_layout = QGridLayout(naming_group)
        
        naming_layout.addWidget(QLabel("بادئة اسم الملف:"), 0, 0)
        self.file_prefix_edit = QLineEdit()
        self.file_prefix_edit.setPlaceholderText("rectpack_results")
        naming_layout.addWidget(self.file_prefix_edit, 0, 1)
        
        self.include_timestamp_check = QCheckBox("إضافة الطابع الزمني")
        self.include_timestamp_check.setChecked(True)
        naming_layout.addWidget(self.include_timestamp_check, 1, 0, 1, 2)
        
        layout.addWidget(naming_group)
        layout.addStretch()
        
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logging group
        logging_group = QGroupBox("السجلات والتتبع")
        logging_layout = QVBoxLayout(logging_group)
        
        self.enable_logging_check = QCheckBox("تفعيل نظام السجلات")
        self.enable_logging_check.setChecked(True)
        logging_layout.addWidget(self.enable_logging_check)
        
        self.verbose_logging_check = QCheckBox("سجلات مفصلة")
        logging_layout.addWidget(self.verbose_logging_check)
        
        self.log_performance_check = QCheckBox("تسجيل مقاييس الأداء")
        self.log_performance_check.setChecked(True)
        logging_layout.addWidget(self.log_performance_check)
        
        layout.addWidget(logging_group)
        
        # Validation group
        validation_group = QGroupBox("التحقق من صحة البيانات")
        validation_layout = QVBoxLayout(validation_group)
        
        self.strict_validation_check = QCheckBox("تحقق صارم من البيانات")
        self.strict_validation_check.setChecked(True)
        validation_layout.addWidget(self.strict_validation_check)
        
        self.warn_duplicates_check = QCheckBox("تحذير من المعرفات المكررة")
        self.warn_duplicates_check.setChecked(True)
        validation_layout.addWidget(self.warn_duplicates_check)
        
        self.check_file_size_check = QCheckBox("فحص حجم الملفات")
        self.check_file_size_check.setChecked(True)
        validation_layout.addWidget(self.check_file_size_check)
        
        layout.addWidget(validation_group)
        
        # Custom config group
        custom_group = QGroupBox("إعدادات مخصصة (JSON)")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_config_edit = QTextEdit()
        self.custom_config_edit.setMaximumHeight(100)
        self.custom_config_edit.setPlaceholderText('{"custom_setting": "value"}')
        custom_layout.addWidget(self.custom_config_edit)
        
        layout.addWidget(custom_group)
        layout.addStretch()
        
        return widget
    
    def load_current_settings(self):
        """Load current settings into the dialog."""
        # Algorithm settings
        self.min_width_spin.setValue(self.current_config.get('min_width', 370))
        self.max_width_spin.setValue(self.current_config.get('max_width', 400))
        self.tolerance_spin.setValue(self.current_config.get('tolerance_length', 100))
        
        self.start_largest_check.setChecked(self.current_config.get('start_with_largest', True))
        self.allow_split_check.setChecked(self.current_config.get('allow_split_rows', True))
        self.optimize_area_check.setChecked(self.current_config.get('optimize_area', False))
        
        # Area constraints
        min_area = self.current_config.get('min_total_area')
        max_area = self.current_config.get('max_total_area')
        self.min_area_spin.setValue(min_area if min_area is not None else 0)
        self.max_area_spin.setValue(max_area if max_area is not None else 0)
        
        # Performance settings
        self.max_iterations_spin.setValue(self.current_config.get('max_iterations', 10000))
        self.progress_interval_spin.setValue(self.current_config.get('progress_interval', 100))
        self.regroup_rounds_spin.setValue(self.current_config.get('regroup_rounds', 100))
        
        # Export settings
        self.export_pdf_check.setChecked(self.current_config.get('export_pdf', True))
        self.export_csv_check.setChecked(self.current_config.get('export_csv', False))
        self.export_json_check.setChecked(self.current_config.get('export_json', False))
        self.export_detailed_check.setChecked(self.current_config.get('export_detailed', False))
        
        self.file_prefix_edit.setText(self.current_config.get('file_prefix', 'rectpack_results'))
        self.include_timestamp_check.setChecked(self.current_config.get('include_timestamp', True))
        
        # Advanced settings
        self.enable_logging_check.setChecked(self.current_config.get('enable_logging', True))
        self.verbose_logging_check.setChecked(self.current_config.get('verbose_logging', False))
        self.log_performance_check.setChecked(self.current_config.get('log_performance', True))
        
        self.strict_validation_check.setChecked(self.current_config.get('strict_validation', True))
        self.warn_duplicates_check.setChecked(self.current_config.get('warn_duplicates', True))
        self.check_file_size_check.setChecked(self.current_config.get('check_file_size', True))
    
    def get_settings(self) -> dict:
        """Get current settings from the dialog."""
        settings = {
            # Algorithm settings
            'min_width': self.min_width_spin.value(),
            'max_width': self.max_width_spin.value(),
            'tolerance_length': self.tolerance_spin.value(),
            'start_with_largest': self.start_largest_check.isChecked(),
            'allow_split_rows': self.allow_split_check.isChecked(),
            'optimize_area': self.optimize_area_check.isChecked(),
            
            # Area constraints
            'min_total_area': self.min_area_spin.value() if self.min_area_spin.value() > 0 else None,
            'max_total_area': self.max_area_spin.value() if self.max_area_spin.value() > 0 else None,
            
            # Performance settings
            'max_iterations': self.max_iterations_spin.value(),
            'progress_interval': self.progress_interval_spin.value(),
            'regroup_rounds': self.regroup_rounds_spin.value(),
            'enable_caching': self.enable_caching_check.isChecked(),
            'cleanup_temp': self.cleanup_temp_check.isChecked(),
            
            # Export settings
            'export_pdf': self.export_pdf_check.isChecked(),
            'export_csv': self.export_csv_check.isChecked(),
            'export_json': self.export_json_check.isChecked(),
            'export_detailed': self.export_detailed_check.isChecked(),
            'file_prefix': self.file_prefix_edit.text().strip() or 'rectpack_results',
            'include_timestamp': self.include_timestamp_check.isChecked(),
            
            # Advanced settings
            'enable_logging': self.enable_logging_check.isChecked(),
            'verbose_logging': self.verbose_logging_check.isChecked(),
            'log_performance': self.log_performance_check.isChecked(),
            'strict_validation': self.strict_validation_check.isChecked(),
            'warn_duplicates': self.warn_duplicates_check.isChecked(),
            'check_file_size': self.check_file_size_check.isChecked(),
        }
        
        # Add custom config if provided
        custom_text = self.custom_config_edit.toPlainText().strip()
        if custom_text:
            try:
                custom_config = json.loads(custom_text)
                settings.update(custom_config)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
        
        return settings
    
    def save_settings(self):
        """Save settings and close dialog."""
        try:
            settings = self.get_settings()
            
            # Validate settings
            if settings['min_width'] >= settings['max_width']:
                QMessageBox.warning(self, "خطأ في الإعدادات", 
                                  "العرض الأدنى يجب أن يكون أقل من العرض الأقصى")
                return
            
            # Emit signal and close
            self.settings_changed.emit(settings)
            logger.info("تم حفظ الإعدادات المتقدمة")
            self.accept()
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الإعدادات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الإعدادات:\n{e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(self, "إعادة تعيين الإعدادات",
                                   "هل أنت متأكد من إعادة تعيين جميع الإعدادات إلى القيم الافتراضية؟",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Reset to default values
            default_config = {
                'min_width': 370,
                'max_width': 400,
                'tolerance_length': 100,
                'start_with_largest': True,
                'allow_split_rows': True,
                'optimize_area': False,
                'min_total_area': None,
                'max_total_area': None,
                'max_iterations': 10000,
                'progress_interval': 100,
                'regroup_rounds': 100,
                'export_pdf': True,
                'export_csv': False,
                'export_json': False,
                'export_detailed': False,
                'file_prefix': 'rectpack_results',
                'include_timestamp': True,
                'enable_logging': True,
                'verbose_logging': False,
                'log_performance': True,
                'strict_validation': True,
                'warn_duplicates': True,
                'check_file_size': True,
            }
            
            self.current_config = default_config
            self.load_current_settings()
            self.custom_config_edit.clear()
            
            logger.info("تم إعادة تعيين الإعدادات إلى القيم الافتراضية")