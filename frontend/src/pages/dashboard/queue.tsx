/**
 * Agent Review Queue Page
 */
import { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { claimsAPI } from '@/utils/api';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/Queue.module.css';

export default function ReviewQueue() {
  const router = useRouter();
  const { user, hasAnyRole, isLoading: authLoading } = useAuth();
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only load if user is authenticated and has permissions
    if (!authLoading && user && hasAnyRole(['agent', 'admin'])) {
      loadQueue();
    } else if (!authLoading && user && !hasAnyRole(['agent', 'admin'])) {
      // Redirect unauthorized users
      router.push('/');
    }
  }, [user, authLoading]);

  const loadQueue = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get queue, fallback to filtered claims list
      try {
        const data = await claimsAPI.getQueue();
        const queueData = Array.isArray(data) ? data : (data.claims || []);
        setQueue(queueData);
      } catch (queueError) {
        // Fallback: get all claims and filter pending ones
        console.log('Queue endpoint failed, falling back to claims list');
        const data = await claimsAPI.list({ page_size: 100 });
        const allClaims = Array.isArray(data) ? data : (data.claims || []);
        const pendingClaims = allClaims.filter((c: any) => 
          ['pending_review', 'submitted', 'extracted', 'validated'].includes(c.status)
        );
        setQueue(pendingClaims);
      }
    } catch (err: any) {
      console.error('Failed to load queue:', err);
      setError(err.message || 'Failed to load queue');
      setQueue([]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number | null | undefined, currency: string = 'USD') => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return 'N/A';
    }
  };

  const getTimeSinceSubmission = (dateString: string | null | undefined) => {
    if (!dateString) return 'Just now';
    try {
      const submitted = new Date(dateString);
      if (isNaN(submitted.getTime())) return 'Just now';
      const now = new Date();
      const diffMs = now.getTime() - submitted.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHours / 24);
      
      if (diffDays > 0) {
        return `${diffDays}d ${diffHours % 24}h ago`;
      }
      if (diffHours > 0) {
        return `${diffHours}h ago`;
      }
      return 'Just now';
    } catch {
      return 'Just now';
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'pending_review': '#f59e0b',
      'submitted': '#3b82f6',
      'extracted': '#8b5cf6',
      'validated': '#6366f1',
    };
    return (
      <span 
        className={styles.statusBadge}
        style={{ backgroundColor: statusColors[status] || '#6b7280' }}
      >
        {(status || 'unknown').replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  // Calculate stats safely
  const totalValue = queue.reduce((sum, c) => sum + (c.total_amount || 0), 0);
  const over24h = queue.filter(c => {
    const dateStr = c.submitted_at || c.created_at;
    if (!dateStr) return false;
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return false;
      const hours = (Date.now() - date.getTime()) / (1000 * 60 * 60);
      return hours > 24;
    } catch {
      return false;
    }
  }).length;

  // Show loading or access denied
  if (authLoading) {
    return (
      <>
        <Head>
          <title>Review Queue | ClaimSphere AI</title>
        </Head>
        <main className={styles.main}>
          <div className={styles.container}>
            <div className={styles.loading}>Loading...</div>
          </div>
        </main>
      </>
    );
  }

  if (!hasAnyRole(['agent', 'admin'])) {
    return (
      <>
        <Head>
          <title>Access Denied | ClaimSphere AI</title>
        </Head>
        <main className={styles.main}>
          <div className={styles.container}>
            <div className={styles.accessDenied}>
              <h2>🚫 Access Denied</h2>
              <p>You don't have permission to access this page.</p>
              <Link href="/" className={styles.backButton}>
                Go to Dashboard
              </Link>
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>Review Queue | ClaimSphere AI</title>
        <meta name="description" content="Review and process pending claims" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <h1 className={styles.title}>
                <span>📥</span>
                Review Queue
              </h1>
              <p className={styles.subtitle}>
                Claims awaiting review and processing
              </p>
            </div>
            <button 
              className={styles.refreshBtn}
              onClick={loadQueue}
              disabled={loading}
            >
              {loading ? '⟳ Loading...' : '⟳ Refresh'}
            </button>
          </div>

          {/* Stats Bar */}
          <div className={styles.statsBar}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{queue.length}</span>
              <span className={styles.statLabel}>In Queue</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{over24h}</span>
              <span className={styles.statLabel}>Over 24h</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{formatCurrency(totalValue)}</span>
              <span className={styles.statLabel}>Total Value</span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className={styles.errorMessage}>
              ⚠️ {error}
            </div>
          )}

          {/* Queue List */}
          {loading ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              Loading queue...
            </div>
          ) : queue.length === 0 ? (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>✅</span>
              <h3>Queue is Empty</h3>
              <p>All claims have been processed. Great work!</p>
            </div>
          ) : (
            <div className={styles.queueList}>
              {queue.map((claim) => (
                <div key={claim.id} className={styles.queueItem}>
                  <div className={styles.claimInfo}>
                    <div className={styles.claimHeader}>
                      <span className={styles.claimNumber}>
                        {claim.claim_number || 'N/A'}
                      </span>
                      {getStatusBadge(claim.status)}
                      <span className={styles.category}>
                        {claim.category || claim.claim_type || 'Other'}
                      </span>
                    </div>
                    <div className={styles.claimDetails}>
                      <span className={styles.amount}>
                        {formatCurrency(claim.total_amount, claim.currency)}
                      </span>
                      <span className={styles.provider}>
                        📍 {claim.provider_name || 'No provider'}
                      </span>
                    </div>
                    <div className={styles.claimMeta}>
                      <span className={styles.timeAgo}>
                        ⏱️ {getTimeSinceSubmission(claim.submitted_at || claim.created_at)}
                      </span>
                      <span className={styles.serviceDate}>
                        📅 Service: {formatDate(claim.service_date)}
                      </span>
                    </div>
                  </div>
                  
                  <div className={styles.claimActions}>
                    <Link 
                      href={`/claims/${claim.id}`} 
                      className={styles.viewButton}
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
