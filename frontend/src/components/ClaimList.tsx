import { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './ClaimList.module.css';
import { format } from 'date-fns';

interface Claim {
  id: string;
  claim_number: string;
  claimant_name: string;
  date_of_incident: string;
  date_submitted: string;
  total_amount: number;
  approved_amount?: number;
  currency: string;
  claim_type: string;
  status: string;
  is_duplicate?: boolean;
  validation_errors?: string[];
}

interface ClaimListProps {
  claims: Claim[];
  refreshKey: number;
  onRefresh: () => void;
}

export default function ClaimList({ claims, refreshKey, onRefresh }: ClaimListProps) {
  const [filteredClaims, setFilteredClaims] = useState<Claim[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    onRefresh();
  }, [refreshKey]);

  useEffect(() => {
    let filtered = [...claims];

    // Apply type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(claim => claim.claim_type === typeFilter);
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(claim => claim.status === statusFilter);
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(claim =>
        claim.claimant_name.toLowerCase().includes(term) ||
        claim.claim_number?.toLowerCase().includes(term) ||
        claim.claim_type.toLowerCase().includes(term)
      );
    }

    // Sort by date (newest first)
    filtered.sort((a, b) => new Date(b.date_submitted).getTime() - new Date(a.date_submitted).getTime());

    setFilteredClaims(filtered);
  }, [claims, typeFilter, statusFilter, searchTerm]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this claim?')) {
      return;
    }

    try {
      await axios.delete(`/api/claims/${id}`);
      onRefresh();
    } catch (error) {
      console.error('Error deleting claim:', error);
      alert('Error deleting claim');
    }
  };

  const handleStatusUpdate = async (id: string, status: string) => {
    try {
      await axios.put(`/api/claims/${id}/status`, { status });
      onRefresh();
    } catch (error) {
      console.error('Error updating claim status:', error);
      alert('Error updating claim status');
    }
  };

  const types = ['all', 'medical', 'insurance', 'travel', 'property', 'business', 'other'];
  const statuses = ['all', 'pending', 'under_review', 'approved', 'rejected', 'requires_info', 'processed'];

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'pending': '#f59e0b',
      'under_review': '#3b82f6',
      'approved': '#10b981',
      'rejected': '#ef4444',
      'requires_info': '#8b5cf6',
      'processed': '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  return (
    <div className={styles.card}>
      <h2>📋 Claims List</h2>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Search claims..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input"
        >
          {types.map(type => (
            <option key={type} value={type}>
              {type === 'all' ? 'All Types' : type.toUpperCase()}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input"
        >
          {statuses.map(status => (
            <option key={status} value={status}>
              {status === 'all' ? 'All Statuses' : status.replace('_', ' ').toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.stats}>
        <span>Total: {filteredClaims.length} claims</span>
        <span>Total Amount: ${filteredClaims.reduce((sum, claim) => sum + claim.total_amount, 0).toFixed(2)}</span>
        <span>Approved: ${filteredClaims.filter(c => c.status === 'approved').reduce((sum, c) => sum + (c.approved_amount || 0), 0).toFixed(2)}</span>
      </div>

      <div className={styles.claimList}>
        {filteredClaims.length === 0 ? (
          <p className={styles.empty}>No claims found. Upload a claim document to get started!</p>
        ) : (
          filteredClaims.map(claim => (
            <div
              key={claim.id}
              className={`${styles.claimItem} ${claim.is_duplicate ? styles.duplicate : ''}`}
            >
              <div className={styles.claimHeader}>
                <div>
                  <h3>{claim.claimant_name}</h3>
                  <span className={styles.claimNumber}>{claim.claim_number || 'N/A'}</span>
                </div>
                <div className={styles.amountSection}>
                  <span className={styles.amount}>
                    {claim.currency} {claim.total_amount.toFixed(2)}
                  </span>
                  {claim.approved_amount && (
                    <span className={styles.approvedAmount}>
                      Approved: {claim.currency} {claim.approved_amount.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>
              <div className={styles.claimDetails}>
                <span className={styles.type}>{claim.claim_type}</span>
                <span 
                  className={styles.status}
                  style={{ backgroundColor: getStatusColor(claim.status) }}
                >
                  {claim.status.replace('_', ' ').toUpperCase()}
                </span>
                <span className={styles.date}>
                  Incident: {format(new Date(claim.date_of_incident), 'MMM dd, yyyy')}
                </span>
                <span className={styles.date}>
                  Submitted: {format(new Date(claim.date_submitted), 'MMM dd, yyyy')}
                </span>
                {claim.is_duplicate && (
                  <span className={styles.duplicateBadge}>⚠️ Potential Duplicate</span>
                )}
              </div>
              {claim.validation_errors && claim.validation_errors.length > 0 && (
                <div className={styles.validationErrors}>
                  <strong>Validation Errors:</strong>
                  <ul>
                    {claim.validation_errors.map((error, idx) => (
                      <li key={idx}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className={styles.actions}>
                {claim.status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleStatusUpdate(claim.id, 'approved')}
                      className={styles.approveBtn}
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleStatusUpdate(claim.id, 'rejected')}
                      className={styles.rejectBtn}
                    >
                      Reject
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleDelete(claim.id)}
                  className={styles.deleteBtn}
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

