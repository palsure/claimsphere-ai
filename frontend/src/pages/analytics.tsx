import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import { claimsAPI } from '@/utils/api';
import styles from '@/styles/Analytics.module.css';

interface ClaimStats {
  total: number;
  pending: number;
  approved: number;
  denied: number;
  totalAmount: number;
  approvedAmount: number;
  avgAmount: number;
  byCategory: Record<string, { count: number; amount: number }>;
}

export default function AnalyticsPage() {
  const { user } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [stats, setStats] = useState<ClaimStats>({
    total: 0,
    pending: 0,
    approved: 0,
    denied: 0,
    totalAmount: 0,
    approvedAmount: 0,
    avgAmount: 0,
    byCategory: {},
  });
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const data = await claimsAPI.list({ page_size: 100 });
      const claimsData = Array.isArray(data) ? data : (data.claims || data || []);
      setClaims(claimsData);
      calculateStats(claimsData);
    } catch (error) {
      console.error('Error fetching claims:', error);
      setClaims([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const calculateStats = (claimsData: any[]) => {
    const byCategory: Record<string, { count: number; amount: number }> = {};

    claimsData.forEach(claim => {
      // By category
      const category = claim.category || 'other';
      if (!byCategory[category]) {
        byCategory[category] = { count: 0, amount: 0 };
      }
      byCategory[category].count++;
      byCategory[category].amount += claim.total_amount || 0;
    });

    const totalAmount = claimsData.reduce((sum, c) => sum + (c.total_amount || 0), 0);
    const approvedClaims = claimsData.filter(c => 
      ['approved', 'auto_approved'].includes(c.status)
    );
    const approvedAmount = approvedClaims.reduce((sum, c) => 
      sum + (c.approved_amount || c.total_amount || 0), 0
    );

    const pendingStatuses = ['submitted', 'extracted', 'validated', 'pending_review', 'pended'];

    setStats({
      total: claimsData.length,
      pending: claimsData.filter(c => pendingStatuses.includes(c.status)).length,
      approved: approvedClaims.length,
      denied: claimsData.filter(c => c.status === 'denied').length,
      totalAmount,
      approvedAmount,
      avgAmount: claimsData.length > 0 ? totalAmount / claimsData.length : 0,
      byCategory,
    });
  };

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user, fetchData]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      medical: '🏥',
      dental: '🦷',
      vision: '👁️',
      pharmacy: '💊',
      mental_health: '🧠',
      hospital: '🏨',
      emergency: '🚑',
      preventive: '💉',
      other: '📄',
    };
    return icons[category] || '📄';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
      case 'auto_approved':
        return 'var(--success)';
      case 'denied':
        return 'var(--danger)';
      case 'pending_review':
      case 'pended':
        return 'var(--warning)';
      default:
        return 'var(--info)';
    }
  };

  const approvalRate = stats.total > 0 
    ? Math.round((stats.approved / stats.total) * 100) 
    : 0;

  const pendingRate = stats.total > 0 
    ? Math.round((stats.pending / stats.total) * 100) 
    : 0;

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
                      { label: 'Denied', value: stats.denied, color: 'var(--danger)' },
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

                {/* Claims by Category */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <span>🏷️</span>
                    Claims by Category
                  </h3>
                  <div className={styles.typeList}>
                    {Object.entries(stats.byCategory).length === 0 ? (
                      <p className={styles.noData}>No category data available</p>
                    ) : (
                      Object.entries(stats.byCategory)
                        .sort((a, b) => b[1].amount - a[1].amount)
                        .map(([category, data], index) => (
                          <div key={category} className={styles.typeItem}>
                            <div className={styles.typeIcon}>{getCategoryIcon(category)}</div>
                            <div className={styles.typeInfo}>
                              <span className={styles.typeName}>
                                {category.replace('_', ' ')}
                              </span>
                              <span className={styles.typeCount}>{data.count} claims</span>
                            </div>
                            <span className={styles.typeAmount}>{formatCurrency(data.amount)}</span>
                          </div>
                        ))
                    )}
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
                            strokeDasharray={`${approvalRate}, 100`}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                        </svg>
                        <span className={styles.metricValue}>{approvalRate}%</span>
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
                            strokeDasharray={`${pendingRate}, 100`}
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                        </svg>
                        <span className={styles.metricValue}>{pendingRate}%</span>
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
                          <span className={styles.recentName}>
                            {claim.claimant_name || claim.provider_name || claim.claim_number}
                          </span>
                          <span className={styles.recentType}>
                            {(claim.category || 'other').replace('_', ' ')}
                          </span>
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
