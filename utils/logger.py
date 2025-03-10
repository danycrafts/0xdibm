import logging
import threading
from logging.handlers import RotatingFileHandler
import sys
from typing import Optional

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
class ColoredFormatter(logging.Formatter):
    """Custom formatter to add color to log messages."""
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[41m'  # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{super().format(record)}{self.RESET}"

# a function to get Logger instance
def get_logger(log_level: int = logging.DEBUG, log_file: str = 'desh.log') -> 'Logger':
    return Logger(log_level, log_file)
class Logger:
    _instance: Optional['Logger'] = None
    _lock = threading.Lock()

    def __new__(cls, log_level: int = logging.INFO, log_file: str = 'desh.log') -> 'Logger':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Logger, cls).__new__(cls)
                    cls._instance._initialize_logger(log_level, log_file)
        return cls._instance

    def _initialize_logger(self, log_level: int, log_file: str) -> None:
        self.logger_instance = logging.getLogger(__name__)
        self.logger_instance.setLevel(log_level)

        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=30)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        self.logger_instance.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_formatter = ColoredFormatter(LOG_FORMAT)
        stream_handler.setFormatter(stream_formatter)
        self.logger_instance.addHandler(stream_handler)

    def set_log_level(self, log_level: int) -> None:
        self.logger_instance.setLevel(log_level)
        for handler in self.logger_instance.handlers:
            handler.setLevel(log_level)

    def debug(self, message: str) -> None:
        self.logger_instance.debug(message)
    
    def info(self, message: str) -> None:
        self.logger_instance.info(message)
    
    def warning(self, message: str) -> None:
        self.logger_instance.warning(message)
    
    def error(self, message: str) -> None:
        self.logger_instance.error(message)

    def critical(self, message: str) -> None:
        self.logger_instance.critical(message)
