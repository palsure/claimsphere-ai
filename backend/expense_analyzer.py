"""
Business logic for expense analysis, duplicate detection, and analytics
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from backend.models.expense import Expense, ExpenseCategory, ExpenseAnalytics
from backend.utils import normalize_merchant_name


class ExpenseAnalyzer:
    """Analyze expenses for duplicates, anomalies, and generate insights"""
    
    def __init__(self):
        self.expenses: List[Expense] = []
    
    def add_expense(self, expense: Expense):
        """Add an expense to the analyzer"""
        self.expenses.append(expense)
    
    def detect_duplicates(self, expense: Expense, threshold: float = 0.95) -> List[Expense]:
        """
        Detect duplicate expenses
        
        Args:
            expense: Expense to check for duplicates
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of duplicate expenses
        """
        duplicates = []
        
        for existing_expense in self.expenses:
            if existing_expense.id == expense.id:
                continue
            
            similarity = self._calculate_similarity(expense, existing_expense)
            if similarity >= threshold:
                duplicates.append(existing_expense)
        
        return duplicates
    
    def _calculate_similarity(self, exp1: Expense, exp2: Expense) -> float:
        """
        Calculate similarity between two expenses
        
        Args:
            exp1: First expense
            exp2: Second expense
            
        Returns:
            Similarity score (0-1)
        """
        score = 0.0
        factors = 0
        
        # Merchant name similarity (using normalized names)
        if exp1.merchant_name and exp2.merchant_name:
            norm1 = normalize_merchant_name(exp1.merchant_name)
            norm2 = normalize_merchant_name(exp2.merchant_name)
            merchant_sim = self._string_similarity(norm1, norm2)
            score += merchant_sim * 0.3
            factors += 0.3
        
        # Amount similarity (within 1%)
        if exp1.total_amount and exp2.total_amount:
            amount_diff = abs(exp1.total_amount - exp2.total_amount)
            amount_avg = (exp1.total_amount + exp2.total_amount) / 2
            if amount_avg > 0:
                amount_sim = max(0, 1 - (amount_diff / amount_avg))
                score += amount_sim * 0.4
                factors += 0.4
        
        # Date similarity (within 1 day)
        if exp1.date and exp2.date:
            date_diff = abs((exp1.date - exp2.date).days)
            date_sim = max(0, 1 - (date_diff / 1.0))  # 1 day tolerance
            score += date_sim * 0.3
            factors += 0.3
        
        return score / factors if factors > 0 else 0.0
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Simple string similarity using Levenshtein-like approach"""
        if s1 == s2:
            return 1.0
        
        # Check if one contains the other
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # Simple character overlap
        set1 = set(s1.lower())
        set2 = set(s2.lower())
        if len(set1) == 0 and len(set2) == 0:
            return 1.0
        if len(set1) == 0 or len(set2) == 0:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def detect_anomalies(self, expense: Expense) -> List[str]:
        """
        Detect anomalies in an expense
        
        Args:
            expense: Expense to check
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        # Check for unusually high amounts
        if expense.total_amount > 0:
            avg_amount = self._get_average_amount()
            if avg_amount > 0 and expense.total_amount > avg_amount * 3:
                anomalies.append(f"Unusually high amount: ${expense.total_amount:.2f} (avg: ${avg_amount:.2f})")
        
        # Check for future dates
        if expense.date > datetime.now():
            anomalies.append("Expense date is in the future")
        
        # Check for very old dates (more than 1 year)
        if expense.date < datetime.now() - timedelta(days=365):
            anomalies.append("Expense date is more than 1 year old")
        
        # Check for negative amounts
        if expense.total_amount < 0:
            anomalies.append("Negative amount detected")
        
        # Check for missing merchant name
        if not expense.merchant_name or expense.merchant_name.strip() == "":
            anomalies.append("Missing merchant name")
        
        return anomalies
    
    def _get_average_amount(self) -> float:
        """Calculate average expense amount"""
        if not self.expenses:
            return 0.0
        
        total = sum(exp.total_amount for exp in self.expenses)
        return total / len(self.expenses)
    
    def generate_analytics(self, date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None) -> ExpenseAnalytics:
        """
        Generate analytics for expenses
        
        Args:
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            ExpenseAnalytics object
        """
        # Filter expenses by date range
        filtered_expenses = self.expenses
        if date_from:
            filtered_expenses = [e for e in filtered_expenses if e.date >= date_from]
        if date_to:
            filtered_expenses = [e for e in filtered_expenses if e.date <= date_to]
        
        if not filtered_expenses:
            return ExpenseAnalytics(
                total_expenses=0.0,
                expense_count=0,
                category_breakdown={},
                monthly_trends=[],
                top_merchants=[],
                tax_deductible_total=0.0
            )
        
        # Calculate totals
        total_expenses = sum(exp.total_amount for exp in filtered_expenses)
        expense_count = len(filtered_expenses)
        
        # Category breakdown
        category_breakdown = defaultdict(float)
        for exp in filtered_expenses:
            category = exp.category.value if exp.category else "other"
            category_breakdown[category] += exp.total_amount
        
        # Monthly trends
        monthly_trends = self._calculate_monthly_trends(filtered_expenses)
        
        # Top merchants
        top_merchants = self._get_top_merchants(filtered_expenses, limit=10)
        
        # Tax deductible total (simplified: assume meals, travel, office supplies are deductible)
        tax_deductible_categories = [
            ExpenseCategory.MEALS,
            ExpenseCategory.TRAVEL,
            ExpenseCategory.OFFICE_SUPPLIES,
            ExpenseCategory.SOFTWARE,
            ExpenseCategory.PROFESSIONAL_SERVICES
        ]
        tax_deductible_total = sum(
            exp.total_amount for exp in filtered_expenses
            if exp.category in tax_deductible_categories
        )
        
        return ExpenseAnalytics(
            total_expenses=total_expenses,
            expense_count=expense_count,
            category_breakdown=dict(category_breakdown),
            monthly_trends=monthly_trends,
            top_merchants=top_merchants,
            tax_deductible_total=tax_deductible_total
        )
    
    def _calculate_monthly_trends(self, expenses: List[Expense]) -> List[Dict]:
        """Calculate monthly spending trends"""
        monthly_data = defaultdict(float)
        
        for exp in expenses:
            month_key = exp.date.strftime("%Y-%m")
            monthly_data[month_key] += exp.total_amount
        
        trends = [
            {"month": month, "total": total}
            for month, total in sorted(monthly_data.items())
        ]
        
        return trends
    
    def _get_top_merchants(self, expenses: List[Expense], limit: int = 10) -> List[Dict]:
        """Get top merchants by spending"""
        merchant_totals = defaultdict(float)
        merchant_counts = defaultdict(int)
        
        for exp in expenses:
            merchant = exp.merchant_name or "Unknown"
            merchant_totals[merchant] += exp.total_amount
            merchant_counts[merchant] += 1
        
        top_merchants = sorted(
            merchant_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                "merchant": merchant,
                "total": total,
                "count": merchant_counts[merchant]
            }
            for merchant, total in top_merchants
        ]

