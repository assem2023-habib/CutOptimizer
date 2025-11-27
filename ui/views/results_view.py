"""
Results View - Displays processing results and statistics
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont
from ui.components.app_button import AppButton
from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget


class ResultsView(QWidget):
    """Dedicated view for displaying processing results"""
    
    # Signal for back button
    back_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with back button
        header = self._create_header()
        layout.addLayout(header)
        
        # Title
        title = QLabel("📊 نتائج المعالجة")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #00FF91; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Summary statistics
        self.summary_stats = SummaryStatisticsComponent()
        layout.addWidget(self.summary_stats)
        
        # Processing results table
        self.results_table = ProcessingResultsWidget()
        layout.addWidget(self.results_table)
    
    def _create_header(self):
        """Creates the header with back button"""
        header_layout = QHBoxLayout()
        
        back_btn = AppButton(
            text="⬅ رجوع",
            color="#1976D2",
            hover_color="#2196F3",
            text_color="#FFFFFF",
            fixed_size=QSize(120, 40)
        )
        back_btn.clicked.connect(self.back_clicked.emit)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        
        return header_layout
    
    def update_results(self, total, successfully_grouped, remaining, output_path):
        """Updates the results with processing data"""
        # Update statistics
        self.summary_stats.update_statistics(
            total=total,
            successfully_grouped=successfully_grouped,
            remaining=remaining
        )
        
        # Set excel file path for the read button
        if output_path:
            self.results_table.set_excel_file_path(output_path)
