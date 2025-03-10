import os
from datetime import datetime
import uuid
import shutil
from tkinter import filedialog, messagebox
from utils.logger import get_logger

logger = get_logger()

class FileHandler:
    def __init__(self, storage_directory="files"):
        self.storage_directory = storage_directory
        os.makedirs(storage_directory, exist_ok=True)
        self.uploaded_file_path = ""
        self.downloaded_file_path = ""
        logger.debug(f"Storage directory set to: {self.storage_directory}")
    
    def upload_file(self):
        try:
            filename = filedialog.askopenfilename(
                title="Select a File",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Image files", "*.png *.jpg *.jpeg *.gif"),
                    ("Document files", "*.pdf *.docx *.pptx")
                ]
            )
            if filename:
                file_name = os.path.basename(filename)
                timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
                unique_id = str(uuid.uuid4())[:5]
                new_filename = os.path.join(self.storage_directory, f"{timestamp}_{unique_id}_{file_name}")
                shutil.copy2(filename, new_filename)
                self.uploaded_file_path = new_filename
                return file_name, new_filename
            return None, None
        
        except Exception as e:
            messagebox.showerror("Upload Error", str(e))
            return None, None
   
    def download_file(self, source_file_path):
        try:
            if not os.path.exists(source_file_path):
                messagebox.showerror("Download Error", "The source file does not exist.")
                return False
            original_filename = os.path.basename(source_file_path)
            
            parts = original_filename.split('_', 2)
            if len(parts) >= 3 and len(parts[0]) == 8 and len(parts[1]) == 8:
                original_filename = parts[2]
            
            target_path = filedialog.asksaveasfilename(title="Save File As",initialfile=original_filename,filetypes=[("All files", "*.*")])
            
            if target_path:
                shutil.copy2(source_file_path, target_path)
                messagebox.showinfo("Download Complete", f"File saved to: {target_path}")
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("Download Error", str(e))
            return False
        
    def get_uploaded_file_path(self):
        return self.uploaded_file_path

    def get_downloaded_file_path(self):
        return self.downloaded_file_path
    
    def set_uploaded_file_path(self, path):
        self.uploaded_file_path = path

    def set_downloaded_file_path(self, path):
        self.downloaded_file_path = path

    def reset_uploaded_file_path(self):
        self.uploaded_file_path = ""
    
    def reset_downloaded_file_path(self):
        self.downloaded_file_path = ""