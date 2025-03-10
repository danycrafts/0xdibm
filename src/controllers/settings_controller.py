from src.models.settings_model import SettingsModel
from src.views.settings_view import SettingsView
from src.models.llm_handler import LLMHandler
from config import ConfigManager
from utils.logger import get_logger
import tkinter.messagebox as messagebox
import ttkbootstrap as ttk

logger = get_logger()

class SettingsController:
    def __init__(self, config_manager: ConfigManager,notebook: ttk.Notebook,apply_changes,llm_handler:LLMHandler):
        self.config_manager = config_manager
        self.notebook = notebook
        self.llm_handler = llm_handler

        self.model = SettingsModel(self.config_manager)
        self.view = SettingsView(notebook,self.config_manager,save_callback=self.save_settings,reload_model_callback=self.llm_handler.run_init_prompt)
        self.apply_changes = apply_changes
        self._load_initial_settings()

    def _load_initial_settings(self):
        api_config = self.model.get_api_config()
        self.view.base_url_var.set(api_config.get("base_url", ""))
        self.view.api_key_var.set(api_config.get("api_key", ""))
        self.view.model_var.set(api_config.get("model", ""))
        self.view.temperature_var.set(api_config.get("temperature", 0.5))
        self.view.top_p_var.set(api_config.get("top_p", 1.0))
        self.view.max_tokens_var.set(api_config.get("max_tokens", 1024))
        self.view.stream_var.set(api_config.get("stream", True))

        app_settings = self.model.get_app_settings()
        self.view.theme_var.set(app_settings.get("theme", "pulse"))
        self.view.font_size_var.set(app_settings.get("font_size", 10))
        self.view.font_style_var.set(app_settings.get("font_style", "Arial"))
        self.view.width_var.set(app_settings.get("width", 1000))
        self.view.height_var.set(app_settings.get("height", 800))

    def save_settings(self):
        try:
            # Prepare the configuration data
            api_config = {
                "base_url": self.view.base_url_var.get(),
                "api_key": self.view.api_key_var.get(),
                "model": self.view.model_var.get(),
                "temperature": self.view.temperature_var.get(),
                "top_p": self.view.top_p_var.get(),
                "max_tokens": self.view.max_tokens_var.get(),
                "stream": self.view.stream_var.get(),
            }

            app_settings = {
                "theme": self.view.theme_var.get(),
                "font_size": self.view.font_size_var.get(),
                "font_style": self.view.font_style_var.get(),
                "width": self.view.width_var.get(),
                "height": self.view.height_var.get(),
            }
            
            # Update the configuration using update_from_ui method
            for key, value in api_config.items():
                self.config_manager.update_from_ui("api_config", key, value)
                
            for key, value in app_settings.items():
                self.config_manager.update_from_ui("app_settings", key, value)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.apply_changes()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", str(e))

    def _apply_theme(self, theme_name,font_style,font_size):
        try:
            style = ttk.Style()
            style.theme_use(theme_name)
            style.configure('.', font=(font_style, font_size))
            self.notebook.update_idletasks()
        except Exception as e:
            logger.error(f"Theme error: {e}")
            messagebox.showerror("Theme Error", str(e))
