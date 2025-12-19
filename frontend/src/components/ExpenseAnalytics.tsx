import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import styles from './ExpenseAnalytics.module.css';

interface ExpenseAnalyticsProps {
  expenses: any[];
  refreshKey: number;
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea'];

export default function ExpenseAnalytics({ expenses, refreshKey }: ExpenseAnalyticsProps) {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, [expenses, refreshKey]);

  const fetchAnalytics = async () => {
    if (expenses.length === 0) {
      setAnalytics(null);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get('/api/expenses/analytics');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!analytics || expenses.length === 0) {
    return (
      <div className={styles.card}>
        <h2>📊 Analytics</h2>
        <p className={styles.empty}>Upload some expenses to see analytics!</p>
      </div>
    );
  }

  // Prepare data for charts
  const categoryData = Object.entries(analytics.category_breakdown || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    value: Number(value),
  }));

  const monthlyData = (analytics.monthly_trends || []).map((item: any) => ({
    month: item.month,
    total: Number(item.total),
  }));

  return (
    <div className={styles.card}>
      <h2>📊 Analytics Dashboard</h2>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          <div className={styles.summary}>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Total Expenses</div>
              <div className={styles.summaryValue}>
                ${analytics.total_expenses.toFixed(2)}
              </div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Number of Expenses</div>
              <div className={styles.summaryValue}>{analytics.expense_count}</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Tax Deductible</div>
              <div className={styles.summaryValue}>
                ${analytics.tax_deductible_total.toFixed(2)}
              </div>
            </div>
          </div>

          <div className={styles.charts}>
            <div className={styles.chartContainer}>
              <h3>Spending by Category</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {monthlyData.length > 0 && (
              <div className={styles.chartContainer}>
                <h3>Monthly Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                    <Legend />
                    <Bar dataKey="total" fill="#667eea" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {analytics.top_merchants && analytics.top_merchants.length > 0 && (
              <div className={styles.chartContainer}>
                <h3>Top Merchants</h3>
                <div className={styles.merchantList}>
                  {analytics.top_merchants.slice(0, 10).map((merchant: any, index: number) => (
                    <div key={index} className={styles.merchantItem}>
                      <span className={styles.merchantName}>{merchant.merchant}</span>
                      <span className={styles.merchantAmount}>
                        ${merchant.total.toFixed(2)} ({merchant.count} transactions)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

