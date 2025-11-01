from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

class AppButton(QPushButton):
    def __init__(
            self,
            text: str="",
            icon_path: str = None,
            color: str  = "#0078D7",
            text_color: str = "#FFFFFF",
            hover_color: str = "#3399FF",
            fixed_size: QSize = QSize(180, 40),
            pressed_backgroundColor: str = "#1E1E1E",
            disabled_backgroundColor: str = "#555555",
            disabled_color: str = "#AAAAAA",
            parent = None
    ):
        super().__init__(text, parent)
        self.icon_path = icon_path
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.fixed_size =fixed_size
        self.pressed_backgroundColor = pressed_backgroundColor
        self.disabled_backgroundColor = disabled_backgroundColor
        self.disabled_color = disabled_color

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(self.fixed_size)
        if  self.icon_path:
            self.setIcon(QIcon(self.icon_path))
            self.setIconSize(QSize(20, 20))

        self.setStyleSheet(f"""
                QPushButton {{
                           background-color: {self.color};
                           color: {self.text_color};
                           border: none;
                           border-radius: 5px;
                           font-size: 14px;
                           font-weight: 500;
                           padding: 8px 12px;
                }}
                QPushButton:hover {{
                        background-color: {self.hover_color};
                }}
                QPushButton:pressed {{
                        background-color: {self.pressed_backgroundColor};
                }}
                QPushButton:disabled {{
                        background-color: {self.disabled_backgroundColor};
                        color: {self.disabled_color};
                }}
        """)
    def setButtonStyle(self, color: str = None, hover_color: str = None):
        if color:
            self.color = color
        if hover_color:
            self.hover_color = hover_color
        self._setup_ui()