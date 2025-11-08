from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QSize, Qt
from ui.components.app_button import AppButton

class ProcessControllSection(QWidget):
    def __init__(
            self,
            on_start_clicked= None,
            on_stop_clicked= None,
            on_open_excel_clicked=None,
            is_start_enabled=True,
            is_stop_enabled=False,
            parent= None
        ):
        super().__init__(parent)

        self.on_start_clicked = on_start_clicked
        self.on_stop_clicked = on_stop_clicked
        self.on_open_excel_clicked = on_open_excel_clicked
        self.is_start_enabled = bool(is_start_enabled)
        self.is_stop_enabled = bool(is_stop_enabled)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(40)
        main_layout.setAlignment(Qt.AlignCenter)

        self.start_btn = AppButton(
            text= "▶ Start",
            color= "#28A745",
            hover_color= "#34C759",
            text_color= "#FFFFFF",
            fixed_size= QSize(250, 50)
        )

        self.start_btn.setEnabled(bool(self.is_start_enabled))
        if self.on_start_clicked:
            self.start_btn.clicked.connect(self.on_start_clicked)

        self.open_excel_btn = AppButton(
            text="📊 فتح ملف Excel",
            color="#0d6efd",
            hover_color="#007bff",
            text_color="#FFFFFF",
            fixed_size=QSize(200, 50)
        )
        self.open_excel_btn.setVisible(False)
        if self.on_open_excel_clicked:
            self.open_excel_btn.clicked.connect(self.on_open_excel_clicked)

        self.stop_btn = AppButton(
            text= "⏹ Stop",
            color= "#DC3545",
            hover_color= "#FF4C4C",
            text_color= "#FFFFFF",
            fixed_size= QSize(250, 50)
        )

        self.stop_btn.setEnabled(bool(self.is_stop_enabled))
        if self.on_stop_clicked:
            self.stop_btn.clicked.connect(self.on_stop_clicked)

        main_layout.addWidget(self.start_btn)
        main_layout.addStretch(1)
        main_layout.addWidget(self.open_excel_btn)
        main_layout.addStretch(1)
        main_layout.addWidget(self.stop_btn)
        # main_layout.addStretch()
        self.setLayout(main_layout)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #F8F9FA;
                border-radius: 8px;
            }}
        """)

    def set_buttons_enabled(self, start_enabled: bool, stop_enabled: bool):
        self.start_btn.setEnabled(start_enabled)
        self.stop_btn.setEnabled(stop_enabled)

    def disabele_all(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

    def enable_start_only(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def enable_stop_only(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
    def show_open_excel_button(self, visible=True):
        """إظهار أو إخفاء زر فتح ملف Excel"""
        self.open_excel_btn.setVisible(visible)