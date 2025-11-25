import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QPalette, QLinearGradient, QColor, QBrush
from PySide6.QtCore import Qt
from ui.sections.processing_config_section import ProcessingConfigSection

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Processing Configuration Demo")
    window.resize(1000, 600)
    
    # Create gradient background
    palette = QPalette()
    gradient = QLinearGradient(0, 0, 0, 600)
    gradient.setColorAt(0.0, QColor("#E3F2FD"))  # Light Blue
    gradient.setColorAt(0.5, QColor("#F3E5F5"))  # Light Purple
    gradient.setColorAt(1.0, QColor("#E8F5E9"))  # Light Green
    palette.setBrush(QPalette.Window, QBrush(gradient))
    window.setPalette(palette)
    window.setAutoFillBackground(True)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(20, 20, 20, 20)
    
    # Add the section
    config_section = ProcessingConfigSection()
    layout.addWidget(config_section)
    
    # Connect signals for testing
    config_section.start_processing_signal.connect(lambda data: print(f"Start Processing: {data}"))
    config_section.cancel_signal.connect(lambda: print("Cancel Clicked"))
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
