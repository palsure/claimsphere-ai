/**
 * Main Dashboard - Role-based landing page
 */
import { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import DashboardLayout from '../../components/DashboardLayout';
import { claimsAPI, adminAPI } from '../../utils/api';
import styles from '../../styles/Dashboard.module.css';

interface DashboardStats {
  myClaims?: number;
  pendingClaims?: number;
  approvedClaims?: number;
  totalAmount?: number;
  // Admin stats
  totalUsers?: number;
  queueSize?: number;
  todaySubmissions?: number;
}

export default function Dashboard() {
  const { user, hasRole } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({});
  const [recentClaims, setRecentClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    try {
      // Load claims for all users
      const claims = await claimsAPI.list({ page_size: 5 });
      setRecentClaims(claims);

      // Calculate stats based on role
      if (hasRole('admin')) {
        const adminStats = await adminAPI.getDashboardStats();
        setStats({
          totalUsers: adminStats.users.total,
          queueSize: adminStats.claims.pending_review,
          todaySubmissions: adminStats.claims.submitted_today,
          totalAmount: adminStats.amounts.total_claimed,
        });
      } else if (hasRole('agent')) {
        const queue = await claimsAPI.getQueue();
        setStats({
          queueSize: queue.length,
          pendingClaims: claims.filter((c: any) => c.status === 'pending_review').length,
        });
      } else {
        // User stats
        setStats({
          myClaims: claims.length,
          pendingClaims: claims.filter((c: any) => 
            ['submitted', 'pending_review', 'validated'].includes(c.status)
          ).length,
          approvedClaims: claims.filter((c: any) => 
            ['approved', 'auto_approved'].includes(c.status)
          ).length,
          totalAmount: claims.reduce((sum: number, c: any) => sum + c.total_amount, 0),
        });
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses: Record<string, string> = {
      draft: styles.statusDraft,
      submitted: styles.statusSubmitted,
      pending_review: styles.statusPending,
      approved: styles.statusApproved,
      auto_approved: styles.statusApproved,
      denied: styles.statusDenied,
      pended: styles.statusPended,
    };
    return statusClasses[status] || styles.statusDefault;
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <DashboardLayout title="Dashboard">
        <div className={styles.loading}>Loading...</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Dashboard">
      <div className={styles.dashboard}>
        {/* Welcome Section */}
        <div className={styles.welcomeCard}>
          <h2>Welcome back, {user?.first_name}!</h2>
          <p>
            {hasRole('admin') 
              ? 'Manage your organization\'s claims, users, and policies.'
              : hasRole('agent')
              ? 'Review and process claims in your queue.'
              : 'Submit and track your insurance claims.'}
          </p>
        </div>

        {/* Stats Grid */}
        <div className={styles.statsGrid}>
          {hasRole('admin') ? (
            <>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>👥</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.totalUsers || 0}</span>
                  <span className={styles.statLabel}>Total Users</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>📥</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.queueSize || 0}</span>
                  <span className={styles.statLabel}>Pending Review</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>📅</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.todaySubmissions || 0}</span>
                  <span className={styles.statLabel}>Today's Submissions</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>💰</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{formatCurrency(stats.totalAmount || 0)}</span>
                  <span className={styles.statLabel}>Total Claimed</span>
                </div>
              </div>
            </>
          ) : hasRole('agent') ? (
            <>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>📥</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.queueSize || 0}</span>
                  <span className={styles.statLabel}>Claims in Queue</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>⏳</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.pendingClaims || 0}</span>
                  <span className={styles.statLabel}>Pending Review</span>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>📋</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.myClaims || 0}</span>
                  <span className={styles.statLabel}>My Claims</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>⏳</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.pendingClaims || 0}</span>
                  <span className={styles.statLabel}>Pending</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>✅</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{stats.approvedClaims || 0}</span>
                  <span className={styles.statLabel}>Approved</span>
                </div>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statIcon}>💰</span>
                <div className={styles.statContent}>
                  <span className={styles.statValue}>{formatCurrency(stats.totalAmount || 0)}</span>
                  <span className={styles.statLabel}>Total Claimed</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Recent Claims */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3>Recent Claims</h3>
            <a href={hasRole('admin') || hasRole('agent') ? '/dashboard/all-claims' : '/dashboard/claims'} className={styles.viewAllLink}>
              View All →
            </a>
          </div>
          
          {recentClaims.length === 0 ? (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>📭</span>
              <p>No claims yet</p>
              {hasRole('user') && (
                <a href="/dashboard/claims/new" className={styles.primaryButton}>
                  Submit Your First Claim
                </a>
              )}
            </div>
          ) : (
            <div className={styles.claimsList}>
              {recentClaims.map((claim: any) => (
                <a
                  key={claim.id}
                  href={`/dashboard/claims/${claim.id}`}
                  className={styles.claimCard}
                >
                  <div className={styles.claimHeader}>
                    <span className={styles.claimNumber}>{claim.claim_number}</span>
                    <span className={`${styles.statusBadge} ${getStatusBadge(claim.status)}`}>
                      {claim.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className={styles.claimDetails}>
                    <span className={styles.claimCategory}>{claim.category}</span>
                    <span className={styles.claimAmount}>
                      {formatCurrency(claim.total_amount, claim.currency)}
                    </span>
                  </div>
                  <div className={styles.claimMeta}>
                    <span>{claim.provider_name || 'No provider'}</span>
                    <span>{formatDate(claim.created_at)}</span>
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className={styles.section}>
          <h3>Quick Actions</h3>
          <div className={styles.actionsGrid}>
            {hasRole('user') && (
              <>
                <a href="/dashboard/claims/new" className={styles.actionCard}>
                  <span className={styles.actionIcon}>➕</span>
                  <span className={styles.actionLabel}>Submit New Claim</span>
                </a>
                <a href="/dashboard/claims" className={styles.actionCard}>
                  <span className={styles.actionIcon}>📋</span>
                  <span className={styles.actionLabel}>View My Claims</span>
                </a>
              </>
            )}
            {(hasRole('agent') || hasRole('admin')) && (
              <>
                <a href="/dashboard/queue" className={styles.actionCard}>
                  <span className={styles.actionIcon}>📥</span>
                  <span className={styles.actionLabel}>Review Queue</span>
                </a>
                <a href="/dashboard/all-claims" className={styles.actionCard}>
                  <span className={styles.actionIcon}>🔍</span>
                  <span className={styles.actionLabel}>Search Claims</span>
                </a>
              </>
            )}
            {hasRole('admin') && (
              <>
                <a href="/dashboard/users" className={styles.actionCard}>
                  <span className={styles.actionIcon}>👥</span>
                  <span className={styles.actionLabel}>Manage Users</span>
                </a>
                <a href="/dashboard/analytics" className={styles.actionCard}>
                  <span className={styles.actionIcon}>📈</span>
                  <span className={styles.actionLabel}>View Analytics</span>
                </a>
              </>
            )}
            <a href="/dashboard/query" className={styles.actionCard}>
              <span className={styles.actionIcon}>🤖</span>
              <span className={styles.actionLabel}>Ask AI</span>
            </a>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

