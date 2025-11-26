from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen
from PySide6.QtSvgWidgets import QSvgWidget
import io

class SummaryStatCard(QWidget):
    """
    A card component for displaying summary statistics with an icon, 
    large number, title, and subtitle.
    """
    def __init__(self, title, value, subtitle, icon_svg, bg_color, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.value_text = value
        self.subtitle_text = subtitle
        self.icon_svg_content = icon_svg
        self.bg_color = bg_color
        
        self.setup_ui()
        
    def setup_ui(self):
        # Set fixed height for consistency, width will be flexible
        self.setMinimumHeight(180)
        
        # Enable styled background for custom painting if needed, 
        # but we will use paintEvent for rounded corners and custom background
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Icon
        self.icon_widget = QSvgWidget()
        self.icon_widget.load(self.icon_svg_content.encode('utf-8'))
        self.icon_widget.setFixedSize(24, 24)
        # We need to ensure the icon is white. 
        # The SVG string passed should ideally have fill="white" or stroke="white".
        layout.addWidget(self.icon_widget)
        
        layout.addSpacing(12)
        
        # Main Number
        self.value_label = QLabel(self.value_text)
        self.value_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 42px;
            font-weight: 800;
            color: #FFFFFF;
            background: transparent;
        """)
        layout.addWidget(self.value_label)
        
        # Title
        self.title_label = QLabel(self.title_text)
        self.title_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #FFFFFF;
            background: transparent;
        """)
        layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel(self.subtitle_text)
        self.subtitle_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.75);
            background: transparent;
        """)
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()

        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rect background
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 12, 12)
        
        painter.fillPath(path, QBrush(QColor(self.bg_color)))

    def update_value(self, new_value, new_subtitle=None):
        self.value_text = str(new_value)
        self.value_label.setText(self.value_text)
        if new_subtitle:
            self.subtitle_text = new_subtitle
            self.subtitle_label.setText(self.subtitle_text)
