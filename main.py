import sys
from PySide6.QtWidgets import QApplication
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()