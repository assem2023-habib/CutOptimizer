from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QFont, QTransform
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
        self._rotation_angle = 0
        self._timer = None

        self._setup_ui()
        self._apply_status_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel(self.status_text)
        self.text_label.setFont(QFont("Segoe UI", 10))
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        self.setLayout(layout)

    def _apply_status_style(self):
        status_color = {
            "success":  {"bg": "#28a745", "icon": "fa5s.check", "text": "#FFFFFF"},
            "in_progress": {"bg": "#0d6efd", "icon": "fa5s.sync", "text": "#FFFFFF"},
            "failed":  {"bg": "#dc3545", "icon": "fa5s.times", "text": "#FFFFFF"},
            "pending": {"bg": "#6c757d", "icon": "fa5s.circle", "text": "#AAAAAA"},
        }

        if self.current_status not in status_color:
            self.current_status = "pending"

        cfg = status_color[self.current_status]

        icon = qta.icon(cfg['icon'],color = "#FFFFFF")
        self.icon_label.setPixmap(icon.pixmap(16, 16))

        self.icon_label.setStyleSheet(f"""
                border-radius: 11px;
                background-color: {cfg['bg']};
            """)
        
        self.text_label.setStyleSheet(f"color: {cfg['text']}")
        
        if self.current_status == "in_progress":
            self._start_spinner_animation
        else:
            self._stop_spinner_animation()
    
    def _start_spinner_animation(self):
        if self._timer:
            return
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate_icon)
        self._timer.start(80)

    def _stop_spinner_animation(self):
        if self._timer:
            self._timer.stop()
            self._timer = None

    def _rotate_icon(self):
        pixmap = self.icon_label.pixmap()
        if not pixmap:
            return
        self._rotation_angle = (self._rotation_angle + 30) % 360
        transform = QTransform().rotate(self._rotation_angle)
        rotated = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.icon_label.setPixmap(rotated)
    
    def set_status(self, new_status: str):
        self.current_status = new_status
        self._apply_status_style()
    
    def set_text(self, text: str):
        self.text_label.setText(text)