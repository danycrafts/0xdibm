import tkinter as tk
import ttkbootstrap as ttk
from config import ConfigManager
from utils.helpers import get_system_info,fetch_models
from utils.logger import get_logger

logger = get_logger()
class SettingsView:
    def __init__(self, notebook: ttk.Notebook, config_manager: ConfigManager,save_callback,reload_model_callback):
        self.notebook = notebook
        self.config_manager = config_manager

        self.base_url_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.show_api_key_var = tk.BooleanVar(value=False)

        self.model_var = tk.StringVar()
        self.temperature_var = tk.DoubleVar()
        self.top_p_var = tk.DoubleVar()
        self.max_tokens_var = tk.IntVar()
        self.stream_var = tk.BooleanVar()

        self.theme_var = tk.StringVar()
        self.font_size_var = tk.IntVar()
        self.font_style_var = tk.StringVar()
        self.width_var = tk.IntVar()
        self.height_var = tk.IntVar()
        self.models_dropdown= ttk.Combobox()

        self.themes = ['flatly', 'cosmo', 'darkly', 'litera', 'lumen', 'minty', 'pulse', 'sandstone', 'united']
        self.font_styles = ['Arial', 'Courier', 'Comic Sans MS', 'Fixedsys', 'MS Sans Serif', 'MS Serif', 'Symbol', 'System', 'Times New Roman', 'Verdana']
        self.save_action = save_callback
        self.reload_model = reload_model_callback
        self._create_ui()

    def toggle_api_key_visibility(self):
        if self.show_api_key_var.get():
            self.api_key_entry.config(show='')
        else:
            self.api_key_entry.config(show='*')

    def _create_ui(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        def update_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.configure(width=frame.winfo_width())
        
        scrollable_frame.bind("<Configure>", update_canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(width=frame.winfo_width()))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        api_frame = ttk.Frame(scrollable_frame)
        api_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.create_api_config_section(api_frame)
        model_frame = ttk.Frame(scrollable_frame)
        model_frame.grid(row=0,column=1,padx=10, pady=10, sticky="nsew")
        self.create_model_config_section(model_frame)
        app_frame = ttk.Frame(scrollable_frame)
        app_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.create_app_settings_section(app_frame)
        sys_info_frame = ttk.Frame(scrollable_frame)
        sys_info_frame.grid(row=1, column=1, columnspan=1, padx=10, pady=10, sticky="nsew")
        self.create_system_info_section(sys_info_frame)
        save_btn = ttk.Button(scrollable_frame, text="Save Settings", command=self.save_action)
        save_btn.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_api_config_section(self, frame):
        api_frame = ttk.LabelFrame(frame, text="API Configuration")
        api_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        api_frame.grid_columnconfigure(1, weight=1)
        self._add_labeled_entry(api_frame, "Base URL:", self.base_url_var)
        api_entry = self._add_labeled_entry(api_frame, "API Key:", self.api_key_var, show="*")
        self.api_key_entry = api_entry
        ttk.Checkbutton(api_frame, text="Show", variable=self.show_api_key_var,command=self.toggle_api_key_visibility).pack(anchor="w", padx=10, pady=10)
        self.base_url_var.trace_add("write", self.on_change)
        self.api_key_var.trace_add("write", self.on_change)
        self.model_var.trace_add("write", self.on_change)
        self.temperature_var.trace_add("write", self.on_change)
        self.top_p_var.trace_add("write", self.on_change)
        self.max_tokens_var.trace_add("write", self.on_change)
        self.stream_var.trace_add("write", self.on_change)

    def create_model_config_section(self, frame):
        model_frame = ttk.LabelFrame(frame, text="Model Configuration")
        model_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        model_frame.grid_columnconfigure(1, weight=1)
        model_options = self._fetch_model_options()
        ttk.Label(model_frame, text="Model: ").pack(anchor="w", padx=10, pady=2)
        self.models_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, values=model_options, state="readonly", width=45)
        self.models_dropdown.pack(fill="x", padx=10, pady=2)

        self._add_labeled_entry(model_frame, "Temperature:", self.temperature_var, width=10)
        self._add_labeled_entry(model_frame, "Top P:", self.top_p_var, width=10)
        self._add_labeled_entry(model_frame, "Max Tokens:", self.max_tokens_var, width=10)
        ttk.Checkbutton(model_frame, text="Stream", variable=self.stream_var).pack(anchor="w", padx=10, pady=10)
        reload_btn = ttk.Button(model_frame, text="Load Model", command=self.reload_model)
        reload_btn.pack(anchor="w", padx=10, pady=10)

    def on_change(self, *args):
        logger.info(f"settings changed: {args}")
        if self.config_manager.get('api_config', 'model') != self.model_var.get():
            self.config_manager.update_from_ui('api_config', 'model', self.model_var.get())
        if self.config_manager.get('api_config', 'base_url') != self.base_url_var.get():
            self.config_manager.update_from_ui('api_config', 'base_url', self.base_url_var.get())
            self.models_dropdown.configure(values=self._fetch_model_options())
        if self.config_manager.get('api_config', 'api_key') != self.api_key_var.get():
            self.config_manager.update_from_ui('api_config', 'api_key', self.api_key_var.get())
            self.models_dropdown.configure(values=self._fetch_model_options())
        if self.config_manager.get('api_config', 'temperature') != self.temperature_var.get():
            self.config_manager.update_from_ui('api_config', 'temperature', self.temperature_var.get())
        if self.config_manager.get('api_config', 'top_p') != self.top_p_var.get():
            self.config_manager.update_from_ui('api_config', 'top_p', self.top_p_var.get())
        if self.config_manager.get('api_config', 'max_tokens') != self.max_tokens_var.get():
            self.config_manager.update_from_ui('api_config', 'max_tokens', self.max_tokens_var.get())
        if self.config_manager.get('api_config', 'stream') != self.stream_var.get():
            self.config_manager.update_from_ui('api_config', 'stream', self.stream_var.get())

    def _add_labeled_entry(self, parent, label, var, width=45, show=None):
        ttk.Label(parent, text=label).pack(anchor="w", padx=10, pady=2)
        entry = ttk.Entry(parent, textvariable=var, width=width, show=show)
        entry.pack(fill="x", padx=10, pady=2)
        return entry

    def _fetch_model_options(self):
        if self.config_manager.get("api_config", "base_url") and self.config_manager.get("api_config", "api_key"):
            return fetch_models(self.config_manager.get("api_config", "base_url"), self.config_manager.get("api_config", "api_key"))
        return ["empty"]
            
    def create_system_info_section(self,frame):
        ttk.Label(frame, text="System Info", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        table = ttk.Treeview(frame, columns=("Property", "Value"), show="headings", height=8)
        table.heading("Property", text="Property")
        table.heading("Value", text="Value")
        table.column("Property", anchor="w")
        table.column("Value", anchor="center")
        
        for key, value in get_system_info().items():
            formatted_key = key.replace("_", " ")
            table.insert("", "end", values=(formatted_key, value))
        
        table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_app_settings_section(self,frame):
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.X, padx=10, pady=5)
        app_settings_frame = ttk.LabelFrame(main_frame, text="App Settings")
        app_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(app_settings_frame, text="Theme:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        theme_dropdown = ttk.Combobox(app_settings_frame, textvariable=self.theme_var, values=self.themes, state="readonly")
        theme_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(app_settings_frame, text="Font Style:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        font_style_dropdown = ttk.Combobox(app_settings_frame, textvariable=self.font_style_var, values=self.font_styles, state="readonly")
        font_style_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(app_settings_frame, text="Font Size:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        font_size_spinbox = ttk.Spinbox(app_settings_frame, from_=8, to=20, textvariable=self.font_size_var, width=5)
        font_size_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(app_settings_frame, text="Width:").grid(row=3, column=0, padx=10, pady=2, sticky="w")
        ttk.Entry(app_settings_frame, textvariable=self.width_var, width=10).grid(row=3, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(app_settings_frame, text="Height:").grid(row=4, column=0, padx=10, pady=2, sticky="w")
        ttk.Entry(app_settings_frame, textvariable=self.height_var, width=10).grid(row=4, column=1, padx=5, pady=2, sticky="w")

        # ttk.Label(app_settings_frame, text="Font Color:").grid(row=7, column=0, padx=10, pady=2, sticky="w")
        # ttk.Entry(app_settings_frame, textvariable=self.font_color_var, width=10).grid(row=7, column=1, padx=5, pady=2, sticky="w")
        # ttk.Button(app_settings_frame, text="Choose", command=self.choose_text_color).grid(row=7, column=2, padx=5, pady=2)

        # ttk.Label(app_settings_frame, text="Background:").grid(row=8, column=0, padx=10, pady=2, sticky="w")
        # ttk.Entry(app_settings_frame, textvariable=self.bg_color_var, width=10).grid(row=8, column=1, padx=5, pady=2, sticky="w")
        # ttk.Button(app_settings_frame, text="Choose", command=self.choose_bg_color).grid(row=8, column=2, padx=5, pady=2)
        
        # ttk.Label(app_settings_frame, text="Chat Directory:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        # ttk.Entry(app_settings_frame, textvariable=self.chat_dir_var).grid(row=9, column=1, padx=5, pady=5, sticky="ew")
        # ttk.Button(app_settings_frame, text="Browse", command=self.choose_directory).grid(row=9, column=2, padx=5, pady=5)
        # app_settings_frame.grid_columnconfigure(1, weight=1)

    # def choose_directory(self):
    #     directory = filedialog.askdirectory(title="Select Chat Logs Directory")
    #     if directory:
    #         self.chat_dir_var.set(directory)

    # def choose_bg_color(self):
    #     color = colorchooser.askcolor(title="Choose Background Color")
    #     if color[1]:
    #         self.bg_color_var.set(color[1])

    # def choose_text_color(self):
    #     color = colorchooser.askcolor(title="Choose Text Color")
    #     if color[1]:
    #         self.font_color_var.set(color[1])
