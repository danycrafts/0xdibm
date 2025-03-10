import tkinter as tk
import ttkbootstrap as ttk
from config import ConfigManager
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()

class ChatView:
    def __init__(self, notebook: ttk.Notebook, config_manager: ConfigManager, upload_callback, send_callback):
        logger.debug("Initializing ChatView")
        self.notebook = notebook
        self.config_manager = config_manager
        self.font = config_manager.get('app_settings', 'font_style')
        self.font_size = config_manager.get('app_settings', 'font_size')
        self.upload_callback = upload_callback
        self.send_callback = send_callback
        self.frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame, text="Chat")
        self.chat_history = self._create_chat_history(self.frame)
        self.input_area = self._create_input_area(self.frame)
        self._configure_chat_tags()
    
    def _create_chat_history(self, parent):
        logger.debug("Creating chat history area")
        frame = ttk.Frame(parent)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        canvas_frame = ttk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(canvas_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(canvas_frame,height=20,width=50,state='disabled',wrap=tk.WORD,font=(self.font, self.font_size),bg="#f9f9f9",padx=15,pady=15,yscrollcommand=scrollbar.set,borderwidth=0,highlightthickness=0)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        return text_widget
    
    def _configure_chat_tags(self):
        self.chat_history.config(state='normal')
        self.chat_history.tag_configure("user_bubble",background="#007bff",foreground="white",borderwidth=0,relief="solid",lmargin1=100,lmargin2=100,rmargin=20,spacing1=10,spacing3=10,justify='right')
        self.chat_history.tag_configure("agent_bubble",background="#e9e9e9",foreground="#333333",borderwidth=0,relief="solid",lmargin1=20,lmargin2=20,rmargin=100,spacing1=10,spacing3=10,justify='left')
        self.chat_history.tag_configure("system_bubble",background="#ffd700",foreground="#333333",borderwidth=0,relief="solid",lmargin1=60,lmargin2=60,rmargin=60,spacing1=10,spacing3=10,justify='center')
        self.chat_history.tag_configure("user_timestamp",foreground="#757575",font=(self.font, self.font_size - 2, 'italic'),justify='right',rmargin=10)
        self.chat_history.tag_configure("agent_timestamp",foreground="#757575",font=(self.font, self.font_size - 2, 'italic'),justify='left',lmargin1=10)
        self.chat_history.tag_configure("system_timestamp",foreground="#757575",font=(self.font, self.font_size - 2, 'italic'),justify='center')
        self.chat_history.config(state='disabled')
    
    def _create_input_area(self, parent):
        logger.debug("Creating input area")
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=5)
        frame = ttk.Frame(parent)
        frame.pack(padx=10, pady=5, fill=tk.X)
        upload_btn = ttk.Button(frame, text="Upload", command=self.upload_callback, bootstyle="secondary-outline")
        upload_btn.pack(side=tk.LEFT, padx=(0, 5))
        entry_container = ttk.Frame(frame, bootstyle="light")
        entry_container.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        message_entry = ttk.Entry(entry_container, font=(self.font, self.font_size))
        message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=3)
        send_btn = ttk.Button( frame, text="Send", command=self.send_callback, bootstyle="primary")
        send_btn.pack(side=tk.LEFT)
        message_entry.bind('<Return>', lambda event: self.send_callback())
        typing_status = ttk.Label(parent, text="", font=(self.font, self.font_size - 2, 'italic'), foreground="#757575")
        typing_status.pack(anchor=tk.W, padx=15, pady=(0, 5))
        self.message_entry = message_entry
        self.typing_status = typing_status
    
    def add_message_to_history(self, message, sender="You", timestamp=None):
        logger.debug(f"Adding message to history: {message} from {sender}")
        self.chat_history.config(state='normal')
        if timestamp is None:
            timestamp = datetime.now().strftime("[%H:%M:%S]")
        if self.chat_history.index('end-1c') != '1.0':
            self.chat_history.insert(tk.END, "\n")
        if sender == "You":
            self.chat_history.insert(tk.END, f"You {timestamp}\n", "user_timestamp")
            self.chat_history.insert(tk.END, f"{message}\n", "user_bubble")
        elif sender == "Agent":
            self.chat_history.insert(tk.END, f"DESH Agent {timestamp}\n", "agent_timestamp")
            self.chat_history.insert(tk.END, f"{message}\n", "agent_bubble")
        else:
            self.chat_history.insert(tk.END, f"{timestamp}\n", "system_timestamp")
            self.chat_history.insert(tk.END, f"{message}\n", "system_bubble")
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
    
    def get_message(self):
        return self.message_entry.get().strip()
    
    def clear_message(self):
        self.message_entry.delete(0, tk.END)
    
    def set_typing_status(self, status):
        self.typing_status.config(text=status)
