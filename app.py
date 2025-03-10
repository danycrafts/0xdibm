import os
import sys
import argparse
import tkinter as tk
from src.models.llm_handler import LLMHandler
from src.controllers.settings_controller import SettingsController
from src.controllers.chat_controller import ChatController
import ttkbootstrap as ttk
from PIL import Image, ImageTk 
from config import ConfigManager
from utils.helpers import get_resource_path
from utils.logger import get_logger

logger = get_logger()
# ASSETS_DIR = os.path.join(os.path.dirname(__file__), "resources/assets")

class DESHApplication:
    def __init__(self, config: ConfigManager):
        self.config_manager = config
        self.root = ttk.Window(themename=self.config_manager.get('app_settings','theme'))
        self.root.title("DESH: Data Engineering Staffing Helper")
        self.root.geometry(f"{self.config_manager.get('app_settings','width')}x{self.config_manager.get('app_settings','height')}")
        self.style = ttk.Style()
        self._set_app_icon()
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.llm_handler = LLMHandler(self.config_manager)
        self.chat_controller = ChatController(self.config_manager,self.notebook,self.llm_handler)
        self.settings_controller = SettingsController(self.config_manager,self.notebook,self.apply_appearance,self.llm_handler)
        
    def apply_appearance(self):
        logger.info("Applying appearance settings")
        theme = self.config_manager.get('app_settings','theme')
        font_style = self.config_manager.get('app_settings','font_style')
        font_size = self.config_manager.get('app_settings','font_size')
        width = self.config_manager.get('app_settings','width')
        height = self.config_manager.get('app_settings','height')
        self.style.theme_use(theme)
        self.style.configure('.', font=(font_style, font_size))
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()

    def _set_app_icon(self):
        if sys.platform.startswith("win"):
            if os.path.exists("resources\\assets\\favicon.ico"):
                self.root.iconbitmap("resources\\assets\\favicon.ico")
        else:
            png_icon_path = os.path.join(get_resource_path("resources/assets"), "android-chrome-192x192.png")
            if os.path.exists(png_icon_path):
                img = Image.open(png_icon_path)
                img = img.resize((32, 32), Image.LANCZOS)
                self.tk_icon = ImageTk.PhotoImage(img)
                self.root.iconphoto(False, self.tk_icon)
    
    def run(self):
        logger.info("Application started")
        self.root.mainloop()


def parse_args():
    parser = argparse.ArgumentParser(description="DESH: Data Engineering Staffing Helper")
    app_group = parser.add_argument_group('app_settings')
    app_group.add_argument("--theme", type=str,help="UI theme")
    app_group.add_argument("--font-size", type=int, help="Font size")
    app_group.add_argument("--font-style", help="Font family")
    app_group.add_argument("--width", type=int, help="Window width")
    app_group.add_argument("--height", type=int, help="Window height")
    api_group = parser.add_argument_group('api_config')
    api_group.add_argument("--base-url", help="API base URL")
    api_group.add_argument("--api-key", help="API key")
    api_group.add_argument("--model", help="Model name")
    api_group.add_argument("--temperature", type=float, help="Temperature setting")
    api_group.add_argument("--top-p", type=float, help="Top-p setting")
    api_group.add_argument("--max-tokens", type=int, help="Max tokens")
    api_group.add_argument("--stream", type=bool, help="Stream response")
    args = parser.parse_args()
    args_dict = {
        'app_settings': {},
        'api_config': {}
    }

    for key in ['theme', 'font_size','font_style','width','height']:
        attr_name = key.replace('-', '_')
        if hasattr(args, attr_name) and getattr(args, attr_name) is not None:
            args_dict['app_settings'][key] = getattr(args, attr_name)
    for key in ['base_url', 'api_key', 'model', 'temperature', 'top_p', 'max_tokens', 'stream']:
        attr_name = key.replace('-', '_')
        if hasattr(args, attr_name) and getattr(args, attr_name) is not None:
            args_dict['api_config'][key] = getattr(args, attr_name)

    return args_dict


def main():
    args_dict = parse_args()
    logger.debug(f"CLI args: {args_dict}")
    config_manager = ConfigManager()
    config_manager.apply_cli_args(args_dict)
    logger.info("Initializing Data Engineering Staffing Helper (DESH) application")
    app = DESHApplication(config=config_manager)
    app.run()
    logger.info("DESH terminated")

if __name__ == "__main__":
    main()
