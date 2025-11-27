"""
Settings Handler - Manages application settings and configuration
"""
import os
import json
from PySide6.QtWidgets import QListWidgetItem

from ui.settings_view import SettingsView
from ui.constants.gradients import get_gradient_style
from core.utilies.background_utils import apply_background, apply_default_gradient


class SettingsHandler:
    """Handles settings, configuration, and background management"""
    
    def __init__(self, parent_window):
        """
        Initialize settings handler
        
        Args:
            parent_window: Reference to main window
        """
        self.window = parent_window
        self.config_path = 'config/config.json'
        self.config = {}
        self._suppress_log = False
    
    def load_config(self):
        """Load configuration from config.json"""
        config_path = os.path.join(os.getcwd(), 'config', 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    self.config = cfg
                    return cfg
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}
    
    def apply_background(self):
        """Apply background gradient or image from config"""
        if "background_image" in self.config:
            apply_background(self.window, self.config["background_image"])
        elif "background_gradient" in self.config:
            gradient_index = self.config["background_gradient"]
            gradient_style = get_gradient_style(gradient_index)
            self.window.setStyleSheet(f"#{self.window.objectName()} {{ background: {gradient_style}; }}")
        else:
            apply_default_gradient(self.window)
    
    def handle_resize(self):
        """Handle window resize - reapply background if needed"""
        if "background_image" in self.config:
            self._suppress_log = True
            try:
                apply_background(self.window, self.config["background_image"])
            finally:
                self._suppress_log = False
    
    def log_append(self, message):
        """
        Log message to console (required by background_utils)
        
        Args:
            message: Message to log
        """
        if self._suppress_log and "✅ تم تطبيق الخلفية بنجاح" in message:
            return
        print(message)
    
    def open_settings_dialog(self):
        """Open settings dialog and update UI after changes"""
        settings_dialog = SettingsView(parent=self.window)
        settings_dialog.exec()
        self._update_machine_sizes_dropdown()
    
    def _update_machine_sizes_dropdown(self):
        """Update machine sizes dropdown after settings change"""
        config_section = self.window.config_section
        config_section._load_machine_sizes()
        
        new_options = [
            f"{size['name']} ({size['min_width']}-{size['max_width']})" 
            for size in config_section.machine_sizes
        ]
        
        config_section.size_dropdown.options_list = new_options
        config_section.size_dropdown.list_widget.clear()
        
        for item_text in new_options:
            item = QListWidgetItem(item_text)
            config_section.size_dropdown.list_widget.addItem(item)
