import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import { API_URL } from '@/config/api';
import styles from '@/styles/Analytics.module.css';

interface ClaimStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  underReview: number;
  totalAmount: number;
  approvedAmount: number;
  avgAmount: number;
  byType: Record<string, { count: number; amount: number }>;
  byMonth: Record<string, number>;
}

export default function AnalyticsPage() {
  const { user } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [stats, setStats] = useState<ClaimStats>({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    underReview: 0,
    totalAmount: 0,
    approvedAmount: 0,
    avgAmount: 0,
    byType: {},
    byMonth: {},
  });
  const [isLoading, setIsLoading] = useState(true);

  const fetchClaims = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_URL}/api/claims?limit=100`);
      const data = await response.json();
      const claimsData = data.claims || [];
      setClaims(claimsData);
      calculateStats(claimsData);
    } catch (error) {
      console.error('Error fetching claims:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const calculateStats = (claimsData: any[]) => {
    const byType: Record<string, { count: number; amount: number }> = {};
    const byMonth: Record<string, number> = {};

    claimsData.forEach(claim => {
      // By type
      const type = claim.claim_type || 'other';
      if (!byType[type]) {
        byType[type] = { count: 0, amount: 0 };
      }
      byType[type].count++;
      byType[type].amount += claim.total_amount || 0;

      // By month
      const date = new Date(claim.date_submitted);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      byMonth[monthKey] = (byMonth[monthKey] || 0) + 1;
    });

    const totalAmount = claimsData.reduce((sum, c) => sum + (c.total_amount || 0), 0);
    const approvedClaims = claimsData.filter(c => c.status === 'approved');
    const approvedAmount = approvedClaims.reduce((sum, c) => sum + (c.approved_amount || c.total_amount || 0), 0);

    setStats({
      total: claimsData.length,
      pending: claimsData.filter(c => c.status === 'pending').length,
      approved: approvedClaims.length,
      rejected: claimsData.filter(c => c.status === 'rejected').length,
      underReview: claimsData.filter(c => c.status === 'under_review').length,
      totalAmount,
      approvedAmount,
      avgAmount: claimsData.length > 0 ? totalAmount / claimsData.length : 0,
      byType,
      byMonth,
    });
  };

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      medical: '🏥',
      insurance: '🛡️',
      travel: '✈️',
      property: '🏠',
      business: '💼',
      other: '📄',
    };
    return icons[type] || '📄';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      approved: 'var(--success)',
      pending: 'var(--warning)',
      rejected: 'var(--danger)',
      under_review: 'var(--info)',
    };
    return colors[status] || 'var(--text-muted)';
  };

  return (
    <>
      <Head>
        <title>Analytics | ClaimSphere AI</title>
        <meta name="description" content="Claims analytics and insights" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <h1 className={styles.title}>
              <span>📈</span>
              Analytics Dashboard
            </h1>
            <p className={styles.subtitle}>
              Insights and metrics for your claims data
            </p>
          </div>

          {isLoading ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Loading analytics...</p>
            </div>
          ) : claims.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>📊</div>
              <h2>No Data Available</h2>
              <p>Upload some claims to see analytics</p>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                  <div className={styles.statIcon}>📋</div>
                  <div className={styles.statContent}>
                    <span className={styles.statValue}>{stats.total}</span>
                    <span className={styles.statLabel}>Total Claims</span>
                  </div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statIcon}>💰</div>
                  <div className={styles.statContent}>
                    <span className={styles.statValue}>{formatCurrency(stats.totalAmount)}</span>
                    <span className={styles.statLabel}>Total Amount</span>
                  </div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statIcon}>✅</div>
                  <div className={styles.statContent}>
                    <span className={styles.statValue}>{formatCurrency(stats.approvedAmount)}</span>
                    <span className={styles.statLabel}>Approved Amount</span>
                  </div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statIcon}>📊</div>
                  <div className={styles.statContent}>
                    <span className={styles.statValue}>{formatCurrency(stats.avgAmount)}</span>
                    <span className={styles.statLabel}>Average Claim</span>
                  </div>
                </div>
              </div>

              {/* Main Grid */}
              <div className={styles.mainGrid}>
                {/* Status Distribution */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <span>📊</span>
                    Status Distribution
                  </h3>
                  <div className={styles.statusChart}>
                    {[
                      { label: 'Approved', value: stats.approved, color: 'var(--success)' },
                      { label: 'Pending', value: stats.pending, color: 'var(--warning)' },
                      { label: 'Rejected', value: stats.rejected, color: 'var(--danger)' },
                      { label: 'Under Review', value: stats.underReview, color: 'var(--info)' },
                    ].map((item, index) => (
                      <div key={index} className={styles.statusItem}>
                        <div className={styles.statusInfo}>
                          <div 
                            className={styles.statusDot} 
                            style={{ background: item.color }}
                          ></div>
                          <span className={styles.statusLabel}>{item.label}</span>
                        </div>
                        <div className={styles.statusBarWrapper}>
                          <div 
                            className={styles.statusBar}
                            style={{ 
                              width: `${stats.total > 0 ? (item.value / stats.total) * 100 : 0}%`,
                              background: item.color
                            }}
                          ></div>
                        </div>
                        <span className={styles.statusValue}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Claims by Type */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <span>🏷️</span>
                    Claims by Type
                  </h3>
                  <div className={styles.typeList}>
                    {Object.entries(stats.byType)
                      .sort((a, b) => b[1].amount - a[1].amount)
                      .map(([type, data], index) => (
                        <div key={type} className={styles.typeItem}>
                          <div className={styles.typeIcon}>{getTypeIcon(type)}</div>
                          <div className={styles.typeInfo}>
                            <span className={styles.typeName}>{type}</span>
                            <span className={styles.typeCount}>{data.count} claims</span>
                          </div>
                          <span className={styles.typeAmount}>{formatCurrency(data.amount)}</span>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Approval Rate */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <span>✅</span>
                    Approval Metrics
                  </h3>
                  <div className={styles.metricsGrid}>
                    <div className={styles.metricItem}>
                      <div className={styles.metricCircle}>
                        <svg viewBox="0 0 36 36" className={styles.circularChart}>
                          <path
                            className={styles.circleBg}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                          <path
                            className={styles.circle}
                            strokeDasharray={`${stats.total > 0 ? (stats.approved / stats.total) * 100 : 0}, 100`}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                        </svg>
                        <span className={styles.metricValue}>
                          {stats.total > 0 ? Math.round((stats.approved / stats.total) * 100) : 0}%
                        </span>
                      </div>
                      <span className={styles.metricLabel}>Approval Rate</span>
                    </div>
                    <div className={styles.metricItem}>
                      <div className={styles.metricCircle}>
                        <svg viewBox="0 0 36 36" className={styles.circularChart}>
                          <path
                            className={styles.circleBg}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                          <path
                            className={styles.circleWarning}
                            strokeDasharray={`${stats.total > 0 ? (stats.pending / stats.total) * 100 : 0}, 100`}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                        </svg>
                        <span className={styles.metricValue}>
                          {stats.total > 0 ? Math.round((stats.pending / stats.total) * 100) : 0}%
                        </span>
                      </div>
                      <span className={styles.metricLabel}>Pending Rate</span>
                    </div>
                  </div>
                </div>

                {/* Recent Claims Summary */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <span>📋</span>
                    Recent Claims
                  </h3>
                  <div className={styles.recentList}>
                    {claims.slice(0, 5).map((claim, index) => (
                      <div key={claim.id || index} className={styles.recentItem}>
                        <div className={styles.recentInfo}>
                          <span className={styles.recentName}>{claim.claimant_name}</span>
                          <span className={styles.recentType}>{claim.claim_type}</span>
                        </div>
                        <div className={styles.recentMeta}>
                          <span 
                            className={styles.recentStatus}
                            style={{ color: getStatusColor(claim.status) }}
                          >
                            {claim.status?.replace('_', ' ')}
                          </span>
                          <span className={styles.recentAmount}>
                            {formatCurrency(claim.total_amount || 0)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </>
  );
}

