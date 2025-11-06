import json
import traceback
import sys, os
import copy
import subprocess
import platform
from PySide6.QtWidgets import (QWidget,QApplication,QLineEdit, QPushButton, QVBoxLayout
                               , QFileDialog, QLabel, QLineEdit,
                                 QTextEdit, QHBoxLayout, QMessageBox, 
                                 QTableWidget, QTableWidgetItem, 
                                 QProgressBar, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QIntValidator
from data_io.excel_io import read_input_excel, write_output_excel
from core.grouping_algorithm import build_groups
from core.validation import validate_config, validate_carpets
from .ui_utils import ( setup_button_animations,
                       _create_section_card)
from ui.components.top_button_section import TopButtonSection
from core.actions.file_actions import (
    browse_input_lineedit,
    browse_output_lineedit,
    open_excel_file
)
from ui.components.measurement_settings_section import MeasurementSettingsSection

class RectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("تجميع السجاد - نظام محسن")

        self.config_path = config_path

        self.is_running = False
        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit()

        # إنشاء منطقة التمرير للمحتوى الرئيسي
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        content_widget = QWidget()

        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        title_label = QLabel("🏠 تجميع السجاد")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)

        self.top_button_section = TopButtonSection(
            on_import_clicked= self.browse_input,
            on_export_clicked= self.browse_output
        )
        self.measurement_section = MeasurementSettingsSection()
        content_layout.addWidget(self.top_button_section)
        content_layout.addWidget(self.measurement_section)
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)


    def browse_input(self):
        browse_input_lineedit(
            self.top_button_section.input_edit,
            self.top_button_section.output_edit
        )

    def browse_output(self):
        browse_output_lineedit(self.top_button_section.output_edit)

    def open_excel_file(self):
        output_path = self.top_button_section.output_edit.text().strip()
        open_excel_file(output_path, getattr(self, "log_append", None))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RectPackApp()
    window.show()
    sys.exit(app.exec())
    