/**
 * New Claim Submission Page
 */
import { useState, useRef } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '../../../components/DashboardLayout';
import { claimsAPI, plansAPI } from '../../../utils/api';
import styles from '../../../styles/ClaimForm.module.css';

interface ClaimFormData {
  category: string;
  total_amount: string;
  currency: string;
  service_date: string;
  provider_name: string;
  provider_npi: string;
  description: string;
  plan_id: string;
}

export default function NewClaim() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [formData, setFormData] = useState<ClaimFormData>({
    category: 'medical',
    total_amount: '',
    currency: 'USD',
    service_date: '',
    provider_name: '',
    provider_npi: '',
    description: '',
    plan_id: '',
  });
  
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles([...files, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (asDraft: boolean = false) => {
    setError('');
    setSubmitting(true);
    
    try {
      // Validate required fields
      if (!formData.total_amount || parseFloat(formData.total_amount) <= 0) {
        throw new Error('Please enter a valid claim amount');
      }
      
      // Create the claim
      const claimData = {
        category: formData.category,
        total_amount: parseFloat(formData.total_amount),
        currency: formData.currency,
        service_date: formData.service_date || undefined,
        provider_name: formData.provider_name || undefined,
        provider_npi: formData.provider_npi || undefined,
        description: formData.description || undefined,
        plan_id: formData.plan_id || undefined,
      };
      
      const claim = await claimsAPI.create(claimData);
      
      // Upload documents if any
      if (files.length > 0) {
        setUploading(true);
        for (const file of files) {
          await claimsAPI.uploadDocument(claim.id, file);
        }
        setUploading(false);
      }
      
      // Submit if not saving as draft
      if (!asDraft) {
        await claimsAPI.submit(claim.id);
      }
      
      // Redirect to claim detail
      router.push(`/dashboard/claims/${claim.id}`);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create claim');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DashboardLayout title="Submit New Claim">
      <div className={styles.container}>
        {/* Progress Steps */}
        <div className={styles.steps}>
          <div className={`${styles.step} ${step >= 1 ? styles.active : ''}`}>
            <span className={styles.stepNumber}>1</span>
            <span className={styles.stepLabel}>Claim Details</span>
          </div>
          <div className={styles.stepLine}></div>
          <div className={`${styles.step} ${step >= 2 ? styles.active : ''}`}>
            <span className={styles.stepNumber}>2</span>
            <span className={styles.stepLabel}>Documents</span>
          </div>
          <div className={styles.stepLine}></div>
          <div className={`${styles.step} ${step >= 3 ? styles.active : ''}`}>
            <span className={styles.stepNumber}>3</span>
            <span className={styles.stepLabel}>Review</span>
          </div>
        </div>

        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}

        {/* Step 1: Claim Details */}
        {step === 1 && (
          <div className={styles.formSection}>
            <h2>Claim Details</h2>
            <p className={styles.sectionDescription}>
              Enter the details of your insurance claim.
            </p>
            
            <div className={styles.formGrid}>
              <div className={styles.formGroup}>
                <label htmlFor="category">Claim Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className={styles.select}
                >
                  <option value="medical">Medical</option>
                  <option value="dental">Dental</option>
                  <option value="vision">Vision</option>
                  <option value="pharmacy">Pharmacy</option>
                  <option value="hospital">Hospital</option>
                  <option value="emergency">Emergency</option>
                  <option value="mental_health">Mental Health</option>
                  <option value="preventive">Preventive Care</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="total_amount">Claim Amount *</label>
                <div className={styles.amountInput}>
                  <select
                    name="currency"
                    value={formData.currency}
                    onChange={handleInputChange}
                    className={styles.currencySelect}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="CNY">CNY</option>
                  </select>
                  <input
                    type="number"
                    id="total_amount"
                    name="total_amount"
                    value={formData.total_amount}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    className={styles.input}
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="service_date">Date of Service</label>
                <input
                  type="date"
                  id="service_date"
                  name="service_date"
                  value={formData.service_date}
                  onChange={handleInputChange}
                  className={styles.input}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="provider_name">Provider Name</label>
                <input
                  type="text"
                  id="provider_name"
                  name="provider_name"
                  value={formData.provider_name}
                  onChange={handleInputChange}
                  placeholder="e.g., Dr. Smith or ABC Hospital"
                  className={styles.input}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="provider_npi">Provider NPI (Optional)</label>
                <input
                  type="text"
                  id="provider_npi"
                  name="provider_npi"
                  value={formData.provider_npi}
                  onChange={handleInputChange}
                  placeholder="10-digit NPI number"
                  maxLength={10}
                  className={styles.input}
                />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe the service or treatment received..."
                rows={4}
                className={styles.textarea}
              />
            </div>

            <div className={styles.formActions}>
              <button
                type="button"
                onClick={() => setStep(2)}
                className={styles.primaryButton}
                disabled={!formData.total_amount}
              >
                Continue to Documents →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Documents */}
        {step === 2 && (
          <div className={styles.formSection}>
            <h2>Upload Documents</h2>
            <p className={styles.sectionDescription}>
              Upload bills, receipts, EOBs, or other supporting documents. 
              AI will automatically extract information from your documents.
            </p>

            <div 
              className={styles.dropZone}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf"
                onChange={handleFileSelect}
                className={styles.fileInput}
              />
              <div className={styles.dropZoneContent}>
                <span className={styles.uploadIcon}>📄</span>
                <p>Click to upload or drag and drop</p>
                <span className={styles.uploadHint}>
                  PDF, PNG, JPG up to 10MB each
                </span>
              </div>
            </div>

            {files.length > 0 && (
              <div className={styles.fileList}>
                {files.map((file, index) => (
                  <div key={index} className={styles.fileItem}>
                    <span className={styles.fileIcon}>📎</span>
                    <span className={styles.fileName}>{file.name}</span>
                    <span className={styles.fileSize}>
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className={styles.removeFile}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className={styles.formActions}>
              <button
                type="button"
                onClick={() => setStep(1)}
                className={styles.secondaryButton}
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => setStep(3)}
                className={styles.primaryButton}
              >
                Review Claim →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <div className={styles.formSection}>
            <h2>Review & Submit</h2>
            <p className={styles.sectionDescription}>
              Review your claim details before submitting.
            </p>

            <div className={styles.reviewCard}>
              <div className={styles.reviewSection}>
                <h3>Claim Details</h3>
                <div className={styles.reviewGrid}>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Category</span>
                    <span className={styles.reviewValue}>{formData.category}</span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Amount</span>
                    <span className={styles.reviewValue}>
                      {formData.currency} {parseFloat(formData.total_amount || '0').toFixed(2)}
                    </span>
                  </div>
                  {formData.service_date && (
                    <div className={styles.reviewItem}>
                      <span className={styles.reviewLabel}>Service Date</span>
                      <span className={styles.reviewValue}>{formData.service_date}</span>
                    </div>
                  )}
                  {formData.provider_name && (
                    <div className={styles.reviewItem}>
                      <span className={styles.reviewLabel}>Provider</span>
                      <span className={styles.reviewValue}>{formData.provider_name}</span>
                    </div>
                  )}
                </div>
                {formData.description && (
                  <div className={styles.reviewDescription}>
                    <span className={styles.reviewLabel}>Description</span>
                    <p>{formData.description}</p>
                  </div>
                )}
              </div>

              <div className={styles.reviewSection}>
                <h3>Documents ({files.length})</h3>
                {files.length === 0 ? (
                  <p className={styles.noDocuments}>No documents uploaded</p>
                ) : (
                  <ul className={styles.documentList}>
                    {files.map((file, index) => (
                      <li key={index}>{file.name}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className={styles.formActions}>
              <button
                type="button"
                onClick={() => setStep(2)}
                className={styles.secondaryButton}
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => handleSubmit(true)}
                className={styles.secondaryButton}
                disabled={submitting}
              >
                Save as Draft
              </button>
              <button
                type="button"
                onClick={() => handleSubmit(false)}
                className={styles.primaryButton}
                disabled={submitting}
              >
                {submitting ? (uploading ? 'Uploading...' : 'Submitting...') : 'Submit Claim'}
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

