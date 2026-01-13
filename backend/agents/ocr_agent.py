"""
OCR Agent - Document processing using PaddleOCR
"""
import logging
from typing import Dict, Any, Optional
from backend.agents.base_agent import BaseAgent
from backend.ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)


class OCRAgent(BaseAgent):
    """Agent for OCR document processing using PaddleOCR"""
    
    def __init__(self, ocr_processor: Optional[OCRProcessor] = None):
        """
        Initialize OCR Agent
        
        Args:
            ocr_processor: Optional OCRProcessor instance (will create one if not provided)
        """
        super().__init__(
            agent_name="OCR",
            system_message="You are an OCR agent that extracts text and layout information from documents."
        )
        self.ocr_processor = ocr_processor or OCRProcessor()
        self.log_action("initialized")
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Process document for OCR extraction
        
        Args:
            input_data: Can be:
                - File path (str)
                - File bytes (bytes)
                - Dict with 'file_path' or 'file_bytes' and optional 'file_type'
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with OCR results:
            - text: Extracted text
            - text_lines: List of text lines
            - layout: Layout information with bounding boxes
            - language: Detected language
            - quality_score: OCR quality score
        """
        try:
            self.log_action("processing_started", {"input_type": type(input_data).__name__})
            
            # Handle different input types
            if isinstance(input_data, str):
                # File path
                result = self.ocr_processor.process_image(input_data)
            elif isinstance(input_data, bytes):
                # File bytes
                file_type = kwargs.get("file_type", "image")
                result = self.ocr_processor.process_bytes(input_data, file_type=file_type)
            elif isinstance(input_data, dict):
                # Dictionary input
                if "file_path" in input_data:
                    result = self.ocr_processor.process_image(input_data["file_path"])
                elif "file_bytes" in input_data:
                    file_type = input_data.get("file_type", kwargs.get("file_type", "image"))
                    result = self.ocr_processor.process_bytes(input_data["file_bytes"], file_type=file_type)
                else:
                    return self.handle_error(
                        ValueError("Input dict must contain 'file_path' or 'file_bytes'"),
                        {"input_data_keys": list(input_data.keys())}
                    )
            else:
                return self.handle_error(
                    TypeError(f"Unsupported input type: {type(input_data)}"),
                    {"input_type": type(input_data).__name__}
                )
            
            # Format result
            formatted_result = {
                "success": "error" not in result,
                "text": result.get("text", ""),
                "text_lines": result.get("text_lines", []),
                "layout": result.get("layout", []),
                "language": result.get("language", "unknown"),
                "quality_score": result.get("quality_score", 0.0),
                "error": result.get("error")
            }
            
            self.log_action("processing_completed", {
                "text_length": len(formatted_result["text"]),
                "lines_count": len(formatted_result["text_lines"]),
                "quality_score": formatted_result["quality_score"]
            })
            
            return formatted_result
            
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
