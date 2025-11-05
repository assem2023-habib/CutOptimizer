from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta

class ProgressStatusItem(QWidget):
    def __init__(
            self,
            status_text: str = "Processing...",
            current_status: str = "pending",
            parent= None
    ):
        super().__init__(parent)
        self.status_text = status_text
        self.current_status = current_status

        self._setup_ui()
        self._apply_status_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border-radius: 10px; background-color: #6c757d;")

        self.text_label = QLabel(self.status_text)
        self.text_label.setFont(QFont("Segoe UI", 10))
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        self.setLayout(layout)

    def _apply_status_style(self):
        status_color = {
            "success":  {"bg": "#28a745", "icon": "fa.check", "text": "#FFFFFF"},
            "in_progress": {"bg": "#0d6efd", "icon": "fa.refresh", "text": "#FFFFFF"},
            "failed":  {"bg": "#dc3545", "icon": "fa.times", "text": "#FFFFFF"},
            "pending": {"bg": "#6c757d", "icon": "fa.circle", "text": "#AAAAAA"},
        }

        if self.current_status not in status_color:
            self.current_status = "pending"

        cfg = status_color[self.current_status]

        icon = qta.icon(cfg['icon'],color = "#FFFFFF")
        self.icon_label.setPixmap(icon.pixmap(14, 14))

        self.icon_label.setStyleSheet(f"""
                border-radius: 10px;
                background-color: {cfg["bg"]};
            """)
        
        self.text_label.setStyleSheet(f"color: {cfg["text"]}")

        if self.current_status == "in_progress":
            self._start_spinner_animation