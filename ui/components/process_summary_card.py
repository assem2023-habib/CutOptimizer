from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF, QSize

class CircularProgress(QWidget):
    def __init__(
        self,
        percentage= 75,
        arc_color= "#0078D7",
        track_color= "#E0E0E0",
        show_text= True,
        text_color= "#0078D7",
        parent= None,
    ):
        super().__init__(parent)
        self.percentage = percentage
        self.arc_color = QColor(arc_color)
        self.track_color = QColor(track_color)
        self.show_text = show_text
        self.text_color = QColor(text_color)

    def setPercentage(self, value: int):
        self.percentage = max(0, min(value, 100))
        self.update()

    def sizeHint(self):
        return QSize(80, 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(5, 5, self.width() - 10, self.height() - 10)
        start_angel = 90 * 16 
        span_angel = - self.percentage * 360 / 100 * 16

        pen = QPen(self.track_color, 8)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        pen.setColor(self.arc_color)
        painter.setPen(pen)
        painter.drawArc(rect, start_angel, span_angel)

        if self.show_text:
            painter.setPen(self.text_color)
            font = QFont()
            font.setPointSize(10)
            font.setWeight(QFont.Medium)
            painter.setFont(font)
            text = f"{int(self.percentage)}%"
            painter.drawText(self.rect(), Qt.AlignCenter, text)

class ProcessSummaryCard(QWidget):
    def __init__(
        self,
        title: str,
        main_value,
        card_background= "#FFFFFF",
        title_color= "#888888",
        main_value_color= "#000000",
        progress_percentage= 0,
        progress_arc_color= "#0078D7",
        progress_track_color= "#E0E0E0",
        show_percentage_text= True,
        parent= None,
    ):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            background-color: {card_background};
            border-radius: 10px;
        """)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            color:{title_color};
            font-size:12px;
            font-weight:400;
            text-transform:uppercase;
        """)

        self.value_label = QLabel(main_value)
        self.value_label.setStyleSheet(f"""
            color: {main_value_color};
            font-size: 22px;
            font-weight: bold;
        """)

        self.progress = CircularProgress(
            percentage= progress_percentage,
            arc_color= progress_arc_color,
            track_color= progress_track_color,
            show_text= show_percentage_text,
            text_color= progress_arc_color,
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.title_label)
        left_layout.addWidget(self.value_label)
        left_layout.addStretch()

        layout.addLayout(left_layout)
        layout.addWidget(self.progress, alignment= Qt.AlignRight)

    def setValue(self, value: str):
        self.value_label.setText(value)

    def setProgress(self, percent: int):
        self.progress.setPercentage(percent)