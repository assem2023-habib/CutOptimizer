from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QSize
from ui.components.app_button import AppButton
import qtawesome as qta

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        layout = QVBoxLayout(self)

        import_btn = AppButton(
            text = "Import Excel File",
            color= "#0078D7",
            hover_color= "#3399FF"
        )
        import_btn.setIcon(qt)