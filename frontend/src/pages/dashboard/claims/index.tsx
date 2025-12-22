/**
 * User Claims List Page
 */
import { useEffect, useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '../../../components/DashboardLayout';
import { claimsAPI } from '../../../utils/api';
import styles from '../../../styles/ClaimsList.module.css';

export default function ClaimsList() {
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: '', category: '' });

  useEffect(() => {
    loadClaims();
  }, [filter]);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const params: any = { page_size: 50 };
      if (filter.status) params.status = filter.status;
      if (filter.category) params.category = filter.category;
      
      const data = await claimsAPI.list(params);
      setClaims(data);
    } catch (error) {
      console.error('Failed to load claims:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses: Record<string, string> = {
      draft: styles.statusDraft,
      submitted: styles.statusSubmitted,
      extracted: styles.statusSubmitted,
      validated: styles.statusSubmitted,
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

  return (
    <DashboardLayout title="My Claims">
      <div className={styles.container}>
        {/* Header Actions */}
        <div className={styles.headerActions}>
          <div className={styles.filters}>
            <select
              value={filter.status}
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
              className={styles.filterSelect}
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="submitted">Submitted</option>
              <option value="pending_review">Pending Review</option>
              <option value="approved">Approved</option>
              <option value="denied">Denied</option>
              <option value="pended">Need More Info</option>
            </select>
            
            <select
              value={filter.category}
              onChange={(e) => setFilter({ ...filter, category: e.target.value })}
              className={styles.filterSelect}
            >
              <option value="">All Categories</option>
              <option value="medical">Medical</option>
              <option value="dental">Dental</option>
              <option value="vision">Vision</option>
              <option value="pharmacy">Pharmacy</option>
              <option value="hospital">Hospital</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
          
          <Link href="/dashboard/claims/new" className={styles.newClaimButton}>
            ➕ New Claim
          </Link>
        </div>

        {/* Claims Table */}
        {loading ? (
          <div className={styles.loading}>Loading claims...</div>
        ) : claims.length === 0 ? (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>📋</span>
            <h3>No claims found</h3>
            <p>You haven't submitted any claims yet.</p>
            <Link href="/dashboard/claims/new" className={styles.primaryButton}>
              Submit Your First Claim
            </Link>
          </div>
        ) : (
          <div className={styles.claimsTable}>
            <div className={styles.tableHeader}>
              <span>Claim #</span>
              <span>Category</span>
              <span>Provider</span>
              <span>Amount</span>
              <span>Status</span>
              <span>Date</span>
              <span>Actions</span>
            </div>
            
            {claims.map((claim) => (
              <div key={claim.id} className={styles.tableRow}>
                <span className={styles.claimNumber}>{claim.claim_number}</span>
                <span className={styles.category}>{claim.category}</span>
                <span className={styles.provider}>{claim.provider_name || '-'}</span>
                <span className={styles.amount}>
                  {formatCurrency(claim.total_amount, claim.currency)}
                  {claim.approved_amount && claim.approved_amount !== claim.total_amount && (
                    <span className={styles.approvedAmount}>
                      (Approved: {formatCurrency(claim.approved_amount, claim.currency)})
                    </span>
                  )}
                </span>
                <span className={`${styles.status} ${getStatusBadge(claim.status)}`}>
                  {claim.status.replace('_', ' ')}
                </span>
                <span className={styles.date}>{formatDate(claim.created_at)}</span>
                <span className={styles.actions}>
                  <Link href={`/dashboard/claims/${claim.id}`} className={styles.viewLink}>
                    View
                  </Link>
                  {claim.status === 'draft' && (
                    <Link href={`/dashboard/claims/${claim.id}/edit`} className={styles.editLink}>
                      Edit
                    </Link>
                  )}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

