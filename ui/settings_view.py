"""
نافذة الإعدادات - تحتوي على جميع خيارات الإعدادات بما في ذلك تغيير الخلفية
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from ui.components.app_button import AppButton
from ui.components.appearance_settings_widget import AppearanceSettingsWidget
from ui.components.machine_sizes_widget import MachineSizesWidget
from ui.styles.settings_styles import SettingsStyles


class SettingsView(QDialog):
    """نافذة الإعدادات الرئيسية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("⚙️ الإعدادات")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(SettingsStyles.get_dialog_stylesheet())
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title_label = QLabel("⚙️ إعدادات التطبيق")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #00FF91; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # قسم المظهر
        appearance_group = self._create_appearance_section()
        main_layout.addWidget(appearance_group)
        
        # قسم مقاسات المكنات
        machine_sizes_group = self._create_machine_sizes_section()
        main_layout.addWidget(machine_sizes_group)
        
        # مساحة فارغة للتوسع المستقبلي
        main_layout.addStretch()
        
        # أزرار الإجراءات
        buttons_layout = self._create_action_buttons()
        main_layout.addLayout(buttons_layout)
    
    def _create_appearance_section(self):
        """إنشاء قسم إعدادات المظهر"""
        appearance_group = QGroupBox("🎨 المظهر والخلفية")
        layout = QVBoxLayout()
        
        # Add appearance widget
        self.appearance_widget = AppearanceSettingsWidget(self.parent_widget)
        layout.addWidget(self.appearance_widget)
        
        appearance_group.setLayout(layout)
        return appearance_group
    
    def _create_machine_sizes_section(self):
        """إنشاء قسم إدارة مقاسات المكنات"""
        sizes_group = QGroupBox("📏 مقاسات المكنات")
        layout = QVBoxLayout()
        
        # Add machine sizes widget
        self.machine_sizes_widget = MachineSizesWidget()
        layout.addWidget(self.machine_sizes_widget)
        
        sizes_group.setLayout(layout)
        return sizes_group
    
    def _create_action_buttons(self):
        """إنشاء أزرار الإجراءات (إغلاق)"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = AppButton(
            text="✖️ إغلاق",
            color="#D32F2F",
            hover_color="#F44336",
            text_color="#FFFFFF",
            fixed_size=QSize(120, 38)
        )
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(close_btn)
        return buttons_layout
