import { useState, useCallback } from 'react';
import axios from 'axios';
import { API_URL } from '@/config/api';
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

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_URL}/api/claims/upload?process_with_ai=true`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const claim = response.data.claim;
      setSuccess(`Claim processed successfully! Claim Number: ${claim.claim_number || 'N/A'}, Claimant: ${claim.claimant_name}`);
      onClaimAdded();
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error processing file');
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
      </div>

      {uploading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing with PaddleOCR and ERNIE...</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
    </div>
  );
}

