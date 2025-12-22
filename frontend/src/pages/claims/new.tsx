import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ClaimWizard from '@/components/ClaimWizard';
import styles from '@/styles/Claims.module.css';

export default function NewClaimPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, isAgent } = useAuth();
  const [showHelpModal, setShowHelpModal] = useState(false);

  // Redirect if not authenticated or if agent (agents don't submit claims)
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
    if (!isLoading && isAgent) {
      router.push('/claims');
    }
  }, [isLoading, isAuthenticated, isAgent, router]);

  if (isLoading || !user) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Loading...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <>
      <Head>
        <title>Submit New Claim | ClaimSphere AI</title>
        <meta name="description" content="Submit a new insurance claim" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Breadcrumb */}
          <div style={{ marginBottom: '24px' }}>
            <Link href="/claims" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>
              ← Back to My Claims
            </Link>
          </div>

          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <h1 className={styles.title}>
                  <span>📝</span>
                  Submit New Claim
                </h1>
                <button
                  onClick={() => setShowHelpModal(true)}
                  className={styles.helpButton}
                  title="Help & Information"
                >
                  <span style={{ fontSize: '0.875rem' }}>Help</span>
                  <span>❓</span>
                </button>
              </div>
              <p className={styles.subtitle}>
                Upload your documents and we'll extract the claim information automatically
              </p>
            </div>
          </div>

          {/* Claim Wizard */}
          <ClaimWizard onComplete={() => router.push('/claims')} />
        </div>
      </main>

      {/* Help Modal */}
      {showHelpModal && (
        <div className={styles.modalOverlay} onClick={() => setShowHelpModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>
                <span>❓</span>
                Claim Processing Help
              </h2>
              <button
                onClick={() => setShowHelpModal(false)}
                className={styles.modalClose}
                aria-label="Close"
              >
                ✕
              </button>
            </div>
            
            <div className={styles.modalBody}>
              <section className={styles.helpSection}>
                <h3>📋 Processing Steps</h3>
                <ol className={styles.helpList}>
                  <li>
                    <strong>Upload Documents</strong>
                    <p>Upload your claim forms, receipts, medical records, or insurance documents</p>
                  </li>
                  <li>
                    <strong>AI Processing</strong>
                    <p>Our system uses PaddleOCR and ClaimSphere AI (powered by ERNIE 4.5) to extract information</p>
                  </li>
                  <li>
                    <strong>Review & Submit</strong>
                    <p>Review the extracted information, make corrections if needed, and submit your claim</p>
                  </li>
                </ol>
              </section>

              <section className={styles.helpSection}>
                <h3>📄 Document Requirements</h3>
                <ul className={styles.helpList}>
                  <li>
                    <strong>Supported Formats:</strong> PDF, JPG, PNG
                  </li>
                  <li>
                    <strong>File Size:</strong> Maximum 10MB per file
                  </li>
                  <li>
                    <strong>Quality:</strong> Clear, readable images for best OCR results
                  </li>
                  <li>
                    <strong>Multiple Documents:</strong> You can upload multiple files if needed
                  </li>
                </ul>
              </section>

              <section className={styles.helpSection}>
                <h3>✨ AI-Powered Features</h3>
                <ul className={styles.helpList}>
                  <li>
                    <strong>Automatic Field Extraction:</strong> Claimant name, dates, amounts, policy numbers
                  </li>
                  <li>
                    <strong>Smart Validation:</strong> AI validates claim data for completeness and consistency
                  </li>
                  <li>
                    <strong>Auto-Categorization:</strong> Claims are automatically categorized (medical, insurance, travel, etc.)
                  </li>
                  <li>
                    <strong>Confidence Scoring:</strong> See confidence levels for extracted fields
                  </li>
                </ul>
              </section>

              <section className={styles.helpSection}>
                <h3>⏱️ What to Expect</h3>
                <ul className={styles.helpList}>
                  <li>
                    <strong>Processing Time:</strong> Usually 30-60 seconds for document processing
                  </li>
                  <li>
                    <strong>Auto-Approval:</strong> Low-risk claims may be automatically approved
                  </li>
                  <li>
                    <strong>Manual Review:</strong> Some claims require agent review (typically 1-2 days)
                  </li>
                  <li>
                    <strong>Status Updates:</strong> Track your claim status in real-time
                  </li>
                </ul>
              </section>

              <section className={styles.helpSection}>
                <h3>💡 Tips for Best Results</h3>
                <ul className={styles.helpList}>
                  <li>Ensure documents are clear and well-lit</li>
                  <li>Upload all relevant supporting documents</li>
                  <li>Review extracted information carefully before submitting</li>
                  <li>Correct any fields that were extracted incorrectly</li>
                  <li>Include policy numbers and dates when available</li>
                </ul>
              </section>

              <section className={styles.helpSection}>
                <h3>🆘 Need More Help?</h3>
                <p>If you encounter any issues or have questions, please contact our support team:</p>
                <ul className={styles.helpList}>
                  <li>Email: support@claimsphere.ai</li>
                  <li>Phone: 1-800-CLAIMS-AI</li>
                  <li>Live Chat: Available in the bottom right corner</li>
                </ul>
              </section>
            </div>

            <div className={styles.modalFooter}>
              <button
                onClick={() => setShowHelpModal(false)}
                className={styles.modalCloseButton}
              >
                Got it, thanks!
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

