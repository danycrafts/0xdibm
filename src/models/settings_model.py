from config import ConfigManager

class SettingsModel:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def get_api_config(self):
        return {
            "base_url": self.config_manager.get("api_config", "base_url"),
            "api_key": self.config_manager.get("api_config", "api_key"),
            "model": self.config_manager.get("api_config", "model"),
            "temperature": self.config_manager.get("api_config", "temperature"),
            "top_p": self.config_manager.get("api_config", "top_p"),
            "max_tokens": self.config_manager.get("api_config", "max_tokens"),
            "stream": self.config_manager.get("api_config", "stream"),
        }

    def get_app_settings(self):
        return {
            "theme": self.config_manager.get("app_settings", "theme"),
            "font_size_sm": self.config_manager.get("app_settings", "font_size"),
            "font_style": self.config_manager.get("app_settings", "font_style"),
            "font_color": self.config_manager.get("app_settings", "font_color"),
            "width": self.config_manager.get("app_settings", "width"),
            "height": self.config_manager.get("app_settings", "height"),
        }
