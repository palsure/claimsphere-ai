import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ClaimWizard from '@/components/ClaimWizard';
import styles from '@/styles/Claims.module.css';

export default function NewClaimPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, isAgent } = useAuth();

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
              <h1 className={styles.title}>
                <span>📝</span>
                Submit New Claim
              </h1>
              <p className={styles.subtitle}>
                Upload your documents and we'll extract the claim information automatically
              </p>
            </div>
          </div>

          {/* Claim Wizard */}
          <ClaimWizard onComplete={() => router.push('/claims')} />
        </div>
      </main>
    </>
  );
}

