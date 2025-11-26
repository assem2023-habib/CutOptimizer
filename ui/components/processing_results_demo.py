"""
Demo application for Processing Results Widget
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.components.processing_results_widget import ProcessingResultsWidget


class DemoWindow(QMainWindow):
    """Demo window to showcase the Processing Results widget"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processing Results Demo")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set background with gradient
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF,
                    stop:1 #E3F2FD
                );
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Add the Processing Results widget
        results_widget = ProcessingResultsWidget()
        layout.addWidget(results_widget)
        
        # Add stretch to keep widget at top
        layout.addStretch()


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    app.setFont(app.font())
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
