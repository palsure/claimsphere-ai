import { useState, useEffect } from 'react';
import Link from 'next/link';
import { claimsAPI } from '@/utils/api';
import { useAuth } from '@/contexts/AuthContext';
import styles from './ClaimList.module.css';
import { format, isValid, parseISO } from 'date-fns';

interface Claim {
  id: string;
  claim_number: string;
  user_id: string;
  claimant_name?: string;
  date_of_incident?: string;
  date_submitted?: string;
  created_at?: string;
  submitted_at?: string;
  service_date?: string;
  total_amount: number;
  approved_amount?: number;
  currency: string;
  claim_type?: string;
  category?: string;
  status: string;
  is_duplicate?: boolean;
  duplicate_score?: number;
  validation_errors?: string[];
  provider_name?: string;
  decisions?: any[];
}

interface ClaimListProps {
  claims: Claim[];
  refreshKey: number;
  onRefresh: () => void;
}

// Safe date formatting helper
const formatSafeDate = (dateStr: string | null | undefined, formatStr: string = 'MMM dd, yyyy'): string => {
  if (!dateStr) return 'N/A';
  try {
    let date = parseISO(dateStr);
    if (!isValid(date)) {
      date = new Date(dateStr);
    }
    if (!isValid(date)) return 'N/A';
    return format(date, formatStr);
  } catch {
    return 'N/A';
  }
};

// Safe date timestamp for sorting
const getDateTimestamp = (dateStr: string | null | undefined): number => {
  if (!dateStr) return 0;
  try {
    let date = parseISO(dateStr);
    if (!isValid(date)) {
      date = new Date(dateStr);
    }
    if (!isValid(date)) return 0;
    return date.getTime();
  } catch {
    return 0;
  }
};

export default function ClaimList({ claims, refreshKey, onRefresh }: ClaimListProps) {
  const { isAdmin, isAgent, hasAnyRole } = useAuth();
  const [filteredClaims, setFilteredClaims] = useState<Claim[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [showRequestInfoModal, setShowRequestInfoModal] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [decisionType, setDecisionType] = useState<'approved' | 'denied' | 'pended'>('approved');
  const [decisionNotes, setDecisionNotes] = useState('');
  const [reasonCode, setReasonCode] = useState('');
  const [approvedAmount, setApprovedAmount] = useState<number>(0);
  const [requestInfoMessage, setRequestInfoMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const canManageClaims = hasAnyRole(['admin', 'agent']);

  useEffect(() => {
    let filtered = [...claims];

    if (typeFilter !== 'all') {
      filtered = filtered.filter(claim => 
        (claim.claim_type === typeFilter) || (claim.category === typeFilter)
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(claim => claim.status === statusFilter);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(claim =>
        (claim.claimant_name || '').toLowerCase().includes(term) ||
        (claim.claim_number || '').toLowerCase().includes(term) ||
        (claim.claim_type || '').toLowerCase().includes(term) ||
        (claim.provider_name || '').toLowerCase().includes(term)
      );
    }

    filtered.sort((a, b) => {
      const dateA = getDateTimestamp(a.date_submitted || a.created_at);
      const dateB = getDateTimestamp(b.date_submitted || b.created_at);
      return dateB - dateA;
    });

    setFilteredClaims(filtered);
  }, [claims, typeFilter, statusFilter, searchTerm]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this claim?')) {
      return;
    }

    try {
      await claimsAPI.delete(id);
      onRefresh();
    } catch (error: any) {
      console.error('Error deleting claim:', error);
      const message = error.response?.data?.detail || 'Error deleting claim';
      alert(message);
    }
  };

  const handleStatusUpdate = async (id: string, status: string) => {
    try {
      await claimsAPI.updateStatus(id, status);
      onRefresh();
    } catch (error: any) {
      console.error('Error updating claim status:', error);
      const message = error.response?.data?.detail || 'Error updating claim status';
      alert(message);
    }
  };

  const openDecisionModal = (claim: Claim, type: 'approved' | 'denied' | 'pended') => {
    setSelectedClaim(claim);
    setDecisionType(type);
    setDecisionNotes('');
    setReasonCode('');
    setApprovedAmount(claim.total_amount || 0);
    setShowDecisionModal(true);
  };

  const openRequestInfoModal = (claim: Claim) => {
    setSelectedClaim(claim);
    setRequestInfoMessage('');
    setShowRequestInfoModal(true);
  };

  const handleDecision = async () => {
    if (!selectedClaim) return;
    
    setIsProcessing(true);
    try {
      await claimsAPI.makeDecision(selectedClaim.id, {
        decision: decisionType,
        reason_code: reasonCode || undefined,
        reason_description: decisionNotes || undefined,
        notes: decisionNotes || undefined,
        approved_amount: decisionType === 'approved' ? approvedAmount : undefined
      });
      setShowDecisionModal(false);
      onRefresh();
    } catch (error: any) {
      console.error('Error making decision:', error);
      alert(error.response?.data?.detail || 'Error making decision');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRequestInfo = async () => {
    if (!selectedClaim || !requestInfoMessage.trim()) return;
    
    setIsProcessing(true);
    try {
      await claimsAPI.requestInfo(selectedClaim.id, requestInfoMessage);
      setShowRequestInfoModal(false);
      onRefresh();
    } catch (error: any) {
      console.error('Error requesting info:', error);
      alert(error.response?.data?.detail || 'Error requesting info');
    } finally {
      setIsProcessing(false);
    }
  };

  const types = ['all', 'medical', 'dental', 'vision', 'pharmacy', 'hospital', 'emergency', 'mental_health', 'preventive', 'other'];
  const statuses = ['all', 'draft', 'submitted', 'extracted', 'validated', 'pending_review', 'auto_approved', 'approved', 'denied', 'pended'];

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'draft': '#9ca3af',
      'submitted': '#f59e0b',
      'extracted': '#3b82f6',
      'validated': '#8b5cf6',
      'pending_review': '#f59e0b',
      'auto_approved': '#10b981',
      'approved': '#10b981',
      'denied': '#ef4444',
      'pended': '#6b7280',
      'pending': '#f59e0b',
      'under_review': '#3b82f6',
      'rejected': '#ef4444',
      'requires_info': '#8b5cf6',
      'processed': '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  const canTakeAction = (status: string) => {
    const actionableStatuses = ['submitted', 'extracted', 'validated', 'pending_review', 'pended'];
    return actionableStatuses.includes(status);
  };

  const reasonCodes = [
    { code: 'complete', label: 'Documentation Complete' },
    { code: 'covered', label: 'Service Covered' },
    { code: 'eligible', label: 'Member Eligible' },
    { code: 'not_covered', label: 'Service Not Covered' },
    { code: 'ineligible', label: 'Member Ineligible' },
    { code: 'duplicate', label: 'Duplicate Claim' },
    { code: 'missing_docs', label: 'Missing Documentation' },
    { code: 'fraud', label: 'Suspected Fraud' },
    { code: 'other', label: 'Other' }
  ];

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
              {type === 'all' ? 'All Types' : type.replace('_', ' ').toUpperCase()}
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
        <span>Total Amount: ${filteredClaims.reduce((sum, claim) => sum + (claim.total_amount || 0), 0).toFixed(2)}</span>
        <span>Approved: ${filteredClaims.filter(c => c.status === 'approved' || c.status === 'auto_approved').reduce((sum, c) => sum + (c.approved_amount || c.total_amount || 0), 0).toFixed(2)}</span>
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
                <Link href={`/claims/${claim.id}`} className={styles.claimLink}>
                  <h3>{claim.claimant_name || claim.provider_name || 'Unnamed Claim'}</h3>
                  <span className={styles.claimNumber}>{claim.claim_number || 'N/A'}</span>
                </Link>
                <div className={styles.amountSection}>
                  <span className={styles.amount}>
                    {claim.currency || 'USD'} {(claim.total_amount || 0).toFixed(2)}
                  </span>
                  {claim.approved_amount && (
                    <span className={styles.approvedAmount}>
                      Approved: {claim.currency || 'USD'} {claim.approved_amount.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>
              
              <div className={styles.claimDetails}>
                <span className={styles.type}>{(claim.claim_type || claim.category || 'other').replace('_', ' ')}</span>
                <span 
                  className={styles.status}
                  style={{ backgroundColor: getStatusColor(claim.status) }}
                >
                  {(claim.status || 'unknown').replace('_', ' ').toUpperCase()}
                </span>
                <span className={styles.date}>
                  Service: {formatSafeDate(claim.date_of_incident || claim.service_date)}
                </span>
                <span className={styles.date}>
                  Submitted: {formatSafeDate(claim.date_submitted || claim.created_at)}
                </span>
                {claim.is_duplicate && (
                  <span className={styles.duplicateBadge}>⚠️ Potential Duplicate</span>
                )}
                {claim.duplicate_score && claim.duplicate_score > 0.5 && (
                  <span className={styles.duplicateScore}>
                    Similarity: {(claim.duplicate_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              {/* Show latest decision/note if available */}
              {claim.decisions && claim.decisions.length > 0 && (
                <div className={styles.decisionNote}>
                  <strong>Latest Decision:</strong> {claim.decisions[claim.decisions.length - 1].notes || claim.decisions[claim.decisions.length - 1].reason_description || 'No notes'}
                </div>
              )}

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
                {/* View Details - for all users */}
                <Link href={`/claims/${claim.id}`} className={styles.viewBtn}>
                  👁️ View Details
                </Link>

                {/* Admin/Agent Actions */}
                {canManageClaims && canTakeAction(claim.status) && (
                  <>
                    <button
                      onClick={() => openDecisionModal(claim, 'approved')}
                      className={styles.approveBtn}
                    >
                      ✅ Approve
                    </button>
                    <button
                      onClick={() => openDecisionModal(claim, 'denied')}
                      className={styles.rejectBtn}
                    >
                      ❌ Deny
                    </button>
                    <button
                      onClick={() => openDecisionModal(claim, 'pended')}
                      className={styles.pendBtn}
                    >
                      ⏸️ Pend
                    </button>
                    <button
                      onClick={() => openRequestInfoModal(claim)}
                      className={styles.infoBtn}
                    >
                      📝 Request Info
                    </button>
                  </>
                )}
                
                {/* Delete button - for claim owner or agents, only non-terminal claims */}
                {!['approved', 'denied', 'auto_approved', 'closed'].includes(claim.status) && (
                  <button
                    onClick={() => handleDelete(claim.id)}
                    className={styles.deleteBtn}
                  >
                    🗑️ Delete
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Decision Modal */}
      {showDecisionModal && selectedClaim && (
        <div className={styles.modalOverlay} onClick={() => setShowDecisionModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>
              {decisionType === 'approved' && '✅ Approve Claim'}
              {decisionType === 'denied' && '❌ Deny Claim'}
              {decisionType === 'pended' && '⏸️ Pend Claim'}
            </h3>
            <p className={styles.modalSubtitle}>
              Claim #{selectedClaim.claim_number} - {selectedClaim.claimant_name || 'Unknown'}
            </p>
            
            {decisionType === 'approved' && (
              <div className={styles.formGroup}>
                <label>Approved Amount ($)</label>
                <input
                  type="number"
                  value={approvedAmount}
                  onChange={(e) => setApprovedAmount(parseFloat(e.target.value) || 0)}
                  className="input"
                  step="0.01"
                />
              </div>
            )}

            <div className={styles.formGroup}>
              <label>Reason Code</label>
              <select
                value={reasonCode}
                onChange={(e) => setReasonCode(e.target.value)}
                className="input"
              >
                <option value="">Select a reason...</option>
                {reasonCodes.map(rc => (
                  <option key={rc.code} value={rc.code}>{rc.label}</option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Notes / Comments</label>
              <textarea
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                className="input"
                rows={4}
                placeholder="Add notes or comments for this decision..."
              />
            </div>

            <div className={styles.modalActions}>
              <button
                onClick={() => setShowDecisionModal(false)}
                className={styles.cancelBtn}
                disabled={isProcessing}
              >
                Cancel
              </button>
              <button
                onClick={handleDecision}
                className={
                  decisionType === 'approved' ? styles.approveBtn :
                  decisionType === 'denied' ? styles.rejectBtn :
                  styles.pendBtn
                }
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : `Confirm ${decisionType.charAt(0).toUpperCase() + decisionType.slice(1)}`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Request Info Modal */}
      {showRequestInfoModal && selectedClaim && (
        <div className={styles.modalOverlay} onClick={() => setShowRequestInfoModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>📝 Request Additional Information</h3>
            <p className={styles.modalSubtitle}>
              Claim #{selectedClaim.claim_number} - {selectedClaim.claimant_name || 'Unknown'}
            </p>
            
            <div className={styles.formGroup}>
              <label>Message to Claimant</label>
              <textarea
                value={requestInfoMessage}
                onChange={(e) => setRequestInfoMessage(e.target.value)}
                className="input"
                rows={5}
                placeholder="Describe what additional information or documents are needed..."
              />
            </div>

            <div className={styles.quickMessages}>
              <span>Quick messages:</span>
              <button onClick={() => setRequestInfoMessage('Please provide a copy of your itemized receipt.')}>
                Itemized Receipt
              </button>
              <button onClick={() => setRequestInfoMessage('Please provide proof of payment.')}>
                Proof of Payment
              </button>
              <button onClick={() => setRequestInfoMessage('Please provide a letter of medical necessity.')}>
                Medical Necessity
              </button>
              <button onClick={() => setRequestInfoMessage('Please provide the Explanation of Benefits (EOB) from your primary insurance.')}>
                EOB Required
              </button>
            </div>

            <div className={styles.modalActions}>
              <button
                onClick={() => setShowRequestInfoModal(false)}
                className={styles.cancelBtn}
                disabled={isProcessing}
              >
                Cancel
              </button>
              <button
                onClick={handleRequestInfo}
                className={styles.infoBtn}
                disabled={isProcessing || !requestInfoMessage.trim()}
              >
                {isProcessing ? 'Sending...' : 'Send Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
