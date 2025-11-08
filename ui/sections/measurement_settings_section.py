from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsBlurEffect,  QGraphicsDropShadowEffect

from ui.components.setting_input_field import SettingInputField 

import os

class MeasurementSettingsSection(QWidget):
    def __init__(self,
                 section_title_text: str = "MEASUREMENT SETTINGS",
                 section_background_color: str = "#F8F9FA",
                 section_title_text_color: str = "#A0A0A0",
                 is_inputs_enabled: bool = True,
                 parent = None
                 ):
        super().__init__(parent)

        self.section_title_text = section_title_text
        self.section_background_color = section_background_color
        self.section_title_text_color = section_title_text_color
        self.is_inputs_enabled = is_inputs_enabled

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(18)

        title_label = QLabel(self.section_title_text)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.section_title_text_color};")
        title_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_label)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(30)

        self.min_input = SettingInputField(
            label_text="Minimum Width",
            input_value=370,
            is_enabled= self.is_inputs_enabled
        )

        self.max_input = SettingInputField(
            label_text="Maximum Width",
            input_value= 400,
            is_enabled= self.is_inputs_enabled
        )

        self.margin_input = SettingInputField(
            label_text="Tolerance",
            input_value= 100,
            is_enabled=self.is_inputs_enabled
        )
        
        for widget in [self.min_input, self.max_input, self.margin_input]:
            fields_layout.addWidget(widget, stretch=1)

        main_layout.addLayout(fields_layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.setGraphicsEffect(blur)

    def _apply_styles(self):
        qss_path = os.path.join(os.path.dirname(__file__), "../styles/style.qss")
        qss_path = os.path.abspath(qss_path)

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"⚠️ ملف التنسيقات غير موجود: {qss_path}")

    def set_inputs_enabled(self, enabled: bool):
        self.min_input.input.setEnabled(enabled)
        self.max_input.input.setEnabled(enabled)
        self.margin_input.input.setEnabled(enabled)