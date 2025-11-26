from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import Qt

class StatisticCard(QFrame):
    """A colored statistic card with glass effect"""
    def __init__(self, title, value, subtitle, bg_color, icon_text="📊", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.bg_color = bg_color
        self.icon_text = icon_text
        
        self.setObjectName("statisticCard")
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(self.icon_text)
        icon_label.setStyleSheet("font-size: 24px; color: white; background-color: transparent;")
        layout.addWidget(icon_label)
        
        # Spacer
        layout.addStretch()
        
        # Large number
        value_label = QLabel(self.value)
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: transparent;
        """)
        layout.addWidget(value_label)
        
        # Description
        desc_label = QLabel(self.title)
        desc_label.setObjectName("descLabel")
        desc_label.setStyleSheet("""
            font-size: 14px;
            font-weight: normal;
            color: #FFFFFF;
            background-color: transparent;
        """)
        layout.addWidget(desc_label)
        
        # Sub-description
        sub_label = QLabel(self.subtitle)
        sub_label.setObjectName("subLabel")
        sub_label.setStyleSheet("""
            font-size: 12px;
            font-weight: normal;
            color: rgba(255, 255, 255, 0.8);
            background-color: transparent;
        """)
        layout.addWidget(sub_label)
    
    def setup_style(self):
        self.setStyleSheet(f"""
            QFrame#statisticCard {{
                background-color: {self.bg_color};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                min-height: 180px;
            }}
        """)

class StatisticsSummaryWidget(QWidget):
    """A widget containing the row of 3 statistic cards"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Card 1: Total Elements (Blue)
        self.total_card = StatisticCard(
            title="Total Elements",
            value="0",
            subtitle="Complete dataset processed",
            bg_color="#4285F4",
            icon_text="💾"
        )
        layout.addWidget(self.total_card)
        
        # Card 2: Successfully Grouped (Green)
        self.success_card = StatisticCard(
            title="Successfully Grouped",
            value="0",
            subtitle="0.0% success rate",
            bg_color="#28A745",
            icon_text="✓"
        )
        layout.addWidget(self.success_card)
        
        # Card 3: Remaining Elements (Orange)
        self.remaining_card = StatisticCard(
            title="Remaining Elements",
            value="0",
            subtitle="0.0% ungrouped",
            bg_color="#FFA000",
            icon_text="⚠"
        )
        layout.addWidget(self.remaining_card)
        
    def update_statistics(self, total=None, success=None, remaining=None):
        """Update the statistics cards"""
        if total is not None:
            self.total_card.findChild(QLabel, "valueLabel").setText(str(total))
        if success is not None:
            self.success_card.findChild(QLabel, "valueLabel").setText(str(success))
        if remaining is not None:
            self.remaining_card.findChild(QLabel, "valueLabel").setText(str(remaining))
