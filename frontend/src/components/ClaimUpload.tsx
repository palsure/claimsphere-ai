import { useState, useCallback } from 'react';
import { claimsAPI } from '@/utils/api';
import styles from './ClaimUpload.module.css';

interface ClaimUploadProps {
  onClaimAdded: () => void;
}

export default function ClaimUpload({ onClaimAdded }: ClaimUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = async (file: File) => {
    // Validate file type
    const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a PDF, JPG, or PNG file.');
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await claimsAPI.upload(file);
      const claim = response.claim || response;
      
      setSuccess(
        `Claim processed successfully! Claim Number: ${claim.claim_number || 'N/A'}` +
        (claim.provider_name ? `, Provider: ${claim.provider_name}` : '') +
        (claim.total_amount ? `, Amount: $${claim.total_amount.toFixed(2)}` : '')
      );
      onClaimAdded();
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Error processing file';
      setError(message);
    } finally {
      setUploading(false);
    }
  };

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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className={styles.card}>
      <h2>📤 Upload Claim Document</h2>
      <p className={styles.subtitle}>Upload claim forms, receipts, medical records, or insurance documents</p>
      
      <div
        className={`${styles.uploadArea} ${dragActive ? styles.dragActive : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className={styles.uploadIcon}>📄</div>
        <p>Drag & drop your claim document here</p>
        <p className={styles.orText}>or</p>
        <label className={styles.fileLabel}>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleChange}
            disabled={uploading}
            className={styles.fileInput}
          />
          <span className="btn">Choose File</span>
        </label>
        <p className={styles.hint}>Supports PDF, JPG, PNG (max 10MB)</p>
      </div>

      {uploading && (
        <div className={styles.processing}>
          <div className={styles.spinner}></div>
          <p>Processing with PaddleOCR and ERNIE AI...</p>
          <p className={styles.processingHint}>This may take a few seconds</p>
        </div>
      )}

      {error && (
        <div className={styles.error}>
          <span>⚠️</span> {error}
        </div>
      )}
      
      {success && (
        <div className={styles.success}>
          <span>✅</span> {success}
        </div>
      )}
    </div>
  );
}
