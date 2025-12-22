import { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './ExpenseList.module.css';
import { format, isValid, parseISO } from 'date-fns';

// Safe date formatting helper
const formatSafeDate = (dateStr: string | null | undefined, formatStr: string = 'MMM dd, yyyy'): string => {
  if (!dateStr) return 'N/A';
  try {
    let date = parseISO(dateStr);
    if (!isValid(date)) date = new Date(dateStr);
    if (!isValid(date)) return 'N/A';
    return format(date, formatStr);
  } catch {
    return 'N/A';
  }
};

// Safe date comparison helper
const getDateTimestamp = (dateStr: string | null | undefined): number => {
  if (!dateStr) return 0;
  try {
    const date = parseISO(dateStr);
    if (isValid(date)) return date.getTime();
    const fallbackDate = new Date(dateStr);
    if (isValid(fallbackDate)) return fallbackDate.getTime();
    return 0;
  } catch {
    return 0;
  }
};

interface Expense {
  id: string;
  merchant_name: string;
  date: string;
  total_amount: number;
  currency: string;
  category: string;
  tax_amount?: number;
  is_duplicate?: boolean;
  status: string;
}

interface ExpenseListProps {
  expenses: Expense[];
  refreshKey: number;
  onRefresh: () => void;
}

export default function ExpenseList({ expenses, refreshKey, onRefresh }: ExpenseListProps) {
  const [filteredExpenses, setFilteredExpenses] = useState<Expense[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    onRefresh();
  }, [refreshKey]);

  useEffect(() => {
    let filtered = [...expenses];

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(exp => exp.category === categoryFilter);
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(exp =>
        exp.merchant_name.toLowerCase().includes(term) ||
        exp.category.toLowerCase().includes(term)
      );
    }

    // Sort by date (newest first) using safe comparison
    filtered.sort((a, b) => getDateTimestamp(b.date) - getDateTimestamp(a.date));

    setFilteredExpenses(filtered);
  }, [expenses, categoryFilter, searchTerm]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    try {
      await axios.delete(`/api/expenses/${id}`);
      onRefresh();
    } catch (error) {
      console.error('Error deleting expense:', error);
      alert('Error deleting expense');
    }
  };

  const categories = ['all', 'meals', 'travel', 'office_supplies', 'utilities', 'software', 'marketing', 'professional_services', 'rent', 'insurance', 'other'];

  return (
    <div className={styles.card}>
      <h2>📋 Expense List</h2>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Search expenses..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="input"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat.replace('_', ' ').toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.stats}>
        <span>Total: {filteredExpenses.length} expenses</span>
        <span>Total Amount: ${filteredExpenses.reduce((sum, exp) => sum + exp.total_amount, 0).toFixed(2)}</span>
      </div>

      <div className={styles.expenseList}>
        {filteredExpenses.length === 0 ? (
          <p className={styles.empty}>No expenses found. Upload a receipt to get started!</p>
        ) : (
          filteredExpenses.map(expense => (
            <div
              key={expense.id}
              className={`${styles.expenseItem} ${expense.is_duplicate ? styles.duplicate : ''}`}
            >
              <div className={styles.expenseHeader}>
                <h3>{expense.merchant_name}</h3>
                <span className={styles.amount}>
                  {expense.currency} {expense.total_amount.toFixed(2)}
                </span>
              </div>
              <div className={styles.expenseDetails}>
                <span className={styles.category}>{expense.category}</span>
                <span className={styles.date}>
                  {formatSafeDate(expense.date)}
                </span>
                {expense.tax_amount && (
                  <span className={styles.tax}>Tax: {expense.currency} {expense.tax_amount.toFixed(2)}</span>
                )}
                {expense.is_duplicate && (
                  <span className={styles.duplicateBadge}>⚠️ Potential Duplicate</span>
                )}
              </div>
              <button
                onClick={() => handleDelete(expense.id)}
                className={styles.deleteBtn}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

