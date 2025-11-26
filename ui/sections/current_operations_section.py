from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui.components.glass_card_layout import GlassCardLayout
from ui.components.statistics_summary_widget import StatisticsSummaryWidget

# Simple SVG for the list icon
LIST_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#6B4EEB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>"""



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
            background-color: transparent;
        """)
        layout.addWidget(label)
        
        # Value
        self.value_label = QLabel(self.value_text)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            font-weight: 600;
            background-color: transparent;
        """)
        layout.addWidget(self.value_label)
    
    def update_value(self, new_value):
        """Update the value text"""
        self.value_text = new_value
        self.value_label.setText(new_value)

class CurrentOperationsSection(GlassCardLayout):
    """Main Current Operations component with glass morphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(title="Current Operations", icon_svg=LIST_ICON_SVG, parent=parent)
        self.setup_content_ui()
        
    def setup_content_ui(self):
        # Create a container for the vertical layout content
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Progress Section
        self.create_progress_section(content_layout)
        
        # Progress Details
        self.create_progress_details(content_layout)
        
        # Summary Statistics Cards
        self.create_statistics_cards(content_layout)
        
        # Add the container to the GlassCardLayout
        self.add_content_widget(content_container)
    
    def create_progress_section(self, parent_layout):
        """Create the progress bar section"""
        # Progress header with title and percentage
        progress_header = QHBoxLayout()
        
        progress_title = QLabel("Processing Data...")
        progress_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #333333;
            background-color: transparent;
        """)
        progress_header.addWidget(progress_title)
        
        progress_header.addStretch()
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #6B4EEB;
            background-color: transparent;
        """)
        progress_header.addWidget(self.percentage_label)
        
        parent_layout.addLayout(progress_header)
        
        # Progress bar
        self.progress_bar = GradientProgressBar()
        self.progress_bar.setValue(0)
        parent_layout.addWidget(self.progress_bar)
    
    def create_progress_details(self, parent_layout):
        """Create the progress details section"""
        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)
        
        # Create detail items
        self.current_step = ProgressDetailItem("Current Step", "Idle")
        self.processed = ProgressDetailItem("Processed", "0 / 0")
        self.elapsed_time = ProgressDetailItem("Elapsed Time", "0m 0s")
        self.estimated_remaining = ProgressDetailItem("Estimated Remaining", "--")
        
        details_layout.addWidget(self.current_step)
        details_layout.addWidget(self.processed)
        details_layout.addWidget(self.elapsed_time)
        details_layout.addWidget(self.estimated_remaining)
        
        parent_layout.addLayout(details_layout)
    
    def create_statistics_cards(self, parent_layout):
        """Create the three summary statistics cards"""
        self.stats_widget = StatisticsSummaryWidget()
        parent_layout.addWidget(self.stats_widget)
    
    def update_progress(self, percentage, current_step=None, processed=None, 
                       elapsed=None, remaining=None):
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
        self.stats_widget.update_statistics(total, success, remaining)
