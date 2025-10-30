from PySide6.QtWidgets import QPushButton, QFileDialog
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt

class WidgetButton(QPushButton):
    def __init__(self, parent, text= "Export File", 
                 fontSize = 20, backgroundColor = "#1e88e5",backgroundColorHover = "#2196f3", 
                 backgroundColorPressed = "#1976d2",backgroundColorDisabled = "#5c5c5c",
                 color = "#f5f5f5", colorDisabled = "#bdbdbd"):
        super().__init__(text, parent)

        font = QFont("Segoe UI", fontSize, QFont.Medium)
        self.setFont(font)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(text)

        self.setStyleSheet(f"""
            QPushButton{{
                background-color: {backgroundColor};
                color:{color};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size:{font}px;
                font-weight:500;
                height: 60px;
                max-width: 400px;
                text-align: center;
            }}
            QPushButton:hover{{
                background-color: {backgroundColorHover};
                }}
            QPushButton:pressed{{
                background-color: {backgroundColorPressed};
                }}
            QPushButton:focus{{
                    outline: none;
                    border: 2px solid #64ffda;           
                }}
            QPushButton:disabled{{
                    background-color:{backgroundColorDisabled};
                    color:{colorDisabled};
                    cursor: not-allowed;
                    opacity: 0.7;
                }}
        """)