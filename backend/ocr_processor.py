"""
PaddleOCR integration for receipt and invoice processing
"""
import os
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np
from io import BytesIO
import base64

# Try to import PaddleOCR - make it optional
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("⚠️  PaddleOCR not available - OCR features will be limited")

# Try to import pdf2image - make it optional
try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("⚠️  pdf2image not available - PDF processing will be limited")


class OCRProcessor:
    """Process documents using PaddleOCR-VL"""
    
    def __init__(self, use_angle_cls=True, lang='en'):
        """
        Initialize PaddleOCR processor
        
        Args:
            use_angle_cls: Whether to use angle classification
            lang: Language code ('en', 'ch', 'multi')
        """
        if not PADDLEOCR_AVAILABLE:
            self.ocr = None
            print("⚠️  PaddleOCR not installed - OCR features disabled")
        else:
            try:
                # Initialize PaddleOCR with minimal parameters to avoid version compatibility issues
                # Note: Different PaddleOCR versions support different parameters
                # Suppress warnings and use CPU mode for compatibility
                import warnings
                warnings.filterwarnings('ignore')
                os.environ['FLAGS_eager_delete_tensor_gb'] = '0'
                os.environ['FLAGS_allocator_strategy'] = 'auto_growth'
                
                self.ocr = PaddleOCR(
                    use_angle_cls=use_angle_cls,
                    lang=lang
                )
            except Exception as e:
                print(f"⚠️  Failed to initialize PaddleOCR: {e}")
                print(f"   This usually means version incompatibility.")
                print(f"   Try: pip install paddleocr==2.7.0 --force-reinstall")
                self.ocr = None
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process an image file and extract text and layout
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text, layout, and metadata
        """
        if not self.ocr:
            return {
                'error': 'PaddleOCR is not available. Please install it with: pip install paddlepaddle paddleocr',
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown'
            }
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            # Extract text and bounding boxes
            text_lines = []
            layout_info = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        bbox = line[0]  # Bounding box coordinates
                        text_info = line[1]  # (text, confidence)
                        text = text_info[0]
                        confidence = text_info[1]
                        
                        text_lines.append(text)
                        layout_info.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox,
                            'position': self._calculate_position(bbox)
                        })
            
            # Detect language (simple heuristic)
            detected_lang = self._detect_language(text_lines)
            
            return {
                'text': '\n'.join(text_lines),
                'text_lines': text_lines,
                'layout': layout_info,
                'language': detected_lang,
                'raw_result': result
            }
        except Exception as e:
            return {
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown'
            }
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file and extract text from all pages
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries, one per page
        """
        if not PDF2IMAGE_AVAILABLE:
            return [{
                'error': 'pdf2image is not available. Please install it with: pip install pdf2image and install poppler',
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown'
            }]
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            results = []
            
            for i, image in enumerate(images):
                # Save temporary image
                temp_path = f"/tmp/pdf_page_{i}.png"
                image.save(temp_path, 'PNG')
                
                # Process image
                page_result = self.process_image(temp_path)
                page_result['page_number'] = i + 1
                results.append(page_result)
                
                # Clean up
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            return results
        except Exception as e:
            return [{
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown'
            }]
    
    def process_bytes(self, file_bytes: bytes, file_type: str = 'image') -> Dict:
        """
        Process file from bytes (for API uploads)
        
        Args:
            file_bytes: File content as bytes
            file_type: 'image' or 'pdf'
            
        Returns:
            Dictionary with extracted text and layout
        """
        try:
            if file_type == 'pdf':
                if not PDF2IMAGE_AVAILABLE:
                    return {
                        'error': 'pdf2image is not available. Please install it with: pip install pdf2image and install poppler',
                        'text': '',
                        'text_lines': [],
                        'layout': [],
                        'language': 'unknown'
                    }
                if not self.ocr:
                    return {
                        'error': 'PaddleOCR is not available. Please install it with: pip install paddlepaddle paddleocr',
                        'text': '',
                        'text_lines': [],
                        'layout': [],
                        'language': 'unknown'
                    }
                # Check if poppler is available
                try:
                    # Convert PDF bytes to images
                    images = pdf2image.convert_from_bytes(file_bytes)
                    if images:
                        # Process first page for now
                        temp_path = "/tmp/uploaded_pdf.png"
                        images[0].save(temp_path, 'PNG')
                        result = self.process_image(temp_path)
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        return result
                    else:
                        return {
                            'error': 'No pages found in PDF',
                            'text': '',
                            'text_lines': [],
                            'layout': [],
                            'language': 'unknown'
                        }
                except Exception as pdf_error:
                    error_msg = str(pdf_error)
                    if 'poppler' in error_msg.lower() or 'page count' in error_msg.lower():
                        return {
                            'error': 'Unable to get page count. Is poppler installed and in PATH?',
                            'text': '',
                            'text_lines': [],
                            'layout': [],
                            'language': 'unknown'
                        }
                    else:
                        return {
                            'error': f'PDF processing failed: {error_msg}',
                            'text': '',
                            'text_lines': [],
                            'layout': [],
                            'language': 'unknown'
                        }
            else:
                if not self.ocr:
                    return {
                        'error': 'PaddleOCR is not available. Please install it with: pip install paddlepaddle paddleocr',
                        'text': '',
                        'text_lines': [],
                        'layout': [],
                        'language': 'unknown'
                    }
                # Process image from bytes
                image = Image.open(BytesIO(file_bytes))
                temp_path = "/tmp/uploaded_image.png"
                image.save(temp_path, 'PNG')
                result = self.process_image(temp_path)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return result
        except Exception as e:
            return {
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown'
            }
    
    def _calculate_position(self, bbox: List) -> str:
        """
        Calculate approximate position of text in document
        
        Args:
            bbox: Bounding box coordinates
            
        Returns:
            Position description ('header', 'body', 'footer', 'left', 'right', 'center')
        """
        if not bbox or len(bbox) < 4:
            return 'unknown'
        
        # Calculate center point
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        
        # Simple heuristics (would need document dimensions for accuracy)
        position = []
        
        # Vertical position
        if center_y < 0.2:  # Top 20%
            position.append('header')
        elif center_y > 0.8:  # Bottom 20%
            position.append('footer')
        else:
            position.append('body')
        
        # Horizontal position
        if center_x < 0.33:
            position.append('left')
        elif center_x > 0.67:
            position.append('right')
        else:
            position.append('center')
        
        return '-'.join(position)
    
    def _detect_language(self, text_lines: List[str]) -> str:
        """
        Simple language detection based on character patterns
        
        Args:
            text_lines: List of extracted text lines
            
        Returns:
            Language code ('en', 'ch', 'multi', 'unknown')
        """
        if not text_lines:
            return 'unknown'
        
        combined_text = ' '.join(text_lines)
        chinese_chars = sum(1 for char in combined_text if '\u4e00' <= char <= '\u9fff')
        total_chars = len([c for c in combined_text if c.isalnum() or '\u4e00' <= c <= '\u9fff'])
        
        if total_chars == 0:
            return 'unknown'
        
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        if chinese_ratio > 0.3:
            # Check if also has English
            has_english = any(ord(c) < 128 for c in combined_text)
            return 'multi' if has_english else 'ch'
        else:
            return 'en'
    
    def extract_key_value_pairs(self, ocr_result: Dict) -> Dict[str, str]:
        """
        Extract key-value pairs from OCR result (e.g., "Total: $50.00")
        
        Args:
            ocr_result: OCR processing result
            
        Returns:
            Dictionary of key-value pairs
        """
        key_values = {}
        text_lines = ocr_result.get('text_lines', [])
        
        for line in text_lines:
            # Look for common patterns like "Key: Value" or "Key Value"
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    key_values[key.lower()] = value
        
        return key_values

