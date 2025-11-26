import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.components.combined_components_demo import CombinedDemoWindow

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = CombinedDemoWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()