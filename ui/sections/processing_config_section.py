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

    def _create_panel_style(self, bg_color):
        return f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: #333333;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                color: #333333;
            }}
            QRadioButton, QCheckBox {{
                color: #333333;
                font-size: 13px;
                spacing: 8px;
            }}
        """

    def _create_panel_a(self):
        """Panel A: Measurement Constraints (Left)"""
        panel = QFrame()
        panel.setStyleSheet(self._create_panel_style("#F3F6FF")) # Light Lavender
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("📏") # Ruler icon placeholder
        icon_label.setFont(QFont("Segoe UI", 14))
        title_label = QLabel("Measurement Constraints")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content
        # Machine Size Dropdown
        layout.addWidget(QLabel("Machine Size:"))
        
        options = [f"{size['name']} ({size['min_width']}-{size['max_width']})" for size in self.machine_sizes]
        self.size_dropdown = DropDownList(
            selected_value_text="Select Size...",
            options_list=options,
            dropdown_background_color="#FFFFFF",
            dropdown_border_color="#E0E0E0",
            selected_value_text_color="#333333",
            option_text_color="#333333",
            option_hover_color="#F0F0F0",
            indicator_icon_color="#666666"
        )
        layout.addWidget(self.size_dropdown)

        # Tolerance Input
        layout.addWidget(QLabel("Tolerance:"))
        self.tolerance_input = QLineEdit("5")
        layout.addWidget(self.tolerance_input)

        layout.addStretch()
        return panel

    def _create_panel_b(self):
        """Panel B: Sort Configuration (Center)"""
        panel = QFrame()
        panel.setStyleSheet(self._create_panel_style("#FFF5F8")) # Light Pale Pink
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("⇅") # Sort icon placeholder
        icon_label.setFont(QFont("Segoe UI", 14))
        title_label = QLabel("Sort Configuration")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
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
        panel.setStyleSheet(self._create_panel_style("#F0FFF4")) # Light Mint Green
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("⚙️") # Gears icon placeholder
        icon_label.setFont(QFont("Segoe UI", 14))
        title_label = QLabel("Processing Options")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content - Checkboxes
        # Advanced Grouping (Maps to GroupingMode)
        self.check_advanced = QCheckBox("Advanced Grouping")
        self.check_advanced.setToolTip("Checked: All Combinations, Unchecked: No Main Repeat")
        
        # Optimize Results (Visual only as per prompt, or maybe logic?)
        # Prompt said: "Optimize Results" (Checked) - Show a checkmark in the box.
        # But user update said: "Implement a single Checkbox for 'Advanced Grouping'... Checked: Maps to GroupingMode.ALL_COMBINATIONS..."
        # I will keep 'Optimize Results' as a visual element if needed, but the logic focus is on Advanced Grouping.
        # Actually, the user update replaced the previous list. I will follow the user update strictly for the logic, 
        # but I'll add 'Generate Report' as requested.
        
        self.check_report = QCheckBox("Generate Report")

        layout.addWidget(self.check_advanced)
        layout.addWidget(self.check_report)

        layout.addStretch()
        return panel

    def _setup_footer(self):
        """Setup Action Buttons"""
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

        self.main_layout.addLayout(footer_layout)

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

        # Get Grouping Mode
        grouping_mode = GroupingMode.NO_MAIN_REPEAT
        if self.check_advanced.isChecked():
            grouping_mode = GroupingMode.ALL_COMBINATIONS

        data = {
            "machine_size": selected_size,
            "tolerance": self.tolerance_input.text(),
            "sort_type": sort_type,
            "grouping_mode": grouping_mode,
            "generate_report": self.check_report.isChecked()
        }
        self.start_processing_signal.emit(data)

