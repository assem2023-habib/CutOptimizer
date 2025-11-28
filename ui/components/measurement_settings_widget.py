"""
Measurement Settings Widget
Allows selecting the unit of measurement (m2, m, cm)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, 
                               QButtonGroup, QGroupBox)
from core.config.config_manager import ConfigManager


class MeasurementSettingsWidget(QWidget):
    """Widget for selecting application measurement unit"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self._setup_ui()
        self._load_current_setting()
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group Box
        self.group_box = QGroupBox("📏 وحدة القياس")
        group_layout = QHBoxLayout()
        group_layout.setSpacing(20)
        
        # Radio Buttons
        self.radio_m2 = QRadioButton("متر مربع (m²)")
        self.radio_m = QRadioButton("متر طولي (m)")
        self.radio_cm = QRadioButton("سنتيمتر (cm)")
        
        # Button Group
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.radio_m2, 1)
        self.button_group.addButton(self.radio_m, 2)
        self.button_group.addButton(self.radio_cm, 3)
        
        # Connect signal
        self.button_group.buttonClicked.connect(self._on_unit_changed)
        
        # Add to layout
        group_layout.addWidget(self.radio_m2)
        group_layout.addWidget(self.radio_m)
        group_layout.addWidget(self.radio_cm)
        group_layout.addStretch()
        
        self.group_box.setLayout(group_layout)
        layout.addWidget(self.group_box)
        
    def _load_current_setting(self):
        """Load current unit from config"""
        unit = ConfigManager.get_value("measurement_unit", "cm")
        
        if unit == "m2":
            self.radio_m2.setChecked(True)
        elif unit == "m":
            self.radio_m.setChecked(True)
        else:
            self.radio_cm.setChecked(True)
            
    def _on_unit_changed(self, button):
        """Handle unit change"""
        unit = "cm"
        if button == self.radio_m2:
            unit = "m2"
        elif button == self.radio_m:
            unit = "m"
            
        # Update config
        ConfigManager.set_value("measurement_unit", unit)
