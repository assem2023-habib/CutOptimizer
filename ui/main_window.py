"""
Main Window - CutOptimizer Application
Simplified main window using handlers for clean separation of concerns
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QScrollArea, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

# Add parent directory to path for imports
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.sections.file_management_section import FileManagementSection
from ui.sections.processing_config_section import ProcessingConfigSection
from ui.sections.current_operations_section import CurrentOperationsSection
from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget
from ui.widgets.app_button import AppButton
from ui.managers.timer_manager import TimerManager
from ui.handlers.settings_handler import SettingsHandler
from ui.handlers.processing_handler import ProcessingHandler


class MainWindow(QMainWindow):
    """Main application window with clean handler-based architecture"""
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_handlers()
        self._setup_ui()
    
    # ==================== Initialization ====================
    
    def _init_window(self):
        """Initialize window properties"""
        self.setWindowTitle("Complete UI Demo - CutOptimizer")
        self.setGeometry(50, 50, 1600, 900)
        self.setObjectName("MainWindow")
    
    def _init_handlers(self):
        """Initialize handler classes"""
        # Settings handler
        self.settings_handler = SettingsHandler(self)
        self.config = self.settings_handler.load_config()
        self.config_path = self.settings_handler.config_path
        
        # Apply background
        self.settings_handler.apply_background()
        
        # These will be initialized after UI setup
        self.timer_manager = None
        self.processing_handler = None
    
    # ==================== UI Setup ====================
    
    def _setup_ui(self):
        """Setup the main user interface"""
        scroll = self._create_scroll_area()
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        layout.addLayout(self._create_header())
        self._add_sections(layout)
        
        # Initialize handlers that depend on UI components
        self._init_ui_dependent_handlers()
    
    def _create_scroll_area(self):
        """Create and configure scroll area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        return scroll
    
    def _create_header(self):
        """Create header with title and settings button"""
        header_layout = QHBoxLayout()
        
        header_title = QLabel("CutOptimizer Demo")
        header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        settings_btn = AppButton(
            text="⚙️",
            color="transparent",
            hover_color="#0078D7",
            text_color="#333333",
            fixed_size=QSize(40, 32)
        )
        settings_btn.clicked.connect(self.settings_handler.open_settings_dialog)
        header_layout.addWidget(settings_btn)
        
        return header_layout
    
    def _add_sections(self, layout):
        """Add all UI sections to the layout"""
        # 1. File Management Section
        self.file_section = FileManagementSection()
        layout.addWidget(self.file_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 2. Processing Configuration Section
        self.config_section = ProcessingConfigSection()
        layout.addWidget(self.config_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 3. Current Operations Section
        self.operations_section = CurrentOperationsSection()
        self.operations_section.update_progress(0, "Ready", "0/0", "00:00:00", "00:00:00")
        layout.addWidget(self.operations_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 4. Summary Statistics Component
        self.stats_component = SummaryStatisticsComponent()
        layout.addWidget(self.stats_component, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 5. Processing Results Widget
        self.results_widget = ProcessingResultsWidget()
        layout.addWidget(self.results_widget, 1)
    
    def _init_ui_dependent_handlers(self):
        """Initialize handlers that depend on UI components"""
        # Timer manager
        self.timer_manager = TimerManager(self.operations_section)
        
        # Processing handler
        self.processing_handler = ProcessingHandler(self, self.config, self.timer_manager)
        
        # Connect signals
        self.config_section.start_processing_signal.connect(self.processing_handler.start_grouping)
        self.config_section.cancel_signal.connect(self.processing_handler.cancel_operation)
    
    # ==================== Event Handlers ====================
    
    def resizeEvent(self, event):
        """Reapply background when window is resized"""
        self.settings_handler.handle_resize()
        super().resizeEvent(event)
    
    def log_append(self, message):
        """Log message (required by background_utils)"""
        self.settings_handler.log_append(message)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
