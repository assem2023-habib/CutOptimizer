"""
Settings Handler - Manages application settings and configuration
"""
from PySide6.QtWidgets import QListWidgetItem

from ui.settings_view import SettingsView
from ui.constants.gradients import get_gradient_style
from core.utilies.background_utils import apply_background, apply_default_gradient
from core.config.config_manager import ConfigManager


class SettingsHandler:
    """Handles settings, configuration, and background management"""
    
    def __init__(self, parent_window):
        """
        Initialize settings handler
        
        Args:
            parent_window: Reference to main window
        """
        self.window = parent_window
        self._suppress_log = False
    
    def load_config(self):
        """Load configuration (Compatibility method)"""
        # No longer needed to load from file, but keeping method signature if used elsewhere
        return {}
    
    def apply_background(self):
        """Apply background gradient or image from config"""
        bg_image = ConfigManager.get_value("background_image")
        bg_gradient = ConfigManager.get_value("background_gradient")
        
        if bg_image:
            apply_background(self.window, bg_image)
        elif bg_gradient is not None:
            try:
                gradient_index = int(bg_gradient)
                gradient_style = get_gradient_style(gradient_index)
                self.window.setStyleSheet(f"#{self.window.objectName()} {{ background: {gradient_style}; }}")
            except (ValueError, TypeError):
                apply_default_gradient(self.window)
        else:
            apply_default_gradient(self.window)
    
    def handle_resize(self):
        """Handle window resize - reapply background if needed"""
        bg_image = ConfigManager.get_value("background_image")
        if bg_image:
            self._suppress_log = True
            try:
                apply_background(self.window, bg_image)
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
        if not hasattr(self.window, 'config_section'):
            return

        config_section = self.window.config_section
        # Assuming config_section has a method to reload or we trigger it
        if hasattr(config_section, '_load_machine_sizes'):
            config_section._load_machine_sizes()
        
        # If config_section.machine_sizes is updated by _load_machine_sizes, we use it
        # Otherwise we might need to fetch from ConfigManager directly
        machine_sizes = ConfigManager.get_value("machine_sizes", [])
        
        if not machine_sizes:
             return

        new_options = [
            f"{size['name']} ({size['min_width']}-{size['max_width']})" 
            for size in machine_sizes
        ]
        
        if hasattr(config_section, 'size_dropdown'):
            config_section.size_dropdown.options_list = new_options
            config_section.size_dropdown.list_widget.clear()
            
            for item_text in new_options:
                item = QListWidgetItem(item_text)
                config_section.size_dropdown.list_widget.addItem(item)
