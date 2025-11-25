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
        
        # تخزين المقاس الحالي
        self.current_min_width = 370
        self.current_max_width = 400

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
        title_layout.addWidget(self.mode_dropdown)
        title_layout.addWidget(self.sort_dropdown)

        main_layout.addLayout(title_layout)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(30)

        # قائمة منسدلة لاختيار المقاس
        self.size_dropdown = DropDownList(
            selected_value_text="اختر المقاس",
            options_list=self._load_machine_sizes_list()
        )
        self.size_dropdown.setFixedWidth(200)
        self.size_dropdown.list_widget.itemClicked.connect(
            lambda _: self._on_size_changed()
        )
        
        # تسميات لعرض القيم الحالية
        self.min_label = QLabel("Min: ---")
        self.min_label.setFont(QFont("Segoe UI", 10))
        self.min_label.setStyleSheet("color: #FFFFFF; background-color: #2D2D2D; padding: 8px; border-radius: 4px;")
        self.min_label.setAlignment(Qt.AlignCenter)
        self.min_label.setFixedWidth(120)
        
        self.max_label = QLabel("Max: ---")
        self.max_label.setFont(QFont("Segoe UI", 10))
        self.max_label.setStyleSheet("color: #FFFFFF; background-color: #2D2D2D; padding: 8px; border-radius: 4px;")
        self.max_label.setAlignment(Qt.AlignCenter)
        self.max_label.setFixedWidth(120)

        self.margin_input = SettingInputField(
            label_text="Tolerance",
            input_value=100,
            is_enabled=self.is_inputs_enabled
        )
        
        # ترتيب العناصر
        size_container = QVBoxLayout()
        size_label = QLabel("Machine Size")
        size_label.setFont(QFont("Segoe UI", 9))
        size_label.setStyleSheet("color: #A0A0A0;")
        size_container.addWidget(size_label)
        size_container.addWidget(self.size_dropdown)
        
        min_container = QVBoxLayout()
        min_title = QLabel("Min Width")
        min_title.setFont(QFont("Segoe UI", 9))
        min_title.setStyleSheet("color: #A0A0A0;")
        min_container.addWidget(min_title)
        min_container.addWidget(self.min_label)
        
        max_container = QVBoxLayout()
        max_title = QLabel("Max Width")
        max_title.setFont(QFont("Segoe UI", 9))
        max_title.setStyleSheet("color: #A0A0A0;")
        max_container.addWidget(max_title)
        max_container.addWidget(self.max_label)
        
        fields_layout.addLayout(size_container)
        fields_layout.addLayout(min_container)
        fields_layout.addLayout(max_container)
        fields_layout.addWidget(self.margin_input, stretch=1)
        
        # تحميل المقاس المحفوظ
        self._load_saved_size()

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

    def _load_machine_sizes_list(self):
        """تحميل قائمة أسماء المقاسات"""
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        default_sizes = [
            {"name": "370x400", "min_width": 370, "max_width": 400},
            {"name": "470x500", "min_width": 470, "max_width": 500}
        ]
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                sizes = config.get("machine_sizes", default_sizes)
            else:
                sizes = default_sizes
        except:
            sizes = default_sizes
        
        return [size["name"] for size in sizes]
    
    def _on_size_changed(self):
        """عند تغيير المقاس المختار"""
        selected_name = self.size_dropdown.get_selected_value()
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                sizes = config.get("machine_sizes", [])
                
                # البحث عن المقاس المختار
                for size in sizes:
                    if size["name"] == selected_name:
                        self.current_min_width = size["min_width"]
                        self.current_max_width = size["max_width"]
                        self.min_label.setText(f"Min: {self.current_min_width}")
                        self.max_label.setText(f"Max: {self.current_max_width}")
                        
                        # حفظ المقاس المختار
                        config["selected_machine_size"] = selected_name
                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(config, f, ensure_ascii=False, indent=4)
                        break
        except Exception as e:
            print(f"خطأ في تحميل المقاس: {e}")
    
    def _load_saved_size(self):
        """تحميل المقاس المحفوظ"""
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                saved_size_name = config.get("selected_machine_size")
                sizes = config.get("machine_sizes", [])
                
                if saved_size_name:
                    for size in sizes:
                        if size["name"] == saved_size_name:
                            self.size_dropdown.selected_value_text = saved_size_name
                            self.size_dropdown.selector_btn.setText(saved_size_name)
                            self.current_min_width = size["min_width"]
                            self.current_max_width = size["max_width"]
                            self.min_label.setText(f"Min: {self.current_min_width}")
                            self.max_label.setText(f"Max: {self.current_max_width}")
                            return
                
                # إذا لم يكن هناك مقاس محفوظ، استخدم الأول
                if sizes:
                    first_size = sizes[0]
                    self.size_dropdown.selected_value_text = first_size["name"]
                    self.size_dropdown.selector_btn.setText(first_size["name"])
                    self.current_min_width = first_size["min_width"]
                    self.current_max_width = first_size["max_width"]
                    self.min_label.setText(f"Min: {self.current_min_width}")
                    self.max_label.setText(f"Max: {self.current_max_width}")
        except Exception as e:
            print(f"خطأ في تحميل المقاس المحفوظ: {e}")

    def _apply_styles(self):
        qss_path = os.path.join(os.path.dirname(__file__), "../styles/style.qss")
        qss_path = os.path.abspath(qss_path)

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"⚠️ ملف التنسيقات غير موجود: {qss_path}")

    def set_inputs_enabled(self, enabled: bool):
        self.margin_input.input.setEnabled(enabled)
        self.mode_dropdown.setDisabled(not enabled)
        self.size_dropdown.setDisabled(not enabled)
        
    def get_min_width(self) -> int:
        """الحصول على العرض الأدنى من المقاس المختار"""
        return self.current_min_width
    
    def get_max_width(self) -> int:
        """الحصول على العرض الأعلى من المقاس المختار"""
        return self.current_max_width
        
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

    def get_selected_sort(self) -> str:
        return self.sort_dropdown.selected_value_text