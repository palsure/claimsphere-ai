import { useState, useEffect } from 'react';
import { claimsAPI } from '@/utils/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line } from 'recharts';
import styles from './ClaimAnalytics.module.css';

interface ClaimAnalyticsProps {
  claims: any[];
  refreshKey: number;
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea'];

export default function ClaimAnalytics({ claims, refreshKey }: ClaimAnalyticsProps) {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, [claims, refreshKey]);

  const fetchAnalytics = async () => {
    if (claims.length === 0) {
      setAnalytics(null);
      return;
    }

    setLoading(true);
    try {
      const data = await claimsAPI.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!analytics || claims.length === 0) {
    return (
      <div className={styles.card}>
        <h2>📊 Analytics</h2>
        <p className={styles.empty}>Upload some claims to see analytics!</p>
      </div>
    );
  }

  // Prepare data for charts
  const typeData = Object.entries(analytics.type_breakdown || {}).map(([name, value]) => ({
    name: name.toUpperCase(),
    value: Number(value),
  }));

  const statusData = Object.entries(analytics.status_breakdown || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    value: Number(value),
  }));

  const monthlyData = (analytics.monthly_trends || []).map((item: any) => ({
    month: item.month,
    count: item.count,
    total: Number(item.total),
  }));

  return (
    <div className={styles.card}>
      <h2>📊 Claims Analytics Dashboard</h2>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          <div className={styles.summary}>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Total Claims</div>
              <div className={styles.summaryValue}>{analytics.total_claims}</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Total Amount</div>
              <div className={styles.summaryValue}>${analytics.total_amount.toFixed(2)}</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Approved Amount</div>
              <div className={styles.summaryValue}>${analytics.approved_amount.toFixed(2)}</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Pending Amount</div>
              <div className={styles.summaryValue}>${analytics.pending_amount.toFixed(2)}</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Approval Rate</div>
              <div className={styles.summaryValue}>{analytics.approval_rate.toFixed(1)}%</div>
            </div>
            <div className={styles.summaryItem}>
              <div className={styles.summaryLabel}>Avg Processing Time</div>
              <div className={styles.summaryValue}>{analytics.average_processing_time.toFixed(1)} days</div>
            </div>
          </div>

          <div className={styles.charts}>
            <div className={styles.chartContainer}>
              <h3>Claims by Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className={styles.chartContainer}>
              <h3>Claims by Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {monthlyData.length > 0 && (
              <div className={styles.chartContainer}>
                <h3>Monthly Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="count" stroke="#667eea" name="Claim Count" />
                    <Line yAxisId="right" type="monotone" dataKey="total" stroke="#764ba2" name="Total Amount ($)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {analytics.top_claimants && analytics.top_claimants.length > 0 && (
              <div className={styles.chartContainer}>
                <h3>Top Claimants</h3>
                <div className={styles.claimantList}>
                  {analytics.top_claimants.slice(0, 10).map((claimant: any, index: number) => (
                    <div key={index} className={styles.claimantItem}>
                      <span className={styles.claimantName}>{claimant.claimant}</span>
                      <span className={styles.claimantAmount}>
                        ${claimant.total.toFixed(2)} ({claimant.count} claims)
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

