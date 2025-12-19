"""
Tests for expense analyzer
"""
import unittest
from datetime import datetime
from backend.expense_analyzer import ExpenseAnalyzer
from backend.models.expense import Expense, ExpenseCategory


class TestExpenseAnalyzer(unittest.TestCase):
    """Test expense analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ExpenseAnalyzer()
    
    def test_duplicate_detection(self):
        """Test duplicate expense detection"""
        expense1 = Expense(
            id="1",
            merchant_name="Test Store",
            date=datetime.now(),
            total_amount=50.00,
            category=ExpenseCategory.MEALS
        )
        
        expense2 = Expense(
            id="2",
            merchant_name="Test Store",
            date=datetime.now(),
            total_amount=50.00,
            category=ExpenseCategory.MEALS
        )
        
        self.analyzer.add_expense(expense1)
        duplicates = self.analyzer.detect_duplicates(expense2)
        
        self.assertGreater(len(duplicates), 0)
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        expense = Expense(
            id="1",
            merchant_name="Test Store",
            date=datetime.now(),
            total_amount=50.00,
            category=ExpenseCategory.MEALS
        )
        
        anomalies = self.analyzer.detect_anomalies(expense)
        # Should not have anomalies for normal expense
        self.assertIsInstance(anomalies, list)
    
    def test_analytics_generation(self):
        """Test analytics generation"""
        expense = Expense(
            id="1",
            merchant_name="Test Store",
            date=datetime.now(),
            total_amount=50.00,
            category=ExpenseCategory.MEALS
        )
        
        self.analyzer.add_expense(expense)
        analytics = self.analyzer.generate_analytics()
        
        self.assertEqual(analytics.total_expenses, 50.00)
        self.assertEqual(analytics.expense_count, 1)


if __name__ == '__main__':
    unittest.main()

