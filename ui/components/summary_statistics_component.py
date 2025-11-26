from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, QBrush
from PySide6.QtSvgWidgets import QSvgWidget

class SummaryStatCard(QFrame):
    """
    A single statistic card with a specific background color, icon, and values.
    """
    def __init__(self, title, value, subtitle, bg_color, icon_svg, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.bg_color = bg_color
        self.icon_svg = icon_svg
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(4) # Small spacing between elements
        
        # Icon
        self.icon_widget = QSvgWidget()
        self.icon_widget.load(self.icon_svg.encode('utf-8'))
        self.icon_widget.setFixedSize(24, 24)
        self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.icon_widget.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_widget)
        
        # Spacer between icon and number
        layout.addSpacing(12)
        
        # Main Number
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("""
            font-family: 'Inter', 'Roboto', sans-serif;
            font-size: 42px;
            font-weight: 800;
            color: #FFFFFF;
            background: transparent;
        """)
        layout.addWidget(self.value_label)
        
        # Descriptive Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            font-family: 'Inter', 'Roboto', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #FFFFFF;
            background: transparent;
        """)
        layout.addWidget(self.title_label)
        
        # Sub-description
        self.subtitle_label = QLabel(self.subtitle)
        self.subtitle_label.setStyleSheet("""
            font-family: 'Inter', 'Roboto', sans-serif;
            font-size: 13px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        """)
        layout.addWidget(self.subtitle_label)
        
        # Push everything to the top
        layout.addStretch()

    def setup_style(self):
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30)) # Subtle shadow
        self.setGraphicsEffect(shadow)
        
        # Set minimum size
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        """Custom paint event for rounded corners and background color"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rect
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        
        painter.fillPath(path, QBrush(QColor(self.bg_color)))

    def update_value(self, value, subtitle=None):
        self.value_label.setText(str(value))
        if subtitle:
            self.subtitle_label.setText(subtitle)


class SummaryStatisticsComponent(QWidget):
    """
    Component containing three statistic cards: Total, Success, Remaining.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20) # Gutter
        
        # SVGs
        # Database Icon (Stack of disks)
        db_icon = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 3C16.97 3 21 4.34 21 6V18C21 19.66 16.97 21 12 21C7.03 21 3 19.66 3 18V6C3 4.34 7.03 3 12 3Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 12C21 13.66 16.97 15 12 15C7.03 15 3 13.66 3 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 6C21 7.66 16.97 9 12 9C7.03 9 3 7.66 3 6" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

        # Checkmark Icon
        check_icon = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M20 6L9 17L4 12" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

        # Warning Icon
        warn_icon = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M10.29 3.86L1.82 18C1.64556 18.3024 1.55293 18.6453 1.55201 18.9945C1.55108 19.3437 1.64189 19.6871 1.81443 19.9897C1.98697 20.2922 2.2348 20.5424 2.53105 20.7138C2.8273 20.8852 3.16118 20.9716 3.5 20.9716H20.5C20.8388 20.9716 21.1727 20.8852 21.469 20.7138C21.7652 20.5424 22.013 20.2922 22.1856 19.9897C22.3581 19.6871 22.4489 19.3437 22.448 18.9945C22.4471 18.6453 22.3544 18.3024 22.18 18L13.71 3.86C13.5317 3.56611 13.2807 3.32312 12.9835 3.1563C12.6864 2.98948 12.3538 2.90498 12.019 2.91191C11.6842 2.91884 11.3591 3.01695 11.077 3.19599C10.795 3.37503 10.5661 3.62844 10.415 3.927L10.29 3.86Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 9V13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 17H12.01" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

        # Card 1: Total Elements
        self.total_card = SummaryStatCard(
            title="Total Elements",
            value="1,245",
            subtitle="Complete dataset processed",
            bg_color="#4285F4",
            icon_svg=db_icon
        )
        layout.addWidget(self.total_card)
        
        # Card 2: Successfully Grouped
        self.success_card = SummaryStatCard(
            title="Successfully Grouped",
            value="987",
            subtitle="79.3% success rate",
            bg_color="#28A745",
            icon_svg=check_icon
        )
        layout.addWidget(self.success_card)
        
        # Card 3: Remaining Elements
        self.remaining_card = SummaryStatCard(
            title="Remaining Elements",
            value="258",
            subtitle="20.7% ungrouped",
            bg_color="#FFA000",
            icon_svg=warn_icon
        )
        layout.addWidget(self.remaining_card)

    def update_statistics(self, total=None, grouped=None, remaining=None):
        """
        Update the statistics on the cards.
        """
        if total is not None:
            self.total_card.update_value(f"{total:,}")
            
        if grouped is not None:
            # Calculate percentage if total is available
            # Note: This logic assumes total is updated or stored. 
            # For now, just update the value.
            self.success_card.update_value(f"{grouped:,}")
            
        if remaining is not None:
            self.remaining_card.update_value(f"{remaining:,}")
