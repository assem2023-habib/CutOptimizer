from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsBlurEffect

from ui.components.progress_status_item import ProgressStatusItem

class StatusAndLogSection(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)
        
        self.status_item = ProgressStatusItem("جاهز لبدء العملية", "pending")
        self.status_item.setStyleSheet("background-color: transparent; color:white;")

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(150)
        self.log.setObjectName("logBox")

        layout.addWidget(self.status_item)
        layout.addWidget(self.log)

        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.setGraphicsEffect(blur)

    def _apply_style(self):
        self.setObjectName("statusLogContainer")
        self.setStyleSheet("""
            #logBox {
                background-color: rgba(255, 255, 255, 20);
                color: #E0E0E0;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 6px;
                padding: 8px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 10pt;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FCFCFCFF;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)
    def append_log(self, text: str):
        """إضافة نص جديد إلى السجل"""
        self.log.append(text)

    def clear_log(self):
        """مسح السجل"""
        self.log.clear()

    def set_status(self, text: str, state: str = "pending"):
        """تحديث نص حالة ProgressStatusItem"""
        self.status_item.set_status(text, state)