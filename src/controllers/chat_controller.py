import asyncio
import threading
import ttkbootstrap as ttk
from config import ConfigManager
from src.models.chat_model import ChatModel
from src.models.file_handler import FileHandler
from src.models.llm_handler import LLMHandler
from src.views.chat_view import ChatView
from utils.logger import get_logger

logger = get_logger()


class ChatController:
    def __init__(self, config_manager: ConfigManager, notebook: ttk.Notebook, llm_handler: LLMHandler):
        self.config_manager = config_manager
        self.chats_storage_dir = "chats_data"
        self.file_handler = FileHandler(storage_directory=self.chats_storage_dir)
        self.llm_handler = llm_handler
        self.chat_model = ChatModel(self.config_manager, self.file_handler)
        self.chat_view = ChatView(notebook, self.config_manager, upload_callback=self.handle_file_upload, send_callback=self.send_message)
        self._load_existing_messages()
    
    def handle_file_upload(self):
        file_name, saved_path = self.chat_model.upload_file()
        if file_name:
            system_message = f"File uploaded: {file_name}"
            self.chat_view.add_message_to_history(system_message, sender="System")
            self.chat_model.save_message(system_message, sender="System")
    
    def _load_existing_messages(self):
        logger.debug("Loading existing messages")
        try:
            existing_messages = self.chat_model.get_messages(limit=250)
            if not existing_messages:
                logger.debug("No existing messages to load")
                return
            
            for message_data in existing_messages:
                sender = message_data["sender"]
                timestamp = message_data["timestamp"]
                content = "\n".join(message_data["content"])
                
                self.chat_view.add_message_to_history(content, sender=sender, timestamp=timestamp)
        except Exception as e:
            logger.error(f"Failed to load existing messages: {e}")
    
    def send_message(self):
        message = self.chat_view.get_message()
        logger.debug(f"Sending message: {message}")

        if not message:
            return
            
        # Display user message
        self.chat_view.add_message_to_history(message, sender="You")
        self.chat_model.save_message(message, sender="You")
        self.chat_view.clear_message()
        
        # Show typing status and start async response
        self.chat_view.set_typing_status("Agent is typing...")
        threading.Thread(target=self._run_async_response, args=(message,), daemon=True).start()
    
    def _run_async_response(self, message):
        logger.debug(f"Running async response for message: {message}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_generate_agent_response(message))
    
    async def _async_generate_agent_response(self, user_message):
        logger.debug(f"Generating async agent response for user message: {user_message}")
        
        # Process the message intent and get a response
        response_text = await self.llm_handler._process_message_intent(user_message,self.file_handler)
        
        # Use after() to safely update UI from a non-main thread
        self.chat_view.frame.after(0, lambda: self.chat_view.add_message_to_history(response_text, "Agent"))
        self.chat_view.frame.after(0, lambda: self.chat_view.set_typing_status(""))
        self.chat_view.frame.after(0, lambda: self.chat_model.save_message(response_text, sender="Agent"))