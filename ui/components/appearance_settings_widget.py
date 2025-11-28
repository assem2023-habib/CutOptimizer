"""
Appearance Settings Widget
Handles background image and gradient selection
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QRadioButton, QButtonGroup, QComboBox)
from PySide6.QtCore import QSize, Signal
from ui.widgets.app_button import AppButton
from ui.styles.settings_styles import SettingsStyles
from ui.constants.gradients import GRADIENTS
from core.utilies.background_utils import change_background, save_background_gradient
from core.config.config_manager import ConfigManager


class AppearanceSettingsWidget(QWidget):
    """Widget for managing appearance settings (background)"""
    
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.gradients = GRADIENTS
        self._setup_ui()
        self._setup_initial_state()
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Description
        desc_label = QLabel("قم بتخصيص مظهر التطبيق حسب تفضيلاتك")
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Background type selection
        self._create_background_type_selection(layout)
        
        # Image container
        self.image_container = self._create_image_controls()
        layout.addWidget(self.image_container)
        
        # Gradient container
        self.gradient_container = self._create_gradient_controls()
        layout.addWidget(self.gradient_container)
        
        # Note
        note_label = QLabel("💡 نصيحة: اختر نمط الخلفية الذي يريح عينيك")
        note_label.setStyleSheet("color: #808080; font-size: 10px; font-style: italic;")
        layout.addWidget(note_label)
        
        # Connect events
        self.bg_type_group.buttonClicked.connect(self._on_bg_type_changed)
    
    def _create_background_type_selection(self, layout):
        """Creates radio buttons for background type"""
        type_layout = QHBoxLayout()
        self.bg_type_group = QButtonGroup(self)
        
        self.radio_image = QRadioButton("صورة خلفية")
        self.radio_image.setStyleSheet("color: white; font-size: 12px;")
        self.radio_gradient = QRadioButton("تدرج لوني")
        self.radio_gradient.setStyleSheet("color: white; font-size: 12px;")
        
        self.bg_type_group.addButton(self.radio_image)
        self.bg_type_group.addButton(self.radio_gradient)
        
        type_layout.addWidget(self.radio_image)
        type_layout.addWidget(self.radio_gradient)
        type_layout.addStretch()
        layout.addLayout(type_layout)
    
    def _create_image_controls(self):
        """Creates image background controls"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("🖼️ صورة الخلفية:")
        label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        
        self.change_bg_btn = AppButton(
            text="📁 تغيير الخلفية",
            color="#2D5F8D",
            hover_color="#3A7DAB",
            text_color="#FFFFFF",
            fixed_size=QSize(150, 35)
        )
        self.change_bg_btn.clicked.connect(self._change_background)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(self.change_bg_btn)
        
        return container
    
    def _create_gradient_controls(self):
        """Creates gradient background controls"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("🎨 اختر التدرج:")
        label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        
        self.gradient_combo = QComboBox()
        self.gradient_combo.setMinimumWidth(200)
        self.gradient_combo.setStyleSheet(SettingsStyles.get_combo_stylesheet())
        
        for name, _ in self.gradients:
            self.gradient_combo.addItem(name)
        
        self.gradient_combo.currentIndexChanged.connect(self._apply_gradient)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(self.gradient_combo)
        
        return container
    
    def _setup_initial_state(self):
        """Sets initial state based on config"""
        bg_image = ConfigManager.get_value("background_image", "")
        has_image = bool(bg_image)
        
        if has_image:
            self.radio_image.setChecked(True)
            self.gradient_container.setVisible(False)
        else:
            self.radio_gradient.setChecked(True)
            self.image_container.setVisible(False)
    
    def _on_bg_type_changed(self, button):
        """Handles background type change"""
        if button == self.radio_image:
            self.image_container.setVisible(True)
            self.gradient_container.setVisible(False)
        else:
            self.image_container.setVisible(False)
            self.gradient_container.setVisible(True)
            self._apply_gradient(self.gradient_combo.currentIndex())
    
    def _apply_gradient(self, index):
        """Applies the selected gradient"""
        if 0 <= index < len(self.gradients) and self.parent_window:
            gradient_style = self.gradients[index][1]
            save_background_gradient(index)
            self.parent_window.setStyleSheet(f"#MainWindow {{ background: {gradient_style}; }}")
    
    def _change_background(self):
        """Opens file dialog to change background image"""
        if self.parent_window:
            change_background(self.parent_window)
