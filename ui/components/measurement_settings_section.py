from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from .setting_input_field import SettingInputField 

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

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        title_label = QLabel(self.section_title_text)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.section_title_text_color};")
        title_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_label)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(16)

        self.min_input = SettingInputField(
            label_text="Minimum Width",
            input_value="370",
            is_enabled= self.is_inputs_enabled
        )

        self.max_input = SettingInputField(
            label_text="Maximum Width",
            input_value= "400",
            is_enabled= self.is_inputs_enabled
        )

        self.margin_input = SettingInputField(
            label_text="Tolerance",
            input_value= 100,
            is_enabled=self.is_inputs_enabled
        )

        fields_layout.addWidget(self.min_input)
        fields_layout.addWidget(self.max_input)
        fields_layout.addWidget(self.margin_input)
        fields_layout.addStretch()

        main_layout.addLayout(fields_layout)

        self.setStyleSheet(f"""
            background-color: transparent;
            border-radius: 8px;
        """)

    def set_inputs_enabled(self, enabled: bool):
        self.min_input.input.setEnabled(enabled)
        self.max_input.input.setEnabled(enabled)
        self.margin_input.input.setEnabled(enabled)