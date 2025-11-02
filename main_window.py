from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout,QLabel
from PySide6.QtCore import QSize
from ui.components.app_button import AppButton
import qtawesome as qta

from ui.components.app_button import AppButton
from ui.components.toggle_switch import ToggleSwitch

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        layout = QVBoxLayout(self)

        self.lable = QLabel("🌞 light day activated")
        self.lable.setStyleSheet("font-size: 16px;")

        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self.on_toggled)

        import_btn = AppButton(
            text = "Import Excel File",
            color= "#0078D7",
            hover_color= "#3399FF"
        )
        import_btn.setIcon(qta.icon("fa5s.cloud-download-alt", color="white"))
        import_btn.clicked.connect(self.import_file_action)

        export_btn = AppButton(
            text = "Export File",
            color = "#0078D7",
            hover_color= "#3399FF",
        )
        export_btn.setIcon(qta.icon("fa5s.cloud-upload-alt", color= "white"))
        export_btn.clicked.connect(self.export_file_action)

        start_btn = AppButton(
            text = "Start",
            color = "#28A745",
            hover_color = "#3ED15F",
        )
        start_btn.setIcon(qta.icon("fa5s.play", color="white"))
        start_btn.clicked.connect(self.start_action)

        stop_btn = AppButton(
            text = "Stop",
            color = "#DC3545",
            hover_color= "#FF5A6A",
        )
        stop_btn = AppButton(
            text= "Stop",
            color = "#DC3545",
            hover_color= "#FF5A6A",
        )
        stop_btn.setIcon(qta.icon('fa5s.stop', color= "white"))
        stop_btn.clicked.connect(self.stop_action)

        layout.addWidget(self.lable)
        layout.addWidget(self.toggle)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        layout.addStretch()
    def import_file_action(self):
        print("Import File Action")
    def export_file_action(self):
        print("Export File Action")
    def start_action(self):
        print("Start Action")
    def stop_action(self):
        print("Stop Action")
    def on_toggled(self, checked):
        if checked:
            self.lable.setText("🌙 night mode activated")
            self.setStyleSheet("background-color: #1E1E1E; color: white;")

        else:
            self.lable.setText("🌞 light mode")
            self.setStyleSheet("background-color:white; color: black;")

if __name__ == "__main__":
    import sys
    app = QApplication([])
    window = MainWindow()
    window.resize(320, 400)
    window.show()
    sys.exit(app.exec())