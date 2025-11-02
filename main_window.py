from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout,QLabel
from PySide6.QtCore import QSize
from ui.components.app_button import AppButton
import qtawesome as qta

from ui.components.app_button import AppButton
from ui.components.toggle_switch import ToggleSwitch
from ui.components.process_summary_card import ProcessSummaryCard
from ui.components.created_groups_table import CreatedGroupsTable
from ui.components.setting_input_field import SettingInputField

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        layout = QVBoxLayout(self)

        self.lable = QLabel("🌞 light day activated")
        self.lable.setStyleSheet("font-size: 16px;")

        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self.on_toggled)

        total_files = ProcessSummaryCard(
            title= "TOTAL FILES",
            main_value= "248",
            progress_percentage= 80,
            card_background= "#FFFFFF",
            main_value_color= "#333333",
            progress_arc_color= "#0078D7"
        )

        success_rate = ProcessSummaryCard(
            title="SUCCESS RATE",
            main_value="98.4%",
            progress_percentage=98,
            card_background="#FFFFFF",
            main_value_color="#28A745",
            progress_arc_color="#28A745",
        )

        failed_files = ProcessSummaryCard(
            title="FAILED FILES",
            main_value="4",
            progress_percentage=10,
            card_background="#FFFFFF",
            main_value_color="#DC3545",
            progress_arc_color="#DC3545",
        )

        import_btn = AppButton(
            text = "Import Excel File",
            color= "#0078D7",
            hover_color= "#3399FF"
        )

        field1 = SettingInputField(label_text="MINIMUM SIZE", input_value="10")
        field2 = SettingInputField(label_text="MAXIMUM SIZE", input_value="500")
        field3 = SettingInputField(label_text="MARGIN", input_value="5")
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

        table = CreatedGroupsTable()

        layout.addWidget(self.lable)
        layout.addWidget(self.toggle)
        layout.addWidget(total_files)
        layout.addWidget(success_rate)
        layout.addWidget(failed_files)
        layout.addWidget(field1)
        layout.addWidget(field2)
        layout.addWidget(field3)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        layout.addWidget(table)
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