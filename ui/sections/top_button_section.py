from PySide6.QtWidgets import QWidget, QHBoxLayout,QLineEdit
from PySide6.QtWidgets import QGraphicsBlurEffect
from PySide6.QtCore import Qt

from ui.widgets.app_button import AppButton

import os

class TopButtonSection(QWidget):
    def __init__(self,
                 on_import_clicked= None,
                 on_export_clicked= None,
                 parent= None):
        super().__init__(parent)
        
        self.on_import_clicked = on_import_clicked
        self.on_export_clicked = on_export_clicked

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(40)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("حدد ملف الإدخال (Input Excel File)...")
        self.input_edit.setMinimumWidth(450)

        self.import_btn = AppButton(
            text="📥 Import Excel File",
            color="#0078D7",
            hover_color="#3399FF"
        )
        self.import_btn.setFixedWidth(300)
        if self.on_import_clicked:
            self.import_btn.clicked.connect(self.on_import_clicked)

        input_layout.addWidget(self.import_btn)

        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("حدد مكان حفظ الملف الناتج (Output Excel File)...")
        self.output_edit.setMinimumWidth(450)

        self.export_btn = AppButton(
            text="💾  Export File",
            color= "#0078D7",
            hover_color= "#3399FF",
        )
        self.export_btn.setFixedWidth(300)
        if self.on_export_clicked:
            self.export_btn.clicked.connect(self.on_export_clicked)

        output_layout.addWidget(self.export_btn)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)

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
                raise    