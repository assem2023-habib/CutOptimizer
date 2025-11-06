from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout,QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QSize
from .app_button import AppButton

class TopButtonSection(QWidget):
    def __init__(self,
                 on_import_clicked= None,
                 on_export_clicked= None,
                 parent= None):
        super().__init__(parent)
        
        self.on_import_clicked = on_import_clicked
        self.on_export_clicked = on_export_clicked

        self._setup_ui()

    def _setup_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_edit = QLineEdit()
        self.input_edit.setMinimumWidth(400)

        self.import_btn = AppButton(
            text="📥 Import Excel File",
            color="#0078D7",
            hover_color="#3399FF"
        )
        self.import_btn.setFixedWidth(180)
        if self.on_import_clicked:
            self.import_btn.clicked.connect(self.on_import_clicked)

        input_layout.addWidget(self.import_btn)

        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)

        self.output_edit = QLineEdit()
        self.output_edit.setMinimumWidth(400)

        self.export_btn = AppButton(
            text="💾  Export File",
            color= "#0078D7",
            hover_color= "#3399FF",
        )
        self.export_btn.setFixedWidth(180)
        if self.on_export_clicked:
            self.export_btn.clicked.connect(self.on_export_clicked)

        output_layout.addWidget(self.export_btn)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)


        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-radius: 8px;
            }
            QLineEdit {
                padding: 6px 8px;
                border: 1px solid #CCC;
                border-radius: 4px;
            }
            QLabel {
                color: #333;
            }
        """)
