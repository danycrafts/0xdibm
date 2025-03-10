import os
from datetime import datetime
from models.chat_model import ChatModel
from models.llm_handler import LLMHandler
from utils.logger import get_logger
from utils.helpers import create_file, extract_tables

logger = get_logger()

class IntentProcessor:
    def __init__(self, llm_handler:LLMHandler, chat_model:ChatModel):
        self.llm_handler = llm_handler
        self.chat_model = chat_model
        self.intent_handlers = {
            "create listing": self._handle_listing_creation,
            "job listing": self._handle_listing_creation,
            "review": self._handle_cv_review,
            "resume": self._handle_cv_review,
            "process cv batch": self._handle_batch_processing,
            "batch process": self._handle_batch_processing,
            "spell": self._handle_text_correction,
            "grammar": self._handle_text_correction,
            "correct text": self._handle_text_correction,
            "table analysis": self._handle_table_analysis,
            "analyze table": self._handle_table_analysis
        }
    
    async def process_intent(self, user_message):
        user_message_lower = user_message.lower()
        for keyword, handler in self.intent_handlers.items():
            if keyword in user_message_lower:
                return await handler(user_message_lower)
        return await self._handle_general_response(user_message)
    
    async def _handle_listing_creation(self, user_message_lower):
        listing_type = "highly experienced (senior)" if any(term in user_message_lower for term in ["senior", "experienced"]) else "generic"
        return self.llm_handler.create_listing(listing_type)
    
    async def _handle_cv_review(self, *args):
        uploaded_file = self.chat_model.file_handler.get_uploaded_file_path()
        if not uploaded_file:
            return "Please upload a CV file first."
        
        try:
            cv_text = self.llm_handler.extract_text_from_pptx(uploaded_file)
            listing = self.llm_handler.create_listing("generic")
            result = self.llm_handler.review_cv(cv_text, listing)
            self.chat_model.file_handler.reset_uploaded_file_path()
            return result
        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            return f"Error processing the CV: {str(e)}"
    
    async def _handle_batch_processing(self, *args):
        uploaded_file = self.chat_model.file_handler.get_uploaded_file_path()
        if not uploaded_file:
            return "Please upload at least one CV file first."
            
        directory = os.path.dirname(uploaded_file)
        try:
            results, listings = self.llm_handler.process_cv_batch(directory)
            return self._save_batch_results(results)
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return f"Error in batch processing: {str(e)}"
    
    def _save_batch_results(self, results):
        result_text = "Batch Processing Results:\n\n"
        for cv_id, cv_results in results.items():
            result_text += f"## {cv_id}\n"
            for listing_name, review in cv_results.items():
                result_text += f"- {listing_name}: {review}\n"
            result_text += "\n"
        
        download_dir = self.chat_model.file_handler.storage_directory+os.sep+"downloads"
        os.makedirs(download_dir, exist_ok=True)
        result_file = os.path.join(download_dir, f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(result_file, "w") as f:
            f.write(result_text)
        
        return f"Batch processing completed. Results saved to {os.path.basename(result_file)}"
    
    async def _handle_text_correction(self, *args):
        uploaded_file = self.chat_model.file_handler.get_uploaded_file_path()
        if not uploaded_file:
            return "Please upload a CV file first."
            
        try:
            cv_text = self.llm_handler.extract_text_from_pptx(uploaded_file)
            result = self.llm_handler.spelling_and_grammar_check(cv_text)
            created = create_file(f"outputs/gen_{uploaded_file}", result)
            if created:
                self.chat_model.download_file(f"outputs/gen_{uploaded_file}")
            self.chat_model.file_handler.reset_uploaded_file_path()
            return result
        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            return f"Error processing the CV: {str(e)}"
    
    async def _handle_table_analysis(self, *args):
        uploaded_file = self.chat_model.file_handler.get_uploaded_file_path()
        if not uploaded_file:
            return "Please upload a PDF file containing tables first."
            
        try:
            tables = extract_tables(uploaded_file)
            if not tables:
                return "No tables found in the uploaded PDF."
                
            analysis = self.llm_handler.table_analysis(tables)
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing tables: {str(e)}")
            return f"Error analyzing tables: {str(e)}"
    
    async def _handle_general_response(self, user_message):
        return self.llm_handler.response(user_message)