from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPainter, QLinearGradient, QColor


class GlassCard(QFrame):
    """A glass-morphism styled card widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            QFrame#glassCard {
                background-color: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 24px;
            }
        """)


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
        icon_label.setStyleSheet("font-size: 24px; color: white;")
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
        """)
        layout.addWidget(value_label)
        
        # Description
        desc_label = QLabel(self.title)
        desc_label.setObjectName("descLabel")
        desc_label.setStyleSheet("""
            font-size: 14px;
            font-weight: normal;
            color: #FFFFFF;
        """)
        layout.addWidget(desc_label)
        
        # Sub-description
        sub_label = QLabel(self.subtitle)
        sub_label.setObjectName("subLabel")
        sub_label.setStyleSheet("""
            font-size: 12px;
            font-weight: normal;
            color: rgba(255, 255, 255, 0.8);
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


class GradientProgressBar(QProgressBar):
    """Custom progress bar with gradient fill"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(12)
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            QProgressBar {
                background-color: #E0E0E0;
                border-radius: 6px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7B68EE,
                    stop:1 #9370DB
                );
                border-radius: 6px;
            }
        """)


class ProgressDetailItem(QWidget):
    """A single label-value pair for progress details"""
    def __init__(self, label, value, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Label
        label = QLabel(self.label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 13px;
            color: #666666;
            font-weight: normal;
        """)
        layout.addWidget(label)
        
        # Value
        value = QLabel(self.value_text)
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            font-weight: 600;
        """)
        layout.addWidget(value)
    
    def update_value(self, new_value):
        """Update the value text"""
        self.value_text = new_value
        self.layout().itemAt(1).widget().setText(new_value)


class CurrentOperationsWidget(GlassCard):
    """Main Current Operations component with glass morphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Progress Section
        self.create_progress_section(main_layout)
        
        # Progress Details
        self.create_progress_details(main_layout)
        
        # Summary Statistics Cards
        self.create_statistics_cards(main_layout)
    
    def create_header(self, parent_layout):
        """Create the header with icon and title"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icon (using emoji as placeholder - you can replace with actual icon)
        icon_label = QLabel("☰")
        icon_label.setStyleSheet("""
            font-size: 24px;
            color: #6B4EEB;
        """)
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Current Operations")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #333333;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        parent_layout.addLayout(header_layout)
    
    def create_progress_section(self, parent_layout):
        """Create the progress bar section"""
        # Progress header with title and percentage
        progress_header = QHBoxLayout()
        
        progress_title = QLabel("Processing Data...")
        progress_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #333333;
        """)
        progress_header.addWidget(progress_title)
        
        progress_header.addStretch()
        
        self.percentage_label = QLabel("67%")
        self.percentage_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #6B4EEB;
        """)
        progress_header.addWidget(self.percentage_label)
        
        parent_layout.addLayout(progress_header)
        
        # Progress bar
        self.progress_bar = GradientProgressBar()
        self.progress_bar.setValue(67)
        parent_layout.addWidget(self.progress_bar)
    
    def create_progress_details(self, parent_layout):
        """Create the progress details section"""
        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)
        
        # Create detail items
        self.current_step = ProgressDetailItem("Current Step", "Grouping Items")
        self.processed = ProgressDetailItem("Processed", "834 / 1245")
        self.elapsed_time = ProgressDetailItem("Elapsed Time", "2m 34s")
        self.estimated_remaining = ProgressDetailItem("Estimated Remaining", "1m 12s")
        
        details_layout.addWidget(self.current_step)
        details_layout.addWidget(self.processed)
        details_layout.addWidget(self.elapsed_time)
        details_layout.addWidget(self.estimated_remaining)
        
        parent_layout.addLayout(details_layout)
    
    def create_statistics_cards(self, parent_layout):
        """Create the three summary statistics cards"""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        # Card 1: Total Elements (Blue)
        self.total_card = StatisticCard(
            title="Total Elements",
            value="1,245",
            subtitle="Complete dataset processed",
            bg_color="#4285F4",
            icon_text="💾"
        )
        stats_layout.addWidget(self.total_card)
        
        # Card 2: Successfully Grouped (Green)
        self.success_card = StatisticCard(
            title="Successfully Grouped",
            value="987",
            subtitle="79.3% success rate",
            bg_color="#28A745",
            icon_text="✓"
        )
        stats_layout.addWidget(self.success_card)
        
        # Card 3: Remaining Elements (Orange)
        self.remaining_card = StatisticCard(
            title="Remaining Elements",
            value="258",
            subtitle="20.7% ungrouped",
            bg_color="#FFA000",
            icon_text="⚠"
        )
        stats_layout.addWidget(self.remaining_card)
        
        parent_layout.addLayout(stats_layout)
    
    def update_progress(self, percentage, current_step="", processed="", 
                       elapsed="", remaining=""):
        """Update progress bar and details"""
        self.progress_bar.setValue(percentage)
        self.percentage_label.setText(f"{percentage}%")
        
        if current_step:
            self.current_step.update_value(current_step)
        if processed:
            self.processed.update_value(processed)
        if elapsed:
            self.elapsed_time.update_value(elapsed)
        if remaining:
            self.estimated_remaining.update_value(remaining)
    
    def update_statistics(self, total=None, success=None, remaining=None):
        """Update the statistics cards"""
        if total is not None:
            self.total_card.findChild(QLabel, "valueLabel").setText(str(total))
        if success is not None:
            self.success_card.findChild(QLabel, "valueLabel").setText(str(success))
        if remaining is not None:
            self.remaining_card.findChild(QLabel, "valueLabel").setText(str(remaining))
