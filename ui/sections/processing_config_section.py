import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QRadioButton, QCheckBox, QButtonGroup, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ui.components.glass_card_layout import GlassCardLayout
from ui.components.drop_down_list import DropDownList
from ui.components.app_button import AppButton
from core.Enums.sort_type import SortType
from core.Enums.grouping_mode import GroupingMode
from PySide6.QtCore import QSize

class ProcessingConfigSection(GlassCardLayout):
    """
    قسم إعدادات المعالجة - يحتوي على قيود القياس، ترتيب التكوين، وخيارات المعالجة.
    """
    # Signals to communicate changes/actions
    start_processing_signal = Signal(dict)
    cancel_signal = Signal()

    def __init__(self, parent=None):
        # SVG icons (placeholders or actual paths if available)
        # Using simple unicode chars or standard icons for now as placeholders in the prompt description
        super().__init__(title="Processing Configuration", icon_svg=None, parent=parent)
        
        self.machine_sizes = []
        self._load_machine_sizes()
        self._setup_panels()
        self._setup_footer()

    def _load_machine_sizes(self):
        """Load machine sizes from config.json"""
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        default_sizes = [
            {"name": "Default 370x400", "min_width": 370, "max_width": 400},
        ]
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.machine_sizes = config.get("machine_sizes", default_sizes)
            else:
                self.machine_sizes = default_sizes
        except Exception as e:
            print(f"Error loading machine sizes: {e}")
            self.machine_sizes = default_sizes

    def _setup_panels(self):
        """Setup the three main panels"""
        # Panel A: Measurement Constraints
        self.panel_a = self._create_panel_a()
        self.add_content_widget(self.panel_a)

        # Panel B: Sort Configuration
        self.panel_b = self._create_panel_b()
        self.add_content_widget(self.panel_b)

        # Panel C: Processing Options
        self.panel_c = self._create_panel_c()
        self.add_content_widget(self.panel_c)

    def _create_panel_style(self, bg_color, accent_color):
        return f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            QLabel {{
                color: #2C3E50;
                font-family: 'Segoe UI', sans-serif;
                background-color: transparent;
                font-size: 13px;
                border: none;
                padding: 0px;
            }}
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid {accent_color};
                border-radius: 8px;
                padding: 10px;
                color: #2C3E50;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #FFFFFF;
            }}
            QRadioButton, QCheckBox {{
                color: #2C3E50;
                font-size: 13px;
                spacing: 8px;
                background-color: transparent;
                font-weight: 500;
            }}
            QRadioButton::indicator, QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {accent_color};
                background-color: rgba(255, 255, 255, 0.9);
            }}
            QRadioButton::indicator:checked {{
                background-color: {accent_color};
                border: 2px solid {accent_color};
            }}
            QCheckBox::indicator {{
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                border: 2px solid {accent_color};
            }}
        """

    def _create_panel_a(self):
        """Panel A: Measurement Constraints (Left)"""
        panel = QFrame()
        panel.setStyleSheet(self._create_panel_style("rgba(138, 180, 248, 0.15)", "#6B9EF5")) # Soft Blue
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)  # Reduced spacing between icon and title
        icon_label = QLabel("📏") # Ruler icon placeholder
        icon_label.setFont(QFont("Segoe UI Emoji", 24, QFont.Bold))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setContentsMargins(0, 0, 0, 0)
        icon_label.setStyleSheet("background-color: transparent; font-size: 22px; padding: 0px; margin: 0px;")
        title_label = QLabel("Measurement Constraints")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50; background-color: transparent;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 0, Qt.AlignLeft)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content
        # Machine Size Dropdown
        label_size = QLabel("Machine Size:")
        label_size.setStyleSheet("color: #2C3E50; background-color: transparent; font-weight: 600;")
        layout.addWidget(label_size)
        
        options = [f"{size['name']} ({size['min_width']}-{size['max_width']})" for size in self.machine_sizes]
        self.size_dropdown = DropDownList(
            selected_value_text="Select Size...",
            options_list=options,
            dropdown_background_color="rgba(255, 255, 255, 0.95)",
            dropdown_border_color="#6B9EF5",
            selected_value_text_color="#2C3E50",
            option_text_color="#2C3E50",
            option_hover_color="rgba(107, 158, 245, 0.2)",
            indicator_icon_color="#6B9EF5",
            custom_height=32
        )
        layout.addWidget(self.size_dropdown)

        # Tolerance Input
        label_tolerance = QLabel("Tolerance:")
        label_tolerance.setStyleSheet("color: #2C3E50; background-color: transparent; font-weight: 600;")
        layout.addWidget(label_tolerance)
        self.tolerance_input = QLineEdit("5")
        self.tolerance_input.setMaximumHeight(30)
        self.tolerance_input.setStyleSheet("padding: none;")
        layout.addWidget(self.tolerance_input)

        layout.addStretch()
        return panel

    def _create_panel_b(self):
        """Panel B: Sort Configuration (Center)"""
        panel = QFrame()
        panel.setStyleSheet(self._create_panel_style("rgba(255, 183, 77, 0.12)", "#FF9800")) # Light Orange
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)  # Reduced spacing between icon and title
        icon_label = QLabel("⇅") # Sort icon placeholder
        icon_label.setFont(QFont("Segoe UI Emoji", 24, QFont.Bold))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setContentsMargins(0, 0, 0, 0)
        icon_label.setStyleSheet("background-color: transparent; font-size: 22px; padding: 0px; margin: 0px;")
        title_label = QLabel("Sort Configuration")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50; background-color: transparent;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 0, Qt.AlignLeft)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content - Radio Group
        self.sort_group = QButtonGroup(self)
        
        self.radio_width = QRadioButton("Width")
        self.radio_quantity = QRadioButton("Quantity")
        self.radio_height = QRadioButton("Height")
        
        self.radio_height.setChecked(True) # Default checked

        self.sort_group.addButton(self.radio_width)
        self.sort_group.addButton(self.radio_quantity)
        self.sort_group.addButton(self.radio_height)

        layout.addWidget(self.radio_width)
        layout.addWidget(self.radio_quantity)
        layout.addWidget(self.radio_height)

        layout.addStretch()
        return panel

    def _create_panel_c(self):
        """Panel C: Processing Options (Right)"""
        panel = QFrame()
        panel.setStyleSheet(self._create_panel_style("rgba(132, 229, 183, 0.15)", "#4ECDC4")) # Soft Teal/Mint
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)  # Reduced spacing between icon and title
        icon_label = QLabel("⚙️") # Gears icon placeholder
        icon_label.setFont(QFont("Segoe UI Emoji", 24, QFont.Bold))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setContentsMargins(0, 0, 0, 0)
        icon_label.setStyleSheet("background-color: transparent; font-size: 22px; padding: 0px; margin: 0px;")
        title_label = QLabel("Processing Options")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50; background-color: transparent;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 0, Qt.AlignLeft)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content - Radio Buttons for Grouping Mode only
        self.grouping_group = QButtonGroup(self)
        
        self.radio_all_combinations = QRadioButton("All Combinations")
        self.radio_all_combinations.setToolTip(GroupingMode.ALL_COMBINATIONS.value)
        
        self.radio_no_main_repeat = QRadioButton("No Main Repeat")
        self.radio_no_main_repeat.setToolTip(GroupingMode.NO_MAIN_REPEAT.value)
        self.radio_no_main_repeat.setChecked(True)  # Default
        
        self.grouping_group.addButton(self.radio_all_combinations)
        self.grouping_group.addButton(self.radio_no_main_repeat)
        
        layout.addWidget(self.radio_all_combinations)
        layout.addWidget(self.radio_no_main_repeat)

        layout.addStretch()
        return panel

    def _setup_footer(self):
        """Setup Action Buttons inside the glass card"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        footer_layout.setContentsMargins(0, 20, 0, 0)
        footer_layout.addStretch()

        # Start Button
        self.start_btn = AppButton(
            text="Start Processing",
            color="#00C853", # Vibrant Emerald Green
            hover_color="#00E676",
            text_color="#FFFFFF",
            fixed_size=QSize(160, 45)
        )
        # Add icon if possible, for now text is fine or unicode
        self.start_btn.setText("▶ Start Processing")
        self.start_btn.clicked.connect(self._on_start_clicked)

        # Cancel Button
        self.cancel_btn = AppButton(
            text="Cancel",
            color="#FF5252", # Soft Red
            hover_color="#FF8A80",
            text_color="#FFFFFF",
            fixed_size=QSize(140, 45)
        )
        self.cancel_btn.setText("⏹ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_signal.emit)

        footer_layout.addWidget(self.start_btn)
        footer_layout.addWidget(self.cancel_btn)
        footer_layout.addStretch()

        # Add buttons to card_layout instead of main_layout
        self.card_layout.addLayout(footer_layout)

    def _on_start_clicked(self):
        """Collect data and emit start signal"""
        # Get Size
        selected_size_text = self.size_dropdown.get_selected_value()
        selected_size = None
        # Parse selected text to find the size object
        # Format: "Name (Min-Max)"
        for size in self.machine_sizes:
            if size['name'] in selected_size_text:
                selected_size = size
                break
        
        if not selected_size:
            # Handle error or default
            pass

        # Get Sort Type
        sort_type = SortType.SORT_BY_HEIGHT # Default
        if self.radio_width.isChecked():
            sort_type = SortType.SORT_BY_WIDTH
        elif self.radio_quantity.isChecked():
            sort_type = SortType.SORT_BY_QUANTITY

        # Get Grouping Mode from radio buttons
        grouping_mode = GroupingMode.NO_MAIN_REPEAT  # Default
        if self.radio_all_combinations.isChecked():
            grouping_mode = GroupingMode.ALL_COMBINATIONS

        data = {
            "machine_size": selected_size,
            "tolerance": self.tolerance_input.text(),
            "sort_type": sort_type,
            "grouping_mode": grouping_mode,
            "generate_report": False  # No report generation option
        }
        self.start_processing_signal.emit(data)

