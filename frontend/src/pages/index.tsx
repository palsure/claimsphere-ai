import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ClaimUpload from '@/components/ClaimUpload';
import ClaimList from '@/components/ClaimList';
import ClaimAnalytics from '@/components/ClaimAnalytics';
import NaturalLanguageQuery from '@/components/NaturalLanguageQuery';
import styles from '@/styles/Home.module.css';

interface ClaimStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  totalAmount: number;
}

export default function Home() {
  const { user } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [stats, setStats] = useState<ClaimStats>({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    totalAmount: 0,
  });

  const fetchClaims = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/claims?limit=100`);
      const data = await response.json();
      const claimsData = data.claims || [];
      setClaims(claimsData);

      // Calculate stats
      const newStats: ClaimStats = {
        total: claimsData.length,
        pending: claimsData.filter((c: any) => c.status === 'pending').length,
        approved: claimsData.filter((c: any) => c.status === 'approved').length,
        rejected: claimsData.filter((c: any) => c.status === 'rejected').length,
        totalAmount: claimsData.reduce((sum: number, c: any) => sum + (c.total_amount || 0), 0),
      };
      setStats(newStats);
    } catch (error) {
      console.error('Error fetching claims:', error);
    }
  }, []);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const handleClaimAdded = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    fetchClaims();
  }, [fetchClaims]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <>
      <Head>
        <title>Dashboard | ClaimSphere AI</title>
        <meta name="description" content="AI-powered automated claim processing system" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <p className={styles.greeting}>
              <span>👋</span>
              {getGreeting()}, {user?.name?.split(' ')[0] || 'there'}
            </p>
            <h1 className={styles.title}>Claims Dashboard</h1>
            <p className={styles.subtitle}>
              Monitor, process, and analyze your claims with AI-powered insights
            </p>
          </div>

          {/* Stats Grid */}
          <div className={styles.statsGrid}>
            <div className={`${styles.statCard} ${styles.primary}`}>
              <div className={`${styles.statIcon} ${styles.primary}`}>
                📋
              </div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Total Claims</div>
                <div className={styles.statValue}>{stats.total}</div>
                <div className={`${styles.statChange} ${styles.up}`}>
                  <span>↑</span> 12% this week
                </div>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.warning}`}>
              <div className={`${styles.statIcon} ${styles.warning}`}>
                ⏳
              </div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Pending Review</div>
                <div className={styles.statValue}>{stats.pending}</div>
                <div className={`${styles.statChange} ${styles.down}`}>
                  <span>↓</span> 5% from yesterday
                </div>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.success}`}>
              <div className={`${styles.statIcon} ${styles.success}`}>
                ✅
              </div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Approved</div>
                <div className={styles.statValue}>{stats.approved}</div>
                <div className={`${styles.statChange} ${styles.up}`}>
                  <span>↑</span> 8% this month
                </div>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.primary}`}>
              <div className={`${styles.statIcon} ${styles.primary}`}>
                💰
              </div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Total Amount</div>
                <div className={styles.statValue}>{formatCurrency(stats.totalAmount)}</div>
                <div className={`${styles.statChange} ${styles.up}`}>
                  <span>↑</span> 15% this quarter
                </div>
              </div>
            </div>
          </div>

          {/* Main Grid */}
          <div className={styles.mainGrid}>
            <div className={styles.leftColumn}>
              {/* Upload Section */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>📤</span>
                    Upload Claim Document
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <ClaimUpload onClaimAdded={handleClaimAdded} />
                </div>
              </div>

              {/* Claims List */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>📋</span>
                    Recent Claims
                  </h2>
                  <div className={styles.sectionActions}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={fetchClaims}
                    >
                      Refresh
                    </button>
                  </div>
                </div>
                <div className={styles.sectionBody}>
                  <ClaimList
                    claims={claims}
                    refreshKey={refreshKey}
                    onRefresh={fetchClaims}
                  />
                </div>
              </div>

              {/* Analytics */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>📊</span>
                    Analytics Overview
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <ClaimAnalytics claims={claims} refreshKey={refreshKey} />
                </div>
              </div>
            </div>

            <div className={styles.rightColumn}>
              {/* Quick Actions */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>⚡</span>
                    Quick Actions
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <div className={styles.quickActions}>
                    <Link href="#upload" className={styles.quickAction}>
                      <div className={styles.quickActionIcon}>📄</div>
                      <span className={styles.quickActionLabel}>New Claim</span>
                    </Link>
                    <Link href="#claims" className={styles.quickAction}>
                      <div className={styles.quickActionIcon}>🔍</div>
                      <span className={styles.quickActionLabel}>Search Claims</span>
                    </Link>
                    <Link href="#analytics" className={styles.quickAction}>
                      <div className={styles.quickActionIcon}>📈</div>
                      <span className={styles.quickActionLabel}>View Reports</span>
                    </Link>
                    <Link href="#settings" className={styles.quickAction}>
                      <div className={styles.quickActionIcon}>⚙️</div>
                      <span className={styles.quickActionLabel}>Settings</span>
                    </Link>
                  </div>
                </div>
              </div>

              {/* AI Assistant */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>🤖</span>
                    AI Assistant
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <NaturalLanguageQuery claims={claims} />
                </div>
              </div>

              {/* Recent Activity */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>🕐</span>
                    Recent Activity
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <div className={styles.activityList}>
                    {claims.slice(0, 5).map((claim, index) => (
                      <div key={claim.id || index} className={styles.activityItem}>
                        <div className={`${styles.activityIcon} ${
                          claim.status === 'approved' ? styles.success :
                          claim.status === 'rejected' ? styles.danger : styles.info
                        }`}>
                          {claim.status === 'approved' ? '✅' :
                           claim.status === 'rejected' ? '❌' : '📋'}
                        </div>
                        <div className={styles.activityContent}>
                          <div className={styles.activityText}>
                            Claim <strong>{claim.claim_number || 'N/A'}</strong>
                            {' '}was {claim.status || 'submitted'}
                          </div>
                          <div className={styles.activityTime}>
                            {claim.date_submitted ?
                              new Date(claim.date_submitted).toLocaleDateString() :
                              'Just now'}
                          </div>
                        </div>
                      </div>
                    ))}
                    {claims.length === 0 && (
                      <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>
                        No recent activity. Upload a claim to get started!
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
