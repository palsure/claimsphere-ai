/**
 * Admin Analytics Dashboard
 */
import { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { adminAPI } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';
import styles from '../../styles/Analytics.module.css';

interface Analytics {
  total_claims: number;
  total_amount: number;
  approved_amount: number;
  pending_amount: number;
  denied_amount: number;
  status_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  monthly_trends: Array<{
    month: string;
    total_claims: number;
    total_amount: number;
    approved_count: number;
    approved_amount: number;
  }>;
  average_processing_time_hours: number;
  auto_approval_rate: number;
  approval_rate: number;
}

export default function AnalyticsPage() {
  const { hasRole } = useAuth();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await adminAPI.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (!hasRole('admin')) {
    return (
      <DashboardLayout title="Analytics">
        <div className={styles.accessDenied}>
          <h2>Access Denied</h2>
          <p>Only administrators can view analytics.</p>
        </div>
      </DashboardLayout>
    );
  }

  if (loading) {
    return (
      <DashboardLayout title="Analytics">
        <div className={styles.loading}>Loading analytics...</div>
      </DashboardLayout>
    );
  }

  if (!analytics) {
    return (
      <DashboardLayout title="Analytics">
        <div className={styles.error}>Failed to load analytics</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Analytics Dashboard">
      <div className={styles.container}>
        {/* Key Metrics */}
        <div className={styles.metricsGrid}>
          <div className={styles.metricCard}>
            <span className={styles.metricIcon}>📋</span>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>{analytics.total_claims}</span>
              <span className={styles.metricLabel}>Total Claims</span>
            </div>
          </div>
          
          <div className={styles.metricCard}>
            <span className={styles.metricIcon}>💰</span>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>{formatCurrency(analytics.total_amount)}</span>
              <span className={styles.metricLabel}>Total Claimed</span>
            </div>
          </div>
          
          <div className={styles.metricCard}>
            <span className={styles.metricIcon}>✅</span>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>{formatCurrency(analytics.approved_amount)}</span>
              <span className={styles.metricLabel}>Approved Amount</span>
            </div>
          </div>
          
          <div className={styles.metricCard}>
            <span className={styles.metricIcon}>⏱️</span>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>{analytics.average_processing_time_hours.toFixed(1)}h</span>
              <span className={styles.metricLabel}>Avg Processing Time</span>
            </div>
          </div>
        </div>

        {/* Rates */}
        <div className={styles.ratesGrid}>
          <div className={styles.rateCard}>
            <div className={styles.rateHeader}>
              <span>Approval Rate</span>
              <span className={styles.rateValue}>{analytics.approval_rate}%</span>
            </div>
            <div className={styles.rateBar}>
              <div 
                className={styles.rateFill} 
                style={{ width: `${analytics.approval_rate}%`, background: '#4caf50' }}
              ></div>
            </div>
          </div>
          
          <div className={styles.rateCard}>
            <div className={styles.rateHeader}>
              <span>Auto-Approval Rate</span>
              <span className={styles.rateValue}>{analytics.auto_approval_rate}%</span>
            </div>
            <div className={styles.rateBar}>
              <div 
                className={styles.rateFill} 
                style={{ width: `${analytics.auto_approval_rate}%`, background: '#4ecdc4' }}
              ></div>
            </div>
          </div>
        </div>

        {/* Breakdowns */}
        <div className={styles.breakdownsGrid}>
          {/* Status Breakdown */}
          <div className={styles.breakdownCard}>
            <h3>Claims by Status</h3>
            <div className={styles.breakdownList}>
              {Object.entries(analytics.status_breakdown).map(([status, count]) => (
                <div key={status} className={styles.breakdownItem}>
                  <span className={styles.breakdownLabel}>{status.replace('_', ' ')}</span>
                  <span className={styles.breakdownValue}>{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Category Breakdown */}
          <div className={styles.breakdownCard}>
            <h3>Claims by Category</h3>
            <div className={styles.breakdownList}>
              {Object.entries(analytics.category_breakdown).map(([category, count]) => (
                <div key={category} className={styles.breakdownItem}>
                  <span className={styles.breakdownLabel}>{category}</span>
                  <span className={styles.breakdownValue}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Monthly Trends */}
        <div className={styles.trendsCard}>
          <h3>Monthly Trends</h3>
          <div className={styles.trendsTable}>
            <div className={styles.trendsHeader}>
              <span>Month</span>
              <span>Claims</span>
              <span>Total Amount</span>
              <span>Approved</span>
              <span>Approved Amount</span>
            </div>
            {analytics.monthly_trends.map((month) => (
              <div key={month.month} className={styles.trendsRow}>
                <span>{month.month}</span>
                <span>{month.total_claims}</span>
                <span>{formatCurrency(month.total_amount)}</span>
                <span>{month.approved_count}</span>
                <span>{formatCurrency(month.approved_amount)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Amount Distribution */}
        <div className={styles.distributionCard}>
          <h3>Amount Distribution</h3>
          <div className={styles.distributionBars}>
            <div className={styles.distributionItem}>
              <div className={styles.distributionLabel}>
                <span>Approved</span>
                <span>{formatCurrency(analytics.approved_amount)}</span>
              </div>
              <div className={styles.distributionBar}>
                <div 
                  className={styles.distributionFill}
                  style={{ 
                    width: `${(analytics.approved_amount / analytics.total_amount) * 100}%`,
                    background: '#4caf50'
                  }}
                ></div>
              </div>
            </div>
            
            <div className={styles.distributionItem}>
              <div className={styles.distributionLabel}>
                <span>Pending</span>
                <span>{formatCurrency(analytics.pending_amount)}</span>
              </div>
              <div className={styles.distributionBar}>
                <div 
                  className={styles.distributionFill}
                  style={{ 
                    width: `${(analytics.pending_amount / analytics.total_amount) * 100}%`,
                    background: '#ffc107'
                  }}
                ></div>
              </div>
            </div>
            
            <div className={styles.distributionItem}>
              <div className={styles.distributionLabel}>
                <span>Denied</span>
                <span>{formatCurrency(analytics.denied_amount)}</span>
              </div>
              <div className={styles.distributionBar}>
                <div 
                  className={styles.distributionFill}
                  style={{ 
                    width: `${(analytics.denied_amount / analytics.total_amount) * 100}%`,
                    background: '#f44336'
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

