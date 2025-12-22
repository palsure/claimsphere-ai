import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { claimsAPI } from '@/utils/api';
import NaturalLanguageQuery from '@/components/NaturalLanguageQuery';
import styles from '@/styles/Home.module.css';

interface ClaimStats {
  total: number;
  pending: number;
  approved: number;
  denied: number;
  pended: number;
  totalAmount: number;
  avgProcessingTime: number;
}

type ClaimFilter = 'all' | 'pending' | 'approved' | 'denied' | 'pended';

export default function Home() {
  const { user, isAgent, isAdmin, hasAnyRole } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [claimFilter, setClaimFilter] = useState<ClaimFilter>('all');
  const [stats, setStats] = useState<ClaimStats>({
    total: 0,
    pending: 0,
    approved: 0,
    denied: 0,
    pended: 0,
    totalAmount: 0,
    avgProcessingTime: 0,
  });

  const canAccessQueue = hasAnyRole(['agent', 'admin']);
  const canAccessManagement = hasAnyRole(['agent', 'admin']);
  const isRegularUser = !isAgent && !isAdmin;

  const fetchClaims = useCallback(async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    try {
      const data = await claimsAPI.list({ page_size: 100 });
      const claimsData = Array.isArray(data) ? data : (data.claims || data || []);
      setClaims(claimsData);

      // Calculate stats
      const newStats: ClaimStats = {
        total: claimsData.length,
        pending: claimsData.filter((c: any) => 
          ['pending_review', 'submitted', 'extracted', 'validated'].includes(c.status)
        ).length,
        approved: claimsData.filter((c: any) => 
          ['approved', 'auto_approved'].includes(c.status)
        ).length,
        denied: claimsData.filter((c: any) => c.status === 'denied').length,
        pended: claimsData.filter((c: any) => c.status === 'pended').length,
        totalAmount: claimsData.reduce((sum: number, c: any) => sum + (c.total_amount || 0), 0),
        avgProcessingTime: 2.3, // Placeholder - would calculate from actual data
      };
      setStats(newStats);
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

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'Just now';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'Just now';
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return 'Just now';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
      case 'auto_approved':
        return '✅';
      case 'denied':
        return '❌';
      case 'pending_review':
        return '👀';
      case 'submitted':
      case 'extracted':
        return '📄';
      default:
        return '📋';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
      case 'auto_approved':
        return styles.success;
      case 'denied':
        return styles.danger;
      case 'pending_review':
      case 'pended':
        return styles.warning;
      default:
        return styles.info;
    }
  };

  const displayName = user?.first_name || 'there';
  const primaryRole = user?.roles?.[0] || 'user';
  const roleLabel = primaryRole.charAt(0).toUpperCase() + primaryRole.slice(1);

  // Calculate approval rate
  const totalProcessed = stats.approved + stats.denied;
  const approvalRate = totalProcessed > 0 ? ((stats.approved / totalProcessed) * 100).toFixed(1) : '0';

  // Filter claims based on selected filter
  const getFilteredClaims = () => {
    switch (claimFilter) {
      case 'pending':
        return claims.filter(c => ['pending_review', 'submitted', 'extracted', 'validated'].includes(c.status));
      case 'approved':
        return claims.filter(c => ['approved', 'auto_approved'].includes(c.status));
      case 'denied':
        return claims.filter(c => c.status === 'denied');
      case 'pended':
        return claims.filter(c => c.status === 'pended');
      default:
        return claims;
    }
  };

  const filteredClaims = getFilteredClaims();

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
            <div className={styles.headerLeft}>
              <p className={styles.greeting}>
                <span>👋</span>
                {getGreeting()}, {displayName}
              </p>
              <h1 className={styles.title}>
                {canAccessManagement ? 'Agent Dashboard' : 'My Dashboard'}
              </h1>
              <p className={styles.subtitle}>
                {canAccessManagement 
                  ? 'Review claims, manage users, plans, and system settings'
                  : 'Track your claims and get AI-powered insights'}
              </p>
            </div>
            <span className={styles.roleBadge}>{roleLabel}</span>
          </div>

          {/* Stats Grid */}
          <div className={styles.statsGrid}>
            <div className={`${styles.statCard} ${styles.primary}`}>
              <div className={`${styles.statIcon} ${styles.primary}`}>📋</div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>
                  {canAccessQueue ? 'Total Claims' : 'My Claims'}
                </div>
                <div className={styles.statValue}>{isLoading ? '...' : stats.total}</div>
                <Link href="/claims" className={styles.statLink}>View all →</Link>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.warning}`}>
              <div className={`${styles.statIcon} ${styles.warning}`}>⏳</div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Pending</div>
                <div className={styles.statValue}>{isLoading ? '...' : stats.pending}</div>
                <span className={styles.statHint}>
                  {stats.pending > 0 ? 'Awaiting review' : 'All caught up!'}
                </span>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.success}`}>
              <div className={`${styles.statIcon} ${styles.success}`}>✅</div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Approved</div>
                <div className={styles.statValue}>{isLoading ? '...' : stats.approved}</div>
                <span className={styles.statHint}>{approvalRate}% approval rate</span>
              </div>
            </div>

            <div className={`${styles.statCard} ${styles.primary}`}>
              <div className={`${styles.statIcon} ${styles.primary}`}>💰</div>
              <div className={styles.statContent}>
                <div className={styles.statLabel}>Total Amount</div>
                <div className={styles.statValue}>{isLoading ? '...' : formatCurrency(stats.totalAmount)}</div>
                <span className={styles.statHint}>Across all claims</span>
              </div>
            </div>
          </div>

          {/* Main Grid */}
          <div className={styles.mainGrid}>
            <div className={styles.leftColumn}>
              {/* Quick Actions for Users */}
              {isRegularUser && (
                <div className={styles.section}>
                  <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>
                      <span>⚡</span>
                      Quick Actions
                    </h2>
                  </div>
                  <div className={styles.sectionBody}>
                    <div className={styles.quickActionsGrid}>
                      <Link href="/claims/new" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📤</div>
                        <div className={styles.quickActionContent}>
                          <h3>Submit New Claim</h3>
                          <p>Upload a document to create a new claim</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>
                      
                      <Link href="/claims" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📋</div>
                        <div className={styles.quickActionContent}>
                          <h3>View My Claims</h3>
                          <p>Check status and details of your claims</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>
                      
                      <Link href="/analytics" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📊</div>
                        <div className={styles.quickActionContent}>
                          <h3>Analytics</h3>
                          <p>View detailed insights and reports</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>
                    </div>
                  </div>
                </div>
              )}

              {/* Agent/Admin Quick Actions */}
              {canAccessQueue && (
                <div className={styles.section}>
                  <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>
                      <span>⚡</span>
                      Quick Actions
                    </h2>
                  </div>
                  <div className={styles.sectionBody}>
                    <div className={styles.quickActionsGrid}>
                      <Link href="/dashboard/queue" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📥</div>
                        <div className={styles.quickActionContent}>
                          <h3>Review Queue</h3>
                          <p>{stats.pending} claims awaiting review</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>
                      
                      <Link href="/claims" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📋</div>
                        <div className={styles.quickActionContent}>
                          <h3>All Claims</h3>
                          <p>View and manage all claims</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>
                      
                      <Link href="/analytics" className={styles.quickActionCard}>
                        <div className={styles.quickActionIconLarge}>📊</div>
                        <div className={styles.quickActionContent}>
                          <h3>Analytics</h3>
                          <p>View system performance</p>
                        </div>
                        <span className={styles.quickActionArrow}>→</span>
                      </Link>

                      {canAccessManagement && (
                        <Link href="/dashboard/admin" className={styles.quickActionCard}>
                          <div className={styles.quickActionIconLarge}>⚙️</div>
                          <div className={styles.quickActionContent}>
                            <h3>Management</h3>
                            <p>Manage users, plans, and rules</p>
                          </div>
                          <span className={styles.quickActionArrow}>→</span>
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Claims */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>🕐</span>
                    {canAccessQueue ? 'Claims History' : 'Recent Claims'}
                  </h2>
                  <Link href="/claims" className={styles.viewAllLink}>
                    View all →
                  </Link>
                </div>

                {/* Filter tabs for Agent */}
                {canAccessQueue && (
                  <div className={styles.filterTabs}>
                    <button 
                      className={`${styles.filterTab} ${claimFilter === 'all' ? styles.active : ''}`}
                      onClick={() => setClaimFilter('all')}
                    >
                      All ({stats.total})
                    </button>
                    <button 
                      className={`${styles.filterTab} ${claimFilter === 'pending' ? styles.active : ''}`}
                      onClick={() => setClaimFilter('pending')}
                    >
                      ⏳ Pending ({stats.pending})
                    </button>
                    <button 
                      className={`${styles.filterTab} ${claimFilter === 'approved' ? styles.active : ''}`}
                      onClick={() => setClaimFilter('approved')}
                    >
                      ✅ Approved ({stats.approved})
                    </button>
                    <button 
                      className={`${styles.filterTab} ${claimFilter === 'denied' ? styles.active : ''}`}
                      onClick={() => setClaimFilter('denied')}
                    >
                      ❌ Denied ({stats.denied})
                    </button>
                    <button 
                      className={`${styles.filterTab} ${claimFilter === 'pended' ? styles.active : ''}`}
                      onClick={() => setClaimFilter('pended')}
                    >
                      📋 Info Requested ({stats.pended})
                    </button>
                  </div>
                )}

                <div className={styles.sectionBody}>
                  {isLoading ? (
                    <div className={styles.loadingState}>
                      <div className={styles.spinner}></div>
                      <p>Loading claims...</p>
                    </div>
                  ) : filteredClaims.length === 0 ? (
                    <div className={styles.emptyState}>
                      <span className={styles.emptyIcon}>📋</span>
                      <h3>
                        {claimFilter === 'all' ? 'No Claims Yet' : `No ${claimFilter.replace('_', ' ')} Claims`}
                      </h3>
                      <p>
                        {isRegularUser 
                          ? 'Submit your first claim to get started!'
                          : claimFilter === 'all' 
                            ? 'No claims in the system yet.'
                            : `No claims with "${claimFilter}" status.`}
                      </p>
                      {isRegularUser && (
                        <Link href="/claims" className={styles.emptyAction}>
                          Submit a Claim →
                        </Link>
                      )}
                      {canAccessQueue && claimFilter !== 'all' && (
                        <button 
                          onClick={() => setClaimFilter('all')} 
                          className={styles.emptyAction}
                        >
                          View All Claims →
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className={styles.claimsList}>
                      {filteredClaims.slice(0, 10).map((claim, index) => (
                        <Link 
                          href={`/claims/${claim.id}`} 
                          key={claim.id || index} 
                          className={styles.claimItem}
                        >
                          <div className={`${styles.claimIcon} ${getStatusColor(claim.status)}`}>
                            {getStatusIcon(claim.status)}
                          </div>
                          <div className={styles.claimInfo}>
                            <div className={styles.claimHeader}>
                              <span className={styles.claimNumber}>{claim.claim_number}</span>
                              <span className={`${styles.claimStatus} ${getStatusColor(claim.status)}`}>
                                {claim.status?.replace('_', ' ')}
                              </span>
                            </div>
                            <div className={styles.claimDetails}>
                              <span className={styles.claimName}>
                                {claim.claimant_name || claim.provider_name || 'Claim'}
                              </span>
                              <span className={styles.claimDate}>
                                {formatDate(claim.created_at || claim.submitted_at)}
                              </span>
                            </div>
                          </div>
                          <div className={styles.claimAmount}>
                            {formatCurrency(claim.total_amount || 0)}
                          </div>
                        </Link>
                      ))}
                      
                      {/* Show count if more claims */}
                      {filteredClaims.length > 10 && (
                        <div className={styles.moreClaimsHint}>
                          + {filteredClaims.length - 10} more {claimFilter !== 'all' ? claimFilter : ''} claims
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className={styles.rightColumn}>
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

              {/* Claim Summary */}
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span>📊</span>
                    Claims Summary
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <div className={styles.summaryList}>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Total Claims</span>
                      <span className={styles.summaryValue}>{stats.total}</span>
                    </div>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Pending Review</span>
                      <span className={`${styles.summaryValue} ${styles.warning}`}>{stats.pending}</span>
                    </div>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Approved</span>
                      <span className={`${styles.summaryValue} ${styles.success}`}>{stats.approved}</span>
                    </div>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Denied</span>
                      <span className={`${styles.summaryValue} ${styles.danger}`}>{stats.denied}</span>
                    </div>
                    <div className={styles.summaryDivider}></div>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Approval Rate</span>
                      <span className={styles.summaryValue}>{approvalRate}%</span>
                    </div>
                    <div className={styles.summaryItem}>
                      <span className={styles.summaryLabel}>Total Amount</span>
                      <span className={styles.summaryValue}>{formatCurrency(stats.totalAmount)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tips & Help */}
              {isRegularUser && (
                <div className={styles.section}>
                  <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>
                      <span>💡</span>
                      Tips
                    </h2>
                  </div>
                  <div className={styles.sectionBody}>
                    <div className={styles.tipsList}>
                      <div className={styles.tipItem}>
                        <span className={styles.tipIcon}>📄</span>
                        <p>Upload clear, high-quality images for faster processing</p>
                      </div>
                      <div className={styles.tipItem}>
                        <span className={styles.tipIcon}>🔍</span>
                        <p>Include all relevant documents in a single upload</p>
                      </div>
                      <div className={styles.tipItem}>
                        <span className={styles.tipIcon}>⚡</span>
                        <p>Claims under $500 may be auto-approved instantly</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
