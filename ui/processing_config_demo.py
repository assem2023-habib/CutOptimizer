import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from ui.sections.processing_config_section import ProcessingConfigSection

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Processing Configuration Demo")
    window.resize(1000, 600)
    window.setStyleSheet("background-color: #F0F0F0;") # Light gray background
    
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
