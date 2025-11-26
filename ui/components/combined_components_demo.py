"""
Combined Components Demo - Final Version
Complete UI with all components in the requested order
Using ProcessingConfigSection instead of MeasurementSettingsSection
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.sections.file_management_section import FileManagementSection
from ui.sections.processing_config_section import ProcessingConfigSection
from ui.sections.current_operations_section import CurrentOperationsSection
from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget


class CombinedDemoWindow(QMainWindow):
    """Demo window showcasing all components in the requested order"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Complete UI Demo - CutOptimizer")
        self.setGeometry(50, 50, 1600, 900)
        
        # Set diagonal gradient from white to sky blue
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF,
                    stop:0.3 #F8FCFF,
                    stop:0.6 #EFF8FF,
                    stop:1 #D4EDFF
                );
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Central widget
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # 1. File Management Section (Excel Input) - First
        file_section = FileManagementSection()
        layout.addWidget(file_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 2. Processing Configuration Section (Settings/Input) - Second
        config_section = ProcessingConfigSection()
        layout.addWidget(config_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 3. Current Operations Section (الخط) - Third
        operations_section = CurrentOperationsSection()
        operations_section.update_progress(
            percentage=65,
            current_step="Processing Group 4",
            processed="12/25",
            elapsed="00:02:30",
            remaining="00:01:45"
        )
        layout.addWidget(operations_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 4. Summary Statistics Component (الإحصاءات) - Fourth
        stats_component = SummaryStatisticsComponent()
        layout.addWidget(stats_component, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 5. Processing Results Widget (الجدول) - Last
        results_widget = ProcessingResultsWidget()
        layout.addWidget(results_widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Add stretch to push everything to top
        layout.addStretch()


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    from PySide6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))
    
    window = CombinedDemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
