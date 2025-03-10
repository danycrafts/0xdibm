import os
from datetime import datetime
from .file_handler import FileHandler
from utils.logger import get_logger
from config import ConfigManager

logger = get_logger()

class ChatModel:
    def __init__(self, config_manager: ConfigManager, file_handler: FileHandler):
        logger.debug("Initializing ChatModel")
        self.config_manager = config_manager
        self.file_handler = file_handler
    
    def save_message(self, message, sender="You"):
        log_file = os.path.join(self.file_handler.storage_directory, f"chat_log_{datetime.now().strftime('%Y%m%d')}.txt")
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"<BEGIN:{sender}:{timestamp}>\n")
            f.write(f"{message}\n")
            f.write(f"<END:{sender}>\n")
    
    def get_messages(self, limit=250):
        all_messages = self._get_all_messages()
        return all_messages[-limit:] if limit and len(all_messages) > limit else all_messages

    def _get_all_messages(self):
        messages = []
        current_message = {"sender": None, "timestamp": None, "content": []}
        try:
            for filename in sorted(os.listdir(self.file_handler.storage_directory)):
                if filename.startswith("chat_log_") and filename.endswith(".txt"):
                    file_path = os.path.join(self.file_handler.storage_directory, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.rstrip()
                            if line.startswith("<BEGIN:"):
                                # If we have a previous message in progress, add it to messages
                                if current_message["sender"] is not None:
                                    messages.append(current_message)
                                # Parse the begin tag: <BEGIN:sender:timestamp>
                                parts = line[7:-1].split(":", 1)  # Remove <BEGIN: and >
                                sender = parts[0]
                                timestamp = parts[1] if len(parts) > 1 else ""
                                current_message = {"sender": sender, "timestamp": timestamp, "content": []}
                            elif line.startswith("<END:"):
                                # Add the completed message to messages
                                if current_message["sender"] is not None:
                                    messages.append(current_message)
                                    current_message = {"sender": None, "timestamp": None, "content": []}
                            elif current_message["sender"] is not None:
                                current_message["content"].append(line)
            if current_message["sender"] is not None:
                messages.append(current_message)
        except Exception as e:
            logger.error(f"Error while getting messages: {e}")
        return messages
    
    def upload_file(self):
        file_name, saved_path = self.file_handler.upload_file()
        if file_name:
            logger.info(f"File uploaded: {file_name}")
            self.uploaded_file_path = saved_path
            return file_name, saved_path
        return None, None
    
    def download_file(self, file_path):
        return self.file_handler.download_file(file_path)

    
