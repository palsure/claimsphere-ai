import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import ClaimUpload from '@/components/ClaimUpload';
import ClaimList from '@/components/ClaimList';
import { claimsAPI } from '@/utils/api';
import styles from '@/styles/Claims.module.css';

export default function ClaimsPage() {
  const { user, isAgent, isAdmin, hasAnyRole } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is a regular user (not agent or admin)
  const isRegularUser = !isAgent && !isAdmin;
  const canAccessQueue = hasAnyRole(['agent', 'admin']);

  const fetchClaims = useCallback(async () => {
    // Only fetch if we have a token
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const data = await claimsAPI.list({ page_size: 100 });
      // Handle both array and object response
      const claimsData = Array.isArray(data) ? data : (data.claims || data || []);
      console.log('Fetched claims:', claimsData.length, claimsData);
      setClaims(claimsData);
    } catch (error) {
      console.error('Error fetching claims:', error);
      setClaims([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchClaims();
    }
  }, [user, fetchClaims]);

  const handleClaimAdded = useCallback(() => {
    console.log('Claim added, refreshing...');
    setRefreshKey(prev => prev + 1);
    // Small delay to ensure DB is updated
    setTimeout(() => {
      fetchClaims();
    }, 500);
  }, [fetchClaims]);

  // Calculate stats with correct status values
  const stats = {
    total: claims.length,
    pending: claims.filter(c => 
      ['pending_review', 'submitted', 'extracted', 'validated', 'pended'].includes(c.status)
    ).length,
    approved: claims.filter(c => 
      ['approved', 'auto_approved'].includes(c.status)
    ).length,
    denied: claims.filter(c => c.status === 'denied').length,
    totalAmount: claims.reduce((sum, c) => sum + (c.total_amount || 0), 0),
  };

  // Get page title based on role
  const getPageTitle = () => {
    if (isAdmin) return 'All Claims';
    if (isAgent) return 'Claims Queue';
    return 'My Claims';
  };

  const getPageSubtitle = () => {
    if (isAdmin) return 'View and manage all claims across the system';
    if (isAgent) return 'Review and process claims assigned to you';
    return 'Upload, track, and manage your insurance claims';
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
        <title>{getPageTitle()} | ClaimSphere AI</title>
        <meta name="description" content="Manage and process claims" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <h1 className={styles.title}>
                <span>📋</span>
                {getPageTitle()}
              </h1>
              <p className={styles.subtitle}>
                {getPageSubtitle()}
              </p>
            </div>
            <div className={styles.headerStats}>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{stats.total}</span>
                <span className={styles.statLabel}>Total</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{stats.pending}</span>
                <span className={styles.statLabel}>Pending</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{stats.approved}</span>
                <span className={styles.statLabel}>Approved</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{formatCurrency(stats.totalAmount)}</span>
                <span className={styles.statLabel}>Total Amount</span>
              </div>
            </div>
          </div>

          <div className={styles.grid}>
            {/* Upload Section - Only for regular users */}
            {isRegularUser && (
              <div className={styles.uploadSection}>
                <div className={styles.sectionCard}>
                  <div className={styles.sectionHeader}>
                    <h2>
                      <span>📤</span>
                      Submit New Claim
                    </h2>
                    <p className={styles.sectionSubtitle}>
                      Upload a document to create a new claim
                    </p>
                  </div>
                  <div className={styles.sectionBody}>
                    <ClaimUpload onClaimAdded={handleClaimAdded} />
                  </div>
                </div>
              </div>
            )}

            {/* Claims List Section */}
            <div className={isRegularUser ? styles.listSection : styles.listSectionFull}>
              <div className={styles.sectionCard}>
                <div className={styles.sectionHeader}>
                  <h2>
                    <span>📑</span>
                    {isRegularUser ? 'My Claims' : 'All Claims'}
                  </h2>
                  <button 
                    className={styles.refreshBtn}
                    onClick={fetchClaims}
                    disabled={isLoading}
                  >
                    {isLoading ? '⟳ Loading...' : '⟳ Refresh'}
                  </button>
                </div>
                <div className={styles.sectionBody}>
                  {isLoading ? (
                    <div className={styles.loadingState}>
                      <div className={styles.spinner}></div>
                      <p>Loading claims...</p>
                    </div>
                  ) : claims.length === 0 ? (
                    <div className={styles.emptyState}>
                      <span className={styles.emptyIcon}>📋</span>
                      <h3>No Claims Yet</h3>
                      <p>
                        {isRegularUser 
                          ? 'Upload a document above to submit your first claim!'
                          : 'No claims in the system yet.'}
                      </p>
                    </div>
                  ) : (
                    <ClaimList 
                      claims={claims} 
                      refreshKey={refreshKey}
                      onRefresh={fetchClaims}
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
