"""
PaddleOCR integration for receipt and invoice processing
"""
import os
import gc
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
from io import BytesIO
import base64


class OCRProcessor:
    """Process documents using PaddleOCR-VL"""
    
    def __init__(self, use_angle_cls=True, lang='en'):
        """
        Initialize PaddleOCR processor with lightweight models for production
        
        Args:
            use_angle_cls: Whether to use angle classification (deprecated in 3.x, using use_textline_orientation)
            lang: Language code ('en', 'ch', 'multi')
        """
        try:
            # PaddleOCR 3.x API - minimal parameters for compatibility
            print("[OCR] Initializing PaddleOCR...")
            # Use only the most basic parameters for PaddleOCR 3.x
            self.ocr = PaddleOCR(lang=lang)
            print("[OCR] PaddleOCR initialized successfully")
        except Exception as e:
            # If initialization fails, try with explicit device
            try:
                print(f"[OCR] First attempt failed: {e}, trying with explicit device...")
                self.ocr = PaddleOCR(lang=lang, device='cpu')
                print("[OCR] PaddleOCR initialized with explicit CPU device")
            except Exception as e2:
                # If both fail, set to None and handle gracefully
                print(f"[OCR] ERROR: PaddleOCR initialization failed: {e2}")
                import traceback
                traceback.print_exc()
                self.ocr = None
                print("[OCR] Service will continue without OCR functionality")
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process an image file and extract text and layout
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text, layout, and metadata
        """
        print(f"[OCR] Starting process_image for: {image_path}")
        if self.ocr is None:
            print("[OCR] ERROR: PaddleOCR is not initialized")
            return {
                'error': 'PaddleOCR is not initialized',
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }
        try:
            print("[OCR] Running OCR...")
            # PaddleOCR 3.x uses predict() or ocr() without cls parameter
            try:
                # Try predict() first (PaddleOCR 3.x new API)
                if hasattr(self.ocr, 'predict'):
                    result = self.ocr.predict(image_path)
                else:
                    result = self.ocr.ocr(image_path)
            except TypeError as te:
                # Fallback: try without any extra parameters
                print(f"[OCR] API call failed: {te}, trying alternative...")
                try:
                    result = self.ocr.ocr(image_path)
                except:
                    result = self.ocr.predict(image_path) if hasattr(self.ocr, 'predict') else None
            
            # Extract text and bounding boxes
            text_lines = []
            layout_info = []
            confidences = []
            
            print(f"[OCR] Raw result type: {type(result)}")
            
            # Handle different result formats from PaddleOCR 3.x
            if result:
                # PaddleOCR 3.x returns a list with dict containing 'rec_texts' and 'rec_scores'
                if isinstance(result, list) and len(result) > 0:
                    ocr_data = result[0]
                    
                    # Check for PaddleOCR 3.x new format with rec_texts
                    if isinstance(ocr_data, dict) and 'rec_texts' in ocr_data:
                        print("[OCR] Detected PaddleOCR 3.x format with rec_texts")
                        rec_texts = ocr_data.get('rec_texts', [])
                        rec_scores = ocr_data.get('rec_scores', [])
                        rec_polys = ocr_data.get('rec_polys', [])
                        
                        for i, text in enumerate(rec_texts):
                            if text and text.strip():
                                confidence = rec_scores[i] if i < len(rec_scores) else 0.5
                                bbox = rec_polys[i].tolist() if i < len(rec_polys) else []
                                
                                text_lines.append(str(text))
                                confidences.append(float(confidence))
                                layout_info.append({
                                    'text': str(text),
                                    'confidence': float(confidence),
                                    'bbox': bbox,
                                    'position': {}
                                })
                        print(f"[OCR] Extracted {len(text_lines)} text lines from new format")
                    
                    # Fallback to old format parsing
                    elif hasattr(ocr_data, '__iter__') and not isinstance(ocr_data, dict):
                        print("[OCR] Using legacy format parsing")
                        for line in ocr_data:
                            if line:
                                try:
                                    if isinstance(line, (list, tuple)) and len(line) >= 2:
                                        bbox = line[0]
                                        text_info = line[1]
                                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                            text = str(text_info[0])
                                            confidence = float(text_info[1]) if text_info[1] else 0.5
                                        else:
                                            text = str(text_info)
                                            confidence = 0.5
                                    else:
                                        text = str(line)
                                        bbox = []
                                        confidence = 0.5
                                    
                                    if text.strip():
                                        text_lines.append(text)
                                        confidences.append(confidence)
                                        layout_info.append({
                                            'text': text,
                                            'confidence': confidence,
                                            'bbox': bbox if isinstance(bbox, list) else [],
                                            'position': self._calculate_position(bbox) if isinstance(bbox, list) and bbox else {}
                                        })
                                except Exception as parse_err:
                                    print(f"[OCR] Error parsing line: {parse_err}")
                                    continue
            
            # Detect language (simple heuristic)
            detected_lang = self._detect_language(text_lines)
            
            # Calculate quality score
            quality_score = sum(confidences) / len(confidences) if confidences else 0.5
            
            print(f"[OCR] Extracted {len(text_lines)} lines, quality: {quality_score:.2f}")
            
            return {
                'text': '\n'.join(text_lines),
                'text_lines': text_lines,
                'layout': layout_info,
                'language': detected_lang,
                'quality_score': quality_score,
                'raw_result': result
            }
        except Exception as e:
            print(f"[OCR] ERROR in process_image: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file and extract text from all pages
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries, one per page
        """
        try:
            import pdf2image
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
        except ImportError:
            # Try PyMuPDF as fallback
            return self._process_pdf_with_fitz(pdf_path)
        except Exception as e:
            return [{
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }]
    
    def _process_pdf_with_fitz(self, pdf_path: str) -> List[Dict]:
        """Process PDF using PyMuPDF (fitz)"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            results = []
            
            for page_num in range(min(5, len(doc))):
                page = doc[page_num]
                
                # Try to extract text directly first
                text = page.get_text()
                if text.strip():
                    results.append({
                        'text': text,
                        'text_lines': text.split('\n'),
                        'layout': [],
                        'language': 'en',
                        'quality_score': 0.9,
                        'page_number': page_num + 1
                    })
                else:
                    # Render as image and OCR
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                    
                    image = Image.open(BytesIO(img_bytes))
                    temp_path = f"/tmp/pdf_page_{page_num}.png"
                    image.save(temp_path, 'PNG')
                    
                    page_result = self.process_image(temp_path)
                    page_result['page_number'] = page_num + 1
                    results.append(page_result)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            doc.close()
            return results
        except ImportError:
            return [{
                'error': 'PDF processing requires pdf2image or PyMuPDF',
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }]
    
    def process_bytes(self, file_bytes: bytes, file_type: str = 'image') -> Dict:
        """
        Process file from bytes (for API uploads) - Memory optimized
        
        Args:
            file_bytes: File content as bytes
            file_type: 'image' or 'pdf'
            
        Returns:
            Dictionary with extracted text and layout
        """
        print(f"[OCR] Starting process_bytes - Type: {file_type}, Size: {len(file_bytes) / 1024:.1f}KB")
        temp_path = None
        try:
            if file_type == 'pdf':

                return self._process_pdf_bytes(file_bytes)
                print("[OCR] Converting PDF to image...")
                # Convert PDF bytes to images - memory efficient: only first page
                # Use dpi=200 instead of default 300 to reduce memory
                images = pdf2image.convert_from_bytes(
                    file_bytes, 
                    dpi=200,  # Lower DPI to reduce memory
                    first_page=1,
                    last_page=1  # Only process first page
                )
                print(f"[OCR] PDF converted - {len(images)} page(s)")
                if images:
                    # Resize if too large (max 2000px on longest side)
                    image = images[0]
                    print(f"[OCR] Image size: {image.size}")
                    max_size = 2000
                    if max(image.size) > max_size:
                        ratio = max_size / max(image.size)
                        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                        print(f"[OCR] Resizing to: {new_size}")
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    temp_path = "/tmp/uploaded_pdf.png"
                    print(f"[OCR] Saving to: {temp_path}")
                    image.save(temp_path, 'PNG', optimize=True)
                    # Clear image from memory
                    del image, images
                    gc.collect()  # Force garbage collection
                    result = self.process_image(temp_path)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        temp_path = None
                    return result

            else:
                # Process image from bytes - resize if too large
                print("[OCR] Opening image from bytes...")
                
                # Try to detect actual image format from magic bytes
                image = None
                format_detected = None
                
                # Check magic bytes to detect actual format
                if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                    format_detected = "PNG"
                elif file_bytes[:2] == b'\xff\xd8':
                    format_detected = "JPEG"
                elif file_bytes[:6] in (b'GIF87a', b'GIF89a'):
                    format_detected = "GIF"
                elif file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WEBP':
                    format_detected = "WEBP"
                elif file_bytes[:4] == b'\x00\x00\x00\x0c' or file_bytes[:4] == b'\x00\x00\x00\x18':
                    format_detected = "HEIC"
                    
                print(f"[OCR] Detected format from magic bytes: {format_detected}")
                
                try:
                    image = Image.open(BytesIO(file_bytes))
                except Exception as open_error:
                    print(f"[OCR] PIL failed to open image: {open_error}")
                    
                    # Try saving to temp file and opening (sometimes helps with corrupt headers)
                    try:
                        temp_input_path = "/tmp/temp_image_input"
                        with open(temp_input_path, 'wb') as f:
                            f.write(file_bytes)
                        image = Image.open(temp_input_path)
                        print(f"[OCR] Opened image from temp file")
                    except Exception as temp_error:
                        print(f"[OCR] Temp file method also failed: {temp_error}")
                        
                        # Return empty result if can't open
                        return {
                            'error': f'Cannot open image: {open_error}',
                            'text': '',
                            'text_lines': [],
                            'layout': [],
                            'language': 'unknown',
                            'quality_score': 0.0
                        }
                
                print(f"[OCR] Image size: {image.size}, Format: {image.format}, Mode: {image.mode}")
                

                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'P', 'LA'):
                    image = image.convert('RGB')

                # Resize if too large (max 2000px on longest side) to reduce memory
                max_size = 2000
                if max(image.size) > max_size:
                    ratio = max_size / max(image.size)
                    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                    print(f"[OCR] Resizing to: {new_size}")
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                temp_path = "/tmp/uploaded_image.png"
                print(f"[OCR] Saving to: {temp_path}")
                image.save(temp_path, 'PNG', optimize=True)
                # Clear image from memory
                del image
                gc.collect()  # Force garbage collection
                print("[OCR] Processing image with OCR...")
                result = self.process_image(temp_path)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    temp_path = None
                print(f"[OCR] Image processing complete - Extracted {len(result.get('text', ''))} characters")
                return result
        except Exception as e:
            print(f"[OCR] ERROR in process_bytes: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }
        finally:
            # Ensure cleanup
            if temp_path and os.path.exists(temp_path):
                try:
                    print(f"[OCR] Cleaning up temp file: {temp_path}")
                    os.remove(temp_path)
                except Exception as cleanup_error:
                    print(f"[OCR] Cleanup error: {cleanup_error}")
    
    def _process_pdf_bytes(self, file_bytes: bytes) -> Dict:
        """Process PDF from bytes"""
        all_text = []
        all_layout = []
        temp_files = []  # Track temp files for cleanup
        
        try:
            # Try PyMuPDF first (it's faster and more reliable)
            try:
                import fitz
                print("[OCR] Using PyMuPDF for PDF processing")
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                
                for page_num in range(min(3, len(doc))):  # Limit to first 3 pages for speed
                    page = doc[page_num]
                    
                    # Try direct text extraction first (fastest)
                    text = page.get_text().strip()
                    
                    if text and len(text) > 50:  # Good text extraction
                        print(f"[OCR] Page {page_num + 1}: Direct text extraction ({len(text)} chars)")
                        all_text.append(f"--- Page {page_num + 1} ---")
                        all_text.append(text)
                    else:
                        # Render as image and OCR
                        print(f"[OCR] Page {page_num + 1}: Using image OCR")
                        mat = fitz.Matrix(1.5, 1.5)  # Lower resolution for speed
                        pix = page.get_pixmap(matrix=mat)
                        img_bytes = pix.tobytes("png")
                        
                        image = Image.open(BytesIO(img_bytes))
                        # Resize if too large
                        if max(image.size) > 1500:
                            ratio = 1500 / max(image.size)
                            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                            image = image.resize(new_size, Image.Resampling.LANCZOS)
                        
                        temp_path = f"/tmp/pdf_page_{page_num}_{id(self)}.png"
                        temp_files.append(temp_path)
                        image.save(temp_path, 'PNG', optimize=True)
                        del image  # Free memory
                        
                        page_result = self.process_image(temp_path)
                        if page_result.get('text'):
                            all_text.append(f"--- Page {page_num + 1} ---")
                            all_text.append(page_result['text'])
                            all_layout.extend(page_result.get('layout', []))
                
                doc.close()
                
            except ImportError:
                print("[OCR] PyMuPDF not available, using pdf2image")
                # Try pdf2image
                import pdf2image
                images = pdf2image.convert_from_bytes(file_bytes, dpi=150, first_page=1, last_page=3)
                
                for i, image in enumerate(images):
                    temp_path = f"/tmp/pdf_page_{i}_{id(self)}.png"
                    temp_files.append(temp_path)
                    if image.mode in ('RGBA', 'P'):
                        image = image.convert('RGB')
                    image.save(temp_path, 'PNG')
                    
                    page_result = self.process_image(temp_path)
                    if page_result.get('text'):
                        all_text.append(f"--- Page {i + 1} ---")
                        all_text.append(page_result['text'])
                        all_layout.extend(page_result.get('layout', []))
            
            combined_text = '\n'.join(all_text)
            quality_scores = [item.get('confidence', 0.5) for item in all_layout]
            quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.85  # Higher default for text extraction
            
            print(f"[OCR] PDF processed: {len(combined_text)} chars extracted, quality: {quality_score:.2f}")
            
            return {
                'text': combined_text,
                'text_lines': combined_text.split('\n'),
                'layout': all_layout,
                'language': self._detect_language(combined_text.split('\n')),
                'quality_score': quality_score
            }
            
        except Exception as e:
            print(f"[OCR] PDF processing error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'text': '',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'quality_score': 0.0
            }
        finally:
            # Cleanup all temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as cleanup_error:
                    print(f"[OCR] Cleanup error for {temp_file}: {cleanup_error}")
    
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