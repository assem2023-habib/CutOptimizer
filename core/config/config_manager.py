"""
Configuration Manager
Handles loading and saving application configuration
"""
import json
import os


class ConfigManager:
    """Manages application configuration files"""
    
    @staticmethod
    def get_config_path():
        """Returns the path to config.json"""
        return os.path.join(os.getcwd(), "config", "config.json")
    
    @classmethod
    def load_config(cls):
        """Loads and returns the config dictionary"""
        config_path = cls.get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    @classmethod
    def save_config(cls, config):
        """Saves the config dictionary to file"""
        config_path = cls.get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    @classmethod
    def get_value(cls, key, default=None):
        """Gets a specific config value"""
        config = cls.load_config()
        return config.get(key, default)
    
    @classmethod
    def set_value(cls, key, value):
        """Sets a specific config value"""
        config = cls.load_config()
        config[key] = value
        return cls.save_config(config)
    
    @classmethod
    def remove_value(cls, key):
        """Removes a specific config value"""
        config = cls.load_config()
        if key in config:
            del config[key]
            return cls.save_config(config)
        return True
