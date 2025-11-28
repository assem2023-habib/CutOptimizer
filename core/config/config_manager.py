"""
Configuration Manager
Handles loading and saving application configuration
"""
import json
from PySide6.QtCore import QSettings

class ConfigManager:
    """Manages application configuration using QSettings (Registry/Internal Storage)"""
    
    @staticmethod
    def _get_settings():
        return QSettings("CutOptimizer", "CutOptimizer")
    
    @classmethod
    def get_value(cls, key, default=None):
        """Gets a specific config value"""
        settings = cls._get_settings()
        val = settings.value(key, default)
        
        # Handle potential JSON strings for complex objects
        if isinstance(val, str):
            try:
                # Try to decode if it looks like a list or dict
                if val.strip().startswith(('[', '{')):
                    return json.loads(val)
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # QSettings might return 'true'/'false' strings for booleans sometimes, 
        # but PySide6 usually handles types well. 
        # However, if we stored a complex object as JSON, we just returned it above.
        return val
    
    @classmethod
    def set_value(cls, key, value):
        """Sets a specific config value"""
        settings = cls._get_settings()
        
        # Serialize complex objects to JSON string
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
            
        settings.setValue(key, value)
        return True
    
    @classmethod
    def remove_value(cls, key):
        """Removes a specific config value"""
        settings = cls._get_settings()
        settings.remove(key)
        return True
