import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui.components.summary_statistics_component import SummaryStatisticsComponent

class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Summary Statistics Component Demo")
        self.resize(1000, 400)
        self.setStyleSheet("background-color: #f0f2f5;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.stats_component = SummaryStatisticsComponent()
        layout.addWidget(self.stats_component)
        
        layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
