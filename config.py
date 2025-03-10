import datetime
import json
import os
from utils.logger import get_logger
logger = get_logger()

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = {
            "app_settings": {
                "theme": "pulse",
                "font_size": 9,
                "font_style": "Arial",
                "width": 1000,
                "height": 800
            },
            "api_config": {
                "base_url": "https://integrate.api.nvidia.com/v1",
                "api_key": "",
                "model": "",
                "temperature": 0.5,
                "top_p": 1,
                "max_tokens": 1024,
                "stream": True
            }
        }
        self.last_file_modified_time = 0
        self.create_default_config() # Create default config if it doesn't exist
        self.load_from_file()

    def create_default_config(self):
        if not os.path.exists(self.config_path):
            self.save()
            logger.debug(f"Created default config file at {self.config_path}")
    
    def save(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.last_file_modified_time = os.path.getmtime(self.config_path)
            logger.debug(f"Config updated at {self._normalize_unix_time(self.last_file_modified_time)}!")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")

    def _normalize_unix_time(self, unix_time):
        return datetime.datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

    def load_from_file(self):
        try:
            if os.path.exists(self.config_path):
                current_mod_time = os.path.getmtime(self.config_path)         
                # Only reload if file was modified since last load/save
                if current_mod_time > self.last_file_modified_time:
                    with open(self.config_path, 'r') as f:
                        file_config = json.load(f)
                    # Deep merge the config
                    self._deep_update(self.config, file_config)
                    self.last_file_modified_time = current_mod_time
                    logger.info("Config reloaded from file due to external changes")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def get(self, section, key=None):
        self.load_from_file()  # Check for external file changes
        if section in self.config:
            if key is None:
                return self.config[section]
            elif key in self.config[section]:
                return self.config[section][key]
        return None
    
    def update_from_ui(self, section, key, value):
        if section in self.config and key in self.config[section]:
            self.config[section][key] = value
            self.save()
    
    def apply_cli_args(self, args_dict):
        # Process app_settings args
        if hasattr(args_dict, 'app_settings') and args_dict.app_settings:
            for key, value in args_dict.app_settings.items():
                if value is not None and key in self.config["app_settings"]:
                    self.config["app_settings"][key] = value
        # Process api_config args
        if hasattr(args_dict, 'api_config') and args_dict.api_config:
            for key, value in args_dict.api_config.items():
                if value is not None and key in self.config["api_config"]:
                    self.config["api_config"][key] = value
        self.save()

    def _deep_update(self, target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
