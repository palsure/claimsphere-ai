import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/router';
import { claimsAPI } from '@/utils/api';
import RolePlayingReview from './RolePlayingReview';
import styles from './ClaimWizard.module.css';

interface ClaimWizardProps {
  onComplete?: () => void;
}

interface ExtractedField {
  value: string;
  confidence: number;
  source: string;
}

interface ClaimStatus {
  claim_id: string;
  claim_number: string;
  status: string;
  stage: string;
  stage_message: string;
  ocr_quality_score: number | null;
  extraction_confidence: number | null;
  duplicate_score: number;
  is_duplicate: boolean;
  document_count: number;
  extracted_fields: Record<string, ExtractedField>;
  low_confidence_fields: string[];
  validation_messages: Array<{
    rule_name: string;
    passed: boolean;
    message: string;
    severity: string;
    details_json?: any;
  }>;
  decision_details?: {
    reason_code: string;
    reason_description: string;
    notes: string;
    is_auto_decision: boolean;
    created_at: string;
  };
  duplicate_matches?: Array<{
    claim_id: string;
    claim_number: string;
    similarity_score: number;
    match_reasons?: any;
  }>;
  can_edit: boolean;
  can_submit: boolean;
  can_delete: boolean;
}

const CATEGORIES = [
  { value: 'auto', label: '🔮 Auto-detect' },
  { value: 'medical', label: '🏥 Medical' },
  { value: 'dental', label: '🦷 Dental' },
  { value: 'vision', label: '👁️ Vision' },
  { value: 'pharmacy', label: '💊 Pharmacy' },
  { value: 'mental_health', label: '🧠 Mental Health' },
  { value: 'hospital', label: '🏨 Hospital' },
  { value: 'emergency', label: '🚑 Emergency' },
  { value: 'other', label: '📋 Other' },
];

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

export default function ClaimWizard({ onComplete }: ClaimWizardProps) {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Step 1 state
  const [files, setFiles] = useState<File[]>([]);
  const [category, setCategory] = useState('auto');
  const [serviceDate, setServiceDate] = useState('');
  const [notes, setNotes] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [sampleFiles, setSampleFiles] = useState<Array<{filename: string; name: string; size: number; type: string}>>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);
  
  // Step 2 & 3 state
  const [claimId, setClaimId] = useState<string | null>(null);
  const [claimStatus, setClaimStatus] = useState<ClaimStatus | null>(null);
  const [editedFields, setEditedFields] = useState<Record<string, string>>({});
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);
  const [pollCount, setPollCount] = useState(0);
  const [rolePlayingReview, setRolePlayingReview] = useState<any>(null);
  const [showReview, setShowReview] = useState(false);
  const [loadingReview, setLoadingReview] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  // Load sample files on mount
  useEffect(() => {
    const loadSamples = async () => {
      try {
        setLoadingSamples(true);
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/samples`);
        const data = await response.json();
        setSampleFiles(data.samples || []);
      } catch (err) {
        console.error('Error loading sample files:', err);
      } finally {
        setLoadingSamples(false);
      }
    };
    loadSamples();
  }, []);

  // Load a sample file
  const loadSampleFile = async (sample: {filename: string; name: string; type: string}) => {
    try {
      setLoadingSamples(true);
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/samples/${sample.filename}`);
      const blob = await response.blob();
      const file = new File([blob], sample.filename, { type: sample.type });
      setFiles(prev => [...prev, file]);
      setError(null);
    } catch (err: any) {
      setError(`Error loading sample file: ${err.message}`);
    } finally {
      setLoadingSamples(false);
    }
  };

  // Poll claim status during processing
  const pollStatus = useCallback(async (id: string) => {
    try {
      // Limit polling to prevent infinite loops
      setPollCount(prev => {
        if (prev > 30) { // Max 30 polls (60 seconds)
          if (pollInterval) {
            clearInterval(pollInterval);
            setPollInterval(null);
          }
          setIsProcessing(false);
          return prev;
        }
        return prev + 1;
      });
      
      const status = await claimsAPI.getStatus(id);
      setClaimStatus(status);
      
      // Stop polling when processing is complete
      if (status.stage !== 'extracting' && status.stage !== 'validating') {
        if (pollInterval) {
          clearInterval(pollInterval);
          setPollInterval(null);
        }
        setIsProcessing(false);
        
        // Handle denied status - show denied summary
        if (status.stage === 'denied' || status.status === 'denied') {
          // Stay on step 2 but show denied summary instead of processing
          return;
        }
        
        // Move to step 3 when ready for review
        if (status.stage === 'review' || status.stage === 'pending' || status.can_edit) {
          setStep(3);
        }
      }
    } catch (err) {
      console.error('Error polling status:', err);
      // Stop polling after multiple errors
      if (pollCount > 5) {
        if (pollInterval) {
          clearInterval(pollInterval);
          setPollInterval(null);
        }
        setIsProcessing(false);
      }
    }
  }, [pollInterval, pollCount]);

  // Handle file selection
  const handleFiles = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;
    
    const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    const validFiles: File[] = [];
    
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      if (validTypes.includes(file.type) && file.size <= 10 * 1024 * 1024) {
        validFiles.push(file);
      }
    }
    
    setFiles(prev => [...prev, ...validFiles]);
    setError(null);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Handle drag and drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  }, []);

  // Step 1: Upload and submit
  const handleStep1Submit = async () => {
    if (files.length === 0) {
      setError('Please upload at least one document');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setStep(2);

    try {
      // Upload the first file to create the claim
      const response = await claimsAPI.upload(files[0], true);
      const claim = response.claim || response;
      setClaimId(claim.id);
      
      // Clear processing state immediately after upload
      setIsProcessing(false);
      
      // Reset poll count
      setPollCount(0);
      
      // Start polling for status updates (non-blocking)
      const interval = setInterval(() => pollStatus(claim.id), 2000);
      setPollInterval(interval);
      
      // Initial status fetch (non-blocking, with timeout)
      pollStatus(claim.id).catch((err) => {
        console.warn('Initial status fetch failed:', err);
      });
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error uploading document');
      setStep(1);
      setIsProcessing(false);
    }
  };

  // Step 3: Update fields and submit
  const handleFieldChange = (fieldName: string, value: string) => {
    setEditedFields(prev => ({ ...prev, [fieldName]: value }));
  };

  const handleSaveFields = async () => {
    if (!claimId || Object.keys(editedFields).length === 0) return;
    
    try {
      await claimsAPI.updateFields(claimId, editedFields);
      // Refresh status
      await pollStatus(claimId);
      setEditedFields({});
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error saving fields');
    }
  };

  const handleSubmitClaim = async () => {
    if (!claimId) return;
    
    setIsProcessing(true);
    setError(null);
    try {
      // Save any pending field edits first
      if (Object.keys(editedFields).length > 0) {
        await claimsAPI.updateFields(claimId, editedFields);
      }
      
      // Submit the claim
      await claimsAPI.submit(claimId);
      
      // Navigate immediately - don't wait for anything
      router.push(`/claims/${claimId}`);
      onComplete?.();
      
      // Reset processing state after navigation starts
      setIsProcessing(false);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error submitting claim');
      setIsProcessing(false);
    }
  };
  
  const handleContinueAfterReview = () => {
    setShowReview(false);
    if (claimId) {
      router.push(`/claims/${claimId}`);
      onComplete?.();
    }
  };

  const getFieldValue = (fieldName: string): string => {
    if (editedFields[fieldName] !== undefined) {
      return editedFields[fieldName];
    }
    return claimStatus?.extracted_fields[fieldName]?.value || '';
  };

  const isLowConfidence = (fieldName: string): boolean => {
    return claimStatus?.low_confidence_fields.includes(fieldName) || false;
  };

  return (
    <div className={styles.wizard}>
      {/* Progress Steps */}
      <div className={styles.progressBar}>
        <div className={`${styles.step} ${step >= 1 ? styles.active : ''} ${step > 1 ? styles.completed : ''}`}>
          <div className={styles.stepNumber}>{step > 1 ? '✓' : '1'}</div>
          <span className={styles.stepLabel}>Upload</span>
        </div>
        <div className={styles.stepLine} />
        <div className={`${styles.step} ${step >= 2 ? styles.active : ''} ${step > 2 ? styles.completed : ''}`}>
          <div className={styles.stepNumber}>{step > 2 ? '✓' : '2'}</div>
          <span className={styles.stepLabel}>Processing</span>
        </div>
        <div className={styles.stepLine} />
        <div className={`${styles.step} ${step >= 3 ? styles.active : ''}`}>
          <div className={styles.stepNumber}>3</div>
          <span className={styles.stepLabel}>Review</span>
        </div>
      </div>

      {error && (
        <div className={styles.error}>
          <span>⚠️</span> {error}
          <button onClick={() => setError(null)} className={styles.errorClose}>×</button>
        </div>
      )}

      {/* Step 1: Upload & Intent */}
      {step === 1 && (
        <div className={styles.stepContent}>
          <h2 className={styles.stepTitle}>
            <span>📤</span> Upload Documents
          </h2>
          <p className={styles.stepSubtitle}>
            Upload claim forms, receipts, medical records, or insurance documents
          </p>

          {/* Horizontal Layout: Upload + Sample Files */}
          <div className={styles.uploadContainer}>
            {/* Upload Section - Reduced Size */}
            <div className={styles.uploadSection}>
              <div
                className={`${styles.uploadArea} ${dragActive ? styles.dragActive : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className={styles.uploadIcon}>📄</div>
                <p>Drag & drop here</p>
                <p className={styles.orText}>or</p>
                <label className={styles.fileLabel}>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFiles(e.target.files)}
                    multiple
                    className={styles.fileInput}
                  />
                  <span className={styles.uploadBtn}>Choose Files</span>
                </label>
                <p className={styles.hint}>PDF, JPG, PNG (max 10MB)</p>
              </div>
            </div>

            {/* Sample Files Section */}
            {sampleFiles.length > 0 && (
              <div className={styles.sampleFilesSection}>
                <div className={styles.sampleFilesHeader}>
                  <h3>
                    <span>📋</span> Try Sample Files
                  </h3>
                </div>
                <div className={styles.sampleFilesGrid}>
                  {sampleFiles.map((sample) => (
                    <button
                      key={sample.filename}
                      onClick={() => loadSampleFile(sample)}
                      disabled={loadingSamples}
                      className={styles.sampleFileCard}
                      title={`Load ${sample.name}`}
                    >
                      <div className={styles.sampleFileIcon}>
                        {sample.type.includes('pdf') ? '📄' : '🖼️'}
                      </div>
                      <div className={styles.sampleFileInfo}>
                        <div className={styles.sampleFileName}>
                          {sample.name}
                          <span className={styles.fileExtension}>
                            {sample.filename.split('.').pop()?.toUpperCase()}
                          </span>
                        </div>
                        <div className={styles.sampleFileSize}>
                          {(sample.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                      <div className={styles.sampleFileAction}>
                        {loadingSamples ? '⏳' : '⬇️'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {files.length > 0 && (
            <div className={styles.fileList}>
              <h3>Selected Files ({files.length})</h3>
              {files.map((file, index) => (
                <div key={index} className={styles.fileItem}>
                  <span className={styles.fileIcon}>
                    {file.type.includes('pdf') ? '📄' : '🖼️'}
                  </span>
                  <span className={styles.fileName}>{file.name}</span>
                  <span className={styles.fileSize}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                  <button
                    onClick={() => removeFile(index)}
                    className={styles.removeFile}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className={styles.formSection}>
            <div className={styles.formGroup}>
              <label>Claim Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className={styles.select}
              >
                {CATEGORIES.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Date of Service (Optional)</label>
              <input
                type="date"
                value={serviceDate}
                onChange={(e) => setServiceDate(e.target.value)}
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Notes (Optional)</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any additional information..."
                className={styles.textarea}
                rows={3}
              />
            </div>
          </div>

          <div className={styles.actions}>
            <button
              onClick={() => router.back()}
              className={styles.secondaryBtn}
            >
              Cancel
            </button>
            <button
              onClick={handleStep1Submit}
              disabled={files.length === 0}
              className={styles.primaryBtn}
            >
              Upload & Process
              <span>→</span>
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Processing or Denied Summary */}
      {step === 2 && (
        <div className={styles.stepContent}>
          {/* Show denied summary if claim is denied */}
          {claimStatus?.stage === 'denied' || claimStatus?.status === 'denied' ? (
            <>
              <h2 className={styles.stepTitle}>
                <span>❌</span> Claim Denied
              </h2>
              
              <div className={styles.deniedCard}>
                <div className={styles.deniedHeader}>
                  <div className={styles.deniedIcon}>❌</div>
                  <h3>Your claim has been denied</h3>
                  <p className={styles.deniedSubtitle}>
                    Claim Number: {claimStatus?.claim_number}
                  </p>
                </div>

                {/* Decision Details */}
                {claimStatus?.decision_details && (
                  <div className={styles.deniedSection}>
                    <h4>Reason for Denial</h4>
                    <div className={styles.deniedReason}>
                      <div className={styles.reasonCode}>
                        <strong>Code:</strong> {claimStatus.decision_details.reason_code || 'N/A'}
                      </div>
                      <div className={styles.reasonDescription}>
                        {claimStatus.decision_details.reason_description || claimStatus.decision_details.notes || 'No reason provided'}
                      </div>
                      {claimStatus.decision_details.is_auto_decision && (
                        <div className={styles.autoDecisionBadge}>
                          🤖 Auto-decision by system
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Validation Errors */}
                {claimStatus?.validation_messages && claimStatus.validation_messages.some((vm: any) => !vm.passed && vm.severity === 'error') && (
                  <div className={styles.deniedSection}>
                    <h4>Validation Errors</h4>
                    <div className={styles.validationErrorsList}>
                      {claimStatus.validation_messages
                        .filter((vm: any) => !vm.passed && vm.severity === 'error')
                        .map((vm: any, index: number) => (
                          <div key={index} className={styles.validationError}>
                            <div className={styles.errorHeader}>
                              <span className={styles.errorIcon}>⚠️</span>
                              <strong>{vm.rule_name || 'Validation Error'}</strong>
                            </div>
                            <p>{vm.message}</p>
                            {vm.details_json && (
                              <div className={styles.errorDetails}>
                                {vm.details_json.duplicate_score && (
                                  <div>
                                    <strong>Similarity Score:</strong> {(vm.details_json.duplicate_score * 100).toFixed(0)}%
                                  </div>
                                )}
                                {vm.details_json.matched_claims && vm.details_json.matched_claims.length > 0 && (
                                  <div>
                                    <strong>Matched Claims:</strong> {vm.details_json.matched_claims.join(', ')}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Duplicate Matches */}
                {claimStatus?.duplicate_matches && claimStatus.duplicate_matches.length > 0 && (
                  <div className={styles.deniedSection}>
                    <h4>Duplicate Matches</h4>
                    <div className={styles.duplicateMatchesList}>
                      {claimStatus.duplicate_matches.map((match: any, index: number) => (
                        <div key={index} className={styles.duplicateMatch}>
                          <div className={styles.matchHeader}>
                            <span>🔗</span>
                            <strong>Claim {match.claim_number}</strong>
                            <span className={styles.similarityScore}>
                              {(match.similarity_score * 100).toFixed(0)}% similar
                            </span>
                          </div>
                          {match.match_reasons && (
                            <div className={styles.matchReasons}>
                              {Array.isArray(match.match_reasons.reasons) && (
                                <ul>
                                  {match.match_reasons.reasons.map((reason: string, i: number) => (
                                    <li key={i}>{reason}</li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Extracted Information Summary */}
                {claimStatus?.extracted_fields && Object.keys(claimStatus.extracted_fields).length > 0 && (
                  <div className={styles.deniedSection}>
                    <h4>Claim Information</h4>
                    <div className={styles.claimInfoGrid}>
                      {Object.entries(claimStatus.extracted_fields).map(([field, data]: [string, any]) => (
                        <div key={field} className={styles.infoItem}>
                          <label>{field.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}</label>
                          <div>{data.value || 'N/A'}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className={styles.deniedActions}>
                  <button
                    onClick={() => router.push('/claims')}
                    className={styles.primaryBtn}
                  >
                    View All Claims
                  </button>
                  <button
                    onClick={() => {
                      setStep(1);
                      setFiles([]);
                      setClaimId(null);
                      setClaimStatus(null);
                    }}
                    className={styles.secondaryBtn}
                  >
                    Submit New Claim
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              <h2 className={styles.stepTitle}>
                <span>⚙️</span> Processing Your Claim
              </h2>
              
              <div className={styles.processingCard}>
                <div className={styles.spinner}></div>
                <p className={styles.processingMessage}>
                  {claimStatus?.stage_message || 'Uploading document...'}
                </p>
                
                <div className={styles.processingStages}>
                  <div className={`${styles.stage} ${claimStatus?.stage === 'extracting' || claimStatus?.stage === 'validating' || claimStatus?.stage === 'review' ? styles.completed : styles.active}`}>
                    <span>📤</span> Uploading
                  </div>
                  <div className={`${styles.stage} ${claimStatus?.stage === 'validating' || claimStatus?.stage === 'review' ? styles.completed : claimStatus?.stage === 'extracting' ? styles.active : ''}`}>
                    <span>🔍</span> Extracting
                  </div>
                  <div className={`${styles.stage} ${claimStatus?.stage === 'review' ? styles.completed : claimStatus?.stage === 'validating' ? styles.active : ''}`}>
                    <span>✅</span> Validating
                  </div>
                </div>

                {claimStatus?.ocr_quality_score && (
                  <div className={styles.qualityInfo}>
                    <span>OCR Quality: </span>
                    <span className={claimStatus.ocr_quality_score > 0.7 ? styles.good : styles.warning}>
                      {(claimStatus.ocr_quality_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Step 3: Review & Confirm */}
      {step === 3 && claimStatus && (
        <div className={styles.stepContent}>
          <h2 className={styles.stepTitle}>
            <span>📝</span> Review & Confirm
          </h2>
          <p className={styles.stepSubtitle}>
            Review the extracted information and make corrections if needed
          </p>

          {claimStatus.is_duplicate && (
            <div className={styles.duplicateWarning}>
              <span>⚠️</span>
              <div>
                <strong>Potential Duplicate Detected</strong>
                <p>This claim appears similar to an existing claim (Score: {(claimStatus.duplicate_score * 100).toFixed(0)}%)</p>
              </div>
            </div>
          )}

          <div className={styles.reviewGrid}>
            <div className={styles.fieldsSection}>
              <h3>
                <span>📋</span> Extracted Information
              </h3>
              
              <div className={styles.fieldsList}>
                {Object.entries(FIELD_LABELS).map(([fieldName, label]) => {
                  const value = getFieldValue(fieldName);
                  const lowConfidence = isLowConfidence(fieldName);
                  const isEdited = editedFields[fieldName] !== undefined;
                  
                  return (
                    <div 
                      key={fieldName} 
                      className={`${styles.fieldItem} ${lowConfidence ? styles.lowConfidence : ''} ${isEdited ? styles.edited : ''}`}
                    >
                      <label>
                        {label}
                        {lowConfidence && <span className={styles.warningBadge}>Low Confidence</span>}
                        {isEdited && <span className={styles.editedBadge}>Edited</span>}
                      </label>
                      <input
                        type={fieldName === 'total_amount' ? 'number' : 'text'}
                        value={value}
                        onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                        className={styles.fieldInput}
                        placeholder={`Enter ${label.toLowerCase()}`}
                      />
                    </div>
                  );
                })}
              </div>

              {Object.keys(editedFields).length > 0 && (
                <button onClick={handleSaveFields} className={styles.saveBtn}>
                  💾 Save Changes
                </button>
              )}
            </div>

            <div className={styles.validationSection}>
              <h3>
                <span>✅</span> Validation Results
              </h3>
              
              {claimStatus.validation_messages.length > 0 ? (
                <div className={styles.validationList}>
                  {claimStatus.validation_messages.map((msg, idx) => {
                    const isError = !msg.passed && msg.severity === 'error';
                    const isWarning = !msg.passed && msg.severity === 'warning';
                    const isPassed = msg.passed;
                    
                    let icon = '✅';
                    let className = styles.passed;
                    if (isError) {
                      icon = '❌';
                      className = styles.failed;
                    } else if (isWarning) {
                      icon = '⚠️';
                      className = styles.warning;
                    }
                    
                    return (
                      <div 
                        key={idx} 
                        className={`${styles.validationItem} ${className}`}
                      >
                        <span>{icon}</span>
                        <div>
                          <strong>{msg.rule_name}</strong>
                          <p>{msg.message}</p>
                          {msg.severity && (
                            <span className={styles.severityBadge}>
                              {msg.severity.toUpperCase()}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className={styles.noValidation}>No validation issues found</p>
              )}

              <div className={styles.claimSummary}>
                <h4>Claim Summary</h4>
                <div className={styles.summaryItem}>
                  <span>Claim Number</span>
                  <strong>{claimStatus.claim_number}</strong>
                </div>
                <div className={styles.summaryItem}>
                  <span>Documents</span>
                  <strong>{claimStatus.document_count}</strong>
                </div>
                <div className={styles.summaryItem}>
                  <span>Status</span>
                  <strong className={styles.statusBadge}>{claimStatus.status}</strong>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.actions}>
            <button
              onClick={() => setShowDeleteModal(true)}
              className={styles.dangerBtn}
            >
              🗑️ Delete Claim
            </button>
            {/* Only show submit button if claim can be submitted */}
            {claimStatus?.can_submit && (
              <button
                onClick={handleSubmitClaim}
                disabled={isProcessing}
                className={styles.primaryBtn}
              >
                {isProcessing ? 'Submitting...' : 'Submit for Review'}
                <span>→</span>
              </button>
            )}
            {/* Show CTA to view claims if claim is in a pending state */}
            {!claimStatus?.can_submit && ['pending_review', 'submitted', 'pended'].includes(claimStatus?.status || '') && (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                padding: '16px',
                background: 'var(--info-bg, rgba(59, 130, 246, 0.1))',
                border: '1px solid var(--info-border, rgba(59, 130, 246, 0.3))',
                borderRadius: '8px',
                flex: 1
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: 'var(--info-text, #1e40af)',
                  fontSize: '0.95rem',
                  fontWeight: '500'
                }}>
                  <span>ℹ️</span>
                  <span>This claim is already submitted and awaiting review.</span>
                </div>
                <button
                  onClick={() => router.push('/claims')}
                  className={styles.primaryBtn}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    width: '100%',
                    marginTop: '4px'
                  }}
                >
                  <span>📋</span>
                  View All Claims
                  <span>→</span>
                </button>
              </div>
            )}
            {/* Show message for other non-submittable states */}
            {!claimStatus?.can_submit && !['pending_review', 'submitted', 'pended'].includes(claimStatus?.status || '') && (
              <div style={{
                padding: '12px 16px',
                background: 'var(--warning-bg, rgba(251, 191, 36, 0.1))',
                border: '1px solid var(--warning, rgba(251, 191, 36, 0.3))',
                borderRadius: '8px',
                color: 'var(--warning-text, #92400e)',
                fontSize: '0.9rem'
              }}>
                ⚠️ Claim cannot be submitted in current state. 
                {claimStatus?.validation_messages?.some((vm: any) => !vm.passed && vm.severity === 'error') && 
                  ' Fix validation errors and resubmit.'}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className={styles.modalOverlay} onClick={() => setShowDeleteModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>🗑️ Delete Claim?</h3>
            <p className={styles.modalSubtitle}>
              Are you sure you want to delete this claim?
            </p>
            <p className={styles.modalWarning}>
              {claimStatus && (
                <>
                  <strong>Claim #{claimStatus.claim_number}</strong>
                  <br />
                </>
              )}
              <span style={{ color: 'var(--danger)', fontSize: '0.9rem' }}>
                This action cannot be undone.
              </span>
            </p>
            <div className={styles.modalActions}>
              <button
                onClick={() => setShowDeleteModal(false)}
                className={styles.cancelBtn}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  if (!claimId) return;
                  setIsDeleting(true);
                  try {
                    await claimsAPI.delete(claimId);
                    router.push('/claims');
                  } catch (error: any) {
                    console.error('Error deleting claim:', error);
                    alert(error.response?.data?.detail || 'Error deleting claim');
                    setIsDeleting(false);
                  }
                }}
                className={styles.dangerBtn}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Claim'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

