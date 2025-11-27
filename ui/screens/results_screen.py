"""
Results Screen - Displays summary statistics and processing results
Shows after processing completion with detailed view of results
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget
from ui.components.app_button import AppButton


class ResultsScreen(QDialog):
    """Dedicated screen for viewing processing results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
        # Store results data
        self.groups = []
        self.stats = {}
        self.output_path = None
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setWindowTitle("📊 Processing Results")
        self.setMinimumSize(1200, 700)
        self.setModal(False)  # Non-modal so user can interact with main window
        
        # Apply gradient background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E3F2FD, stop:0.5 #BBDEFB, stop:1 #90CAF9);
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header
        header = self._create_header()
        main_layout.addLayout(header)
        
        # Summary Statistics
        self.stats_component = SummaryStatisticsComponent()
        main_layout.addWidget(self.stats_component, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Processing Results Table
        self.results_widget = ProcessingResultsWidget()
        main_layout.addWidget(self.results_widget, 1)
        
        # Footer with close button
        footer = self._create_footer()
        main_layout.addLayout(footer)
    
    def _create_header(self):
        """Create header with title"""
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("📊 Processing Results - Detailed View")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1565C0; background: transparent;")
        
        layout.addWidget(title)
        layout.addStretch()
        
        return layout
    
    def _create_footer(self):
        """Create footer with action buttons"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # Close button
        close_btn = AppButton(
            text="✖️ Close",
            color="#D32F2F",
            hover_color="#F44336",
            text_color="#FFFFFF",
            fixed_size=QSize(130, 40)
        )
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(close_btn)
        
        return layout
    
    def set_results(self, groups, stats, output_path=None):
        """
        Set the results data to display
        
        Args:
            groups: List of group objects
            stats: Dictionary with statistics (total_original, total_used, total_remaining)
            output_path: Path to the output Excel file
        """
        self.groups = groups
        self.stats = stats
        self.output_path = output_path
        
        # Update statistics component
        total_original = stats.get("total_original", 0)
        total_used = stats.get("total_used", 0)
        total_remaining = stats.get("total_remaining", 0)
        
        self.stats_component.update_statistics(
            total=total_original,
            grouped=total_used,
            remaining=total_remaining
        )
        
        # Update results table
        table_data = []
        for g in groups:
            for item in getattr(g, "items", []):
                table_data.append((
                    f"GRP-{getattr(g, 'group_id', '—'):03}",
                    str(getattr(item, "qty_used", 0)),
                    str(getattr(item, "qty_rem", 0)),
                    str(item.length_ref() if hasattr(item, "length_ref") else 0),
                    str(item.summary() if hasattr(item, "summary") else "-"),
                    "Completed"
                ))
        
        self.results_widget.set_data(table_data)
        
        # Set Excel file path if available
        if output_path:
            self.results_widget.set_excel_file_path(output_path)
