import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { claimsAPI } from '@/utils/api';
import styles from '@/styles/ClaimDetails.module.css';

interface ExtractedField {
  id: string;
  field_name: string;
  value: string;
  original_value: string | null;
  confidence: number | null;
  source: string;
  corrected_by: string | null;
  corrected_at: string | null;
}

interface ClaimDocument {
  id: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_size: number;
  ocr_quality_score: number | null;
  created_at: string;
}

interface ValidationResult {
  id: string;
  rule_name: string;
  passed: boolean;
  message: string;
  severity: string;
}

interface Decision {
  id: string;
  decision: string;
  reason_code: string | null;
  reason_description: string | null;
  notes: string | null;
  approved_amount: number | null;
  created_at: string;
}

interface Claim {
  id: string;
  claim_number: string;
  user_id: string;
  claimant_name: string | null;
  status: string;
  category: string;
  total_amount: number;
  approved_amount: number | null;
  currency: string;
  service_date: string | null;
  provider_name: string | null;
  description: string | null;
  ocr_quality_score: number | null;
  extraction_confidence: number | null;
  duplicate_score: number;
  is_duplicate: boolean;
  created_at: string;
  submitted_at: string | null;
  documents: ClaimDocument[];
  extracted_fields: ExtractedField[];
  validation_results: ValidationResult[];
  decisions: Decision[];
}

interface TimelineEvent {
  id: string;
  action: string;
  actor: string;
  timestamp: string;
  details: any;
}

const STATUS_LABELS: Record<string, { label: string; color: string; icon: string }> = {
  draft: { label: 'Draft', color: '#6b7280', icon: '📝' },
  submitted: { label: 'Submitted', color: '#f59e0b', icon: '📤' },
  extracted: { label: 'Extracted', color: '#3b82f6', icon: '🔍' },
  validated: { label: 'Validated', color: '#8b5cf6', icon: '✅' },
  pending_review: { label: 'Pending Review', color: '#f59e0b', icon: '⏳' },
  auto_approved: { label: 'Auto Approved', color: '#10b981', icon: '🤖' },
  approved: { label: 'Approved', color: '#10b981', icon: '✅' },
  denied: { label: 'Denied', color: '#ef4444', icon: '❌' },
  pended: { label: 'More Info Needed', color: '#6b7280', icon: '📋' },
  closed: { label: 'Closed', color: '#374151', icon: '🔒' },
};

const FIELD_LABELS: Record<string, string> = {
  claimant_name: 'Claimant Name',
  date_of_incident: 'Date of Service',
  total_amount: 'Total Amount',
  currency: 'Currency',
  provider_name: 'Provider Name',
  policy_number: 'Policy Number',
  diagnosis: 'Diagnosis',
  procedure: 'Procedure',
  claim_type: 'Claim Type',
};

export default function ClaimDetailsPage() {
  const router = useRouter();
  const { id } = router.query;
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [claim, setClaim] = useState<Claim | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'documents' | 'timeline'>('details');
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchClaim = useCallback(async () => {
    if (!id || typeof id !== 'string') return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const [claimData, timelineData] = await Promise.all([
        claimsAPI.get(id),
        claimsAPI.getTimeline(id).catch(() => ({ timeline: [] })),
      ]);
      
      setClaim(claimData);
      setTimeline(timelineData.timeline || []);
    } catch (err: any) {
      console.error('Error fetching claim:', err);
      setError(err.response?.data?.detail || 'Failed to load claim');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }
    
    if (id && isAuthenticated) {
      fetchClaim();
    }
  }, [id, isAuthenticated, authLoading, router, fetchClaim]);

  const handleDelete = async () => {
    if (!claim) return;
    
    setIsDeleting(true);
    try {
      await claimsAPI.delete(claim.id);
      router.push('/claims');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete claim');
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const canDelete = claim && !['approved', 'denied', 'auto_approved', 'closed'].includes(claim.status);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'N/A';
    }
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  };

  if (authLoading || isLoading) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Loading claim details...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <div className={styles.errorState}>
            <span>❌</span>
            <h2>Error Loading Claim</h2>
            <p>{error}</p>
            <Link href="/claims" className={styles.backLink}>
              ← Back to My Claims
            </Link>
          </div>
        </div>
      </main>
    );
  }

  if (!claim) {
    return null;
  }

  const statusInfo = STATUS_LABELS[claim.status] || STATUS_LABELS.draft;

  return (
    <>
      <Head>
        <title>Claim {claim.claim_number} | ClaimSphere AI</title>
        <meta name="description" content={`View details for claim ${claim.claim_number}`} />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Breadcrumb */}
          <div className={styles.breadcrumb}>
            <Link href="/claims">← Back to My Claims</Link>
          </div>

          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerMain}>
              <h1 className={styles.title}>
                <span>📋</span>
                Claim {claim.claim_number}
              </h1>
              <div 
                className={styles.statusBadge}
                style={{ backgroundColor: statusInfo.color }}
              >
                <span>{statusInfo.icon}</span>
                {statusInfo.label}
              </div>
            </div>
            
            <div className={styles.headerMeta}>
              <span>Created: {formatDate(claim.created_at)}</span>
              {claim.submitted_at && <span>Submitted: {formatDate(claim.submitted_at)}</span>}
            </div>

            <div className={styles.headerActions}>
              {canDelete && (
                <button 
                  onClick={() => setShowDeleteModal(true)}
                  className={styles.deleteBtn}
                >
                  🗑️ Delete Claim
                </button>
              )}
            </div>
          </div>

          {/* Duplicate Warning */}
          {claim.is_duplicate && (
            <div className={styles.duplicateWarning}>
              <span>⚠️</span>
              <div>
                <strong>Potential Duplicate</strong>
                <p>This claim appears similar to an existing claim (Score: {(claim.duplicate_score * 100).toFixed(0)}%)</p>
              </div>
            </div>
          )}

          {/* Summary Cards */}
          <div className={styles.summaryGrid}>
            <div className={styles.summaryCard}>
              <span className={styles.summaryIcon}>💰</span>
              <div>
                <div className={styles.summaryLabel}>Total Amount</div>
                <div className={styles.summaryValue}>{formatCurrency(claim.total_amount, claim.currency)}</div>
              </div>
            </div>
            {claim.approved_amount !== null && (
              <div className={styles.summaryCard}>
                <span className={styles.summaryIcon}>✅</span>
                <div>
                  <div className={styles.summaryLabel}>Approved Amount</div>
                  <div className={styles.summaryValue}>{formatCurrency(claim.approved_amount, claim.currency)}</div>
                </div>
              </div>
            )}
            <div className={styles.summaryCard}>
              <span className={styles.summaryIcon}>🏷️</span>
              <div>
                <div className={styles.summaryLabel}>Category</div>
                <div className={styles.summaryValue}>{claim.category.replace('_', ' ')}</div>
              </div>
            </div>
            <div className={styles.summaryCard}>
              <span className={styles.summaryIcon}>📄</span>
              <div>
                <div className={styles.summaryLabel}>Documents</div>
                <div className={styles.summaryValue}>{claim.documents.length}</div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${activeTab === 'details' ? styles.active : ''}`}
              onClick={() => setActiveTab('details')}
            >
              📋 Details
            </button>
            <button
              className={`${styles.tab} ${activeTab === 'documents' ? styles.active : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              📄 Documents ({claim.documents.length})
            </button>
            <button
              className={`${styles.tab} ${activeTab === 'timeline' ? styles.active : ''}`}
              onClick={() => setActiveTab('timeline')}
            >
              🕐 Timeline
            </button>
          </div>

          {/* Tab Content */}
          <div className={styles.tabContent}>
            {activeTab === 'details' && (
              <div className={styles.detailsGrid}>
                {/* Extracted Fields */}
                <div className={styles.section}>
                  <h3>
                    <span>📝</span>
                    Extracted Information
                  </h3>
                  <div className={styles.fieldsList}>
                    {claim.extracted_fields.length > 0 ? (
                      claim.extracted_fields.map(field => (
                        <div key={field.id} className={styles.fieldItem}>
                          <span className={styles.fieldLabel}>
                            {FIELD_LABELS[field.field_name] || field.field_name}
                          </span>
                          <span className={styles.fieldValue}>{field.value || 'N/A'}</span>
                          {field.source === 'user' && (
                            <span className={styles.editedBadge}>Edited</span>
                          )}
                          {field.confidence && field.confidence < 0.7 && (
                            <span className={styles.lowConfidenceBadge}>Low Confidence</span>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className={styles.emptyText}>No extracted fields available</p>
                    )}
                  </div>
                </div>

                {/* Validation Results */}
                <div className={styles.section}>
                  <h3>
                    <span>✅</span>
                    Validation Results
                  </h3>
                  <div className={styles.validationList}>
                    {claim.validation_results.length > 0 ? (
                      claim.validation_results.map(result => (
                        <div 
                          key={result.id} 
                          className={`${styles.validationItem} ${result.passed ? styles.passed : styles.failed}`}
                        >
                          <span>{result.passed ? '✅' : '❌'}</span>
                          <div>
                            <strong>{result.rule_name}</strong>
                            <p>{result.message}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className={styles.emptyText}>No validation results</p>
                    )}
                  </div>
                </div>

                {/* Decisions */}
                {claim.decisions.length > 0 && (
                  <div className={styles.section}>
                    <h3>
                      <span>⚖️</span>
                      Decisions
                    </h3>
                    <div className={styles.decisionsList}>
                      {claim.decisions.map(decision => (
                        <div key={decision.id} className={styles.decisionItem}>
                          <div className={styles.decisionHeader}>
                            <span className={`${styles.decisionBadge} ${styles[decision.decision]}`}>
                              {decision.decision}
                            </span>
                            <span className={styles.decisionDate}>{formatDate(decision.created_at)}</span>
                          </div>
                          {decision.reason_description && (
                            <p className={styles.decisionReason}>{decision.reason_description}</p>
                          )}
                          {decision.notes && (
                            <p className={styles.decisionNotes}>Notes: {decision.notes}</p>
                          )}
                          {decision.approved_amount !== null && (
                            <p className={styles.decisionAmount}>
                              Approved: {formatCurrency(decision.approved_amount, claim.currency)}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'documents' && (
              <div className={styles.documentsGrid}>
                {claim.documents.length > 0 ? (
                  claim.documents.map(doc => (
                    <div key={doc.id} className={styles.documentCard}>
                      <div className={styles.documentIcon}>
                        {doc.file_type?.includes('pdf') ? '📄' : '🖼️'}
                      </div>
                      <div className={styles.documentInfo}>
                        <span className={styles.documentName}>{doc.file_name}</span>
                        <span className={styles.documentMeta}>
                          {(doc.file_size / 1024).toFixed(1)} KB
                          {doc.ocr_quality_score && ` • OCR: ${(doc.ocr_quality_score * 100).toFixed(0)}%`}
                        </span>
                        <span className={styles.documentDate}>{formatDate(doc.created_at)}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyText}>No documents attached</p>
                )}
              </div>
            )}

            {activeTab === 'timeline' && (
              <div className={styles.timeline}>
                {timeline.length > 0 ? (
                  timeline.map((event, index) => (
                    <div key={event.id || index} className={styles.timelineItem}>
                      <div className={styles.timelineDot}></div>
                      <div className={styles.timelineContent}>
                        <div className={styles.timelineHeader}>
                          <span className={styles.timelineAction}>{event.action.replace('_', ' ')}</span>
                          <span className={styles.timelineDate}>{formatDate(event.timestamp)}</span>
                        </div>
                        <span className={styles.timelineActor}>by {event.actor}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyText}>No activity recorded yet</p>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className={styles.modalOverlay} onClick={() => setShowDeleteModal(false)}>
          <div className={styles.modal} onClick={e => e.stopPropagation()}>
            <h3>🗑️ Delete Claim?</h3>
            <p>Are you sure you want to delete claim <strong>{claim.claim_number}</strong>?</p>
            <p className={styles.modalWarning}>This action cannot be undone.</p>
            <div className={styles.modalActions}>
              <button 
                onClick={() => setShowDeleteModal(false)}
                className={styles.cancelBtn}
              >
                Cancel
              </button>
              <button 
                onClick={handleDelete}
                disabled={isDeleting}
                className={styles.confirmDeleteBtn}
              >
                {isDeleting ? 'Deleting...' : 'Delete Claim'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

