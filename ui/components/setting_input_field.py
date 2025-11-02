from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QColor, QFont, QIntValidator
from PySide6.QtCore import Qt

class SettingInputField(QWidget):
    def __init__(
            self,
            label_text: str = "MINIMUM SIZE",
            label_text_color: str ="#AAAAAA",
            input_value: str = "0",
            input_text_color: str = "#FFFFFF",
            input_background_color: str = "#2C2C2C",
            input_border_color: str = "#555555",
            focus_border_color: str = "#0078D7",
            input_type: str = "number",
            is_enabled: bool = True,
            parent= None
        ):
        super().__init__(parent)

        self.label_text = label_text
        self.label_text_color = label_text_color
        self.input_value = input_value
        self.input_text_color = input_text_color
        self.input_background_color = input_background_color
        self.input_border_color = input_border_color
        self.focus_border_color = focus_border_color
        self.input_type = input_type
        self.is_enabled = is_enabled

        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        self.label = QLabel(self.label_text)
        self.label.setStyleSheet(f"color: {self.label_text_color}; font-weight: 400;")
        self.label.setFont(QFont("Sego UI", 9))
        self.label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label)

        self.input = QLineEdit(self)
        self.input.setText(self.input_value)
        self.input.setEnabled(self.is_enabled)

        if self.input_type == "number":
            self.input.setValidator(QIntValidator())

        self.input.setAlignment(Qt.AlignCenter)
        self.input.setFixedHeight(32)
        self.input.setFont(QFont("Segoe UI", 10))
        self.input.setStyleSheet(self._get_default_style())

        self.input.focusInEvent = self._on_focus_in
        self.input.focusOutEvent = self._on_focus_out

        layout.addWidget(self.input)
    
    def _get_default_style(self):
        bg = self.input_background_color
        border = self.input_border_color
        text = self.input_text_color
        disabled_bg = "#444444"
        disabled_text = "#AAAAAA"
        
        return f"""
                QLineEdit {{
                    background-color: {bg};
                    color: {text};
                    border: 1px solid {border};
                    border-radius: 5px;
                    padding: 4px 8px;
                }}
                QLineEdit:disabled {{
                    background-color: {disabled_bg};
                    color: {disabled_text};
                }}
            """
    
    def _on_focus_in(self, event):
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.input_background_color};
                color: {self.input_text_color};
                border: 1px solid {self.focus_border_color};
                border-radius: 5px;
                padding: 4px 8px;     
            }}
        """)
        return QLineEdit.focusInEvent(self.input, event)
    
    def _on_focus_out(self, event):
        self.input.setStyleSheet(self._get_default_style())
        return QLineEdit.focusOutEvent(self.input, event)
