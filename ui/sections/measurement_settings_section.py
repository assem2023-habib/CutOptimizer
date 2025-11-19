from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGraphicsBlurEffect,  
                               QGraphicsDropShadowEffect)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

from ui.components.setting_input_field import SettingInputField 
from ui.components.drop_down_list import DropDownList
from core.Enums.grouping_mode import GroupingMode
from core.Enums.sort_type import SortType

import os, json

class MeasurementSettingsSection(QWidget):
    def __init__(self,
                 section_title_text: str = "MEASUREMENT SETTINGS",
                 section_background_color: str = "#F8F9FA",
                 section_title_text_color: str = "#A0A0A0",
                 is_inputs_enabled: bool = True,
                 parent = None
                 ):
        super().__init__(parent)

        self.section_title_text = section_title_text
        self.section_background_color = section_background_color
        self.section_title_text_color = section_title_text_color
        self.is_inputs_enabled = is_inputs_enabled

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(18)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(15)

        title_label = QLabel(self.section_title_text)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.section_title_text_color};")
        title_label.setAlignment(Qt.AlignLeft)

        self.mode_dropdown= DropDownList(
            selected_value_text="Default Mod",
            options_list=GroupingMode.list(),
        )
        self.mode_dropdown.setFixedWidth(200)

        self.sort_dropdown = DropDownList(
            selected_value_text="Ascending",
            options_list=SortType.list()
        )
        self.sort_dropdown.setFixedWidth(160)

        self.load_saved_mode()
        self.load_saved_sort()

        self.mode_dropdown.list_widget.itemClicked.connect(
            lambda _: self.save_selected_mode()
        )
        self.sort_dropdown.list_widget.itemClicked.connect(
            lambda _: self.save_selected_sort()
            )

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        # title_layout.addWidget(self.mode_dropdown, alignment=Qt.AlignLeft)
        title_layout.addWidget(self.mode_dropdown)
        title_layout.addWidget(self.sort_dropdown)

        main_layout.addLayout(title_layout)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(30)

        self.min_input = SettingInputField(
            label_text="Minimum Width",
            input_value=370,
            is_enabled= self.is_inputs_enabled
        )

        self.max_input = SettingInputField(
            label_text="Maximum Width",
            input_value= 400,
            is_enabled= self.is_inputs_enabled
        )

        self.margin_input = SettingInputField(
            label_text="Tolerance",
            input_value= 100,
            is_enabled=self.is_inputs_enabled
        )
        
        for widget in [self.min_input, self.max_input, self.margin_input]:
            fields_layout.addWidget(widget, stretch=1)

        main_layout.addLayout(fields_layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(12)
        self.setGraphicsEffect(blur)

    def _apply_styles(self):
        qss_path = os.path.join(os.path.dirname(__file__), "../styles/style.qss")
        qss_path = os.path.abspath(qss_path)

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"⚠️ ملف التنسيقات غير موجود: {qss_path}")

    def set_inputs_enabled(self, enabled: bool):
        self.min_input.input.setEnabled(enabled)
        self.max_input.input.setEnabled(enabled)
        self.margin_input.input.setEnabled(enabled)
        self.mode_dropdown.setDisabled(not enabled)
        
    def load_saved_mode(self):
        config_file_path= os.path.join(os.getcwd(), "config", "config.json")
        if not os.path.exists(config_file_path):
            return
        
        try:
            with open(config_file_path, "r", encoding="utf-8") as f:
                cfg= json.load(f)
            saved_mode= cfg.get("selected_mode")
            if saved_mode and saved_mode in self.mode_dropdown.options_list:
                self.mode_dropdown.selected_value_text = saved_mode
                self.mode_dropdown.selector_btn.setText(saved_mode)
        except Exception as e:
            raise e
        
    def save_selected_mode(self):
        try:
            config_file_path = os.path.join(os.getcwd(), "config", "config.json")
            mode = self.mode_dropdown.get_selected_value()

            if os.path.exists(config_file_path):
                with open(config_file_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            else:
                cfg = {}

            cfg["selected_mode"] = mode
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise e

    def get_selected_mode(self) -> str:
        return self.mode_dropdown.selected_value_text
    
    def load_saved_sort(self):
        config_file_path = os.path.join(os.getcwd(), "config", "config.json")
        if not os.path.exists(config_file_path):
            return

        try:
            with open(config_file_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            saved_sort = cfg.get("selected_sort_type")
            if saved_sort and saved_sort in self.sort_dropdown.options_list:
                self.sort_dropdown.selected_value_text = saved_sort
                self.sort_dropdown.selector_btn.setText(saved_sort)
        except Exception as e:
            raise e

    def save_selected_sort(self):
        try:
            config_file_path = os.path.join(os.getcwd(), "config", "config.json")
            sort_type = self.sort_dropdown.get_selected_value()

            if os.path.exists(config_file_path):
                with open(config_file_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            else:
                cfg = {}

            cfg["selected_sort_type"] = sort_type
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise e

    def get_selected_mode(self) -> str:
        return self.mode_dropdown.selected_value_text

    def get_selected_sort(self) -> str:
        return self.sort_dropdown.selected_value_text