"""
Basic tests for OCR processor
"""
import unittest
from backend.ocr_processor import OCRProcessor


class TestOCRProcessor(unittest.TestCase):
    """Test OCR processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = OCRProcessor(lang='en')
    
    def test_processor_initialization(self):
        """Test that processor initializes correctly"""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.ocr)
    
    def test_language_detection(self):
        """Test language detection"""
        # Test English
        english_text = ["Hello", "World", "Test"]
        lang = self.processor._detect_language(english_text)
        self.assertEqual(lang, 'en')
        
        # Test Chinese
        chinese_text = ["你好", "世界", "测试"]
        lang = self.processor._detect_language(chinese_text)
        self.assertIn(lang, ['ch', 'multi'])


if __name__ == '__main__':
    unittest.main()

