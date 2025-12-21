import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import ClaimUpload from '@/components/ClaimUpload';
import ClaimList from '@/components/ClaimList';
import styles from '@/styles/Claims.module.css';

export default function ClaimsPage() {
  const { user } = useAuth();
  const [claims, setClaims] = useState<any[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchClaims = useCallback(async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/claims?limit=100`);
      const data = await response.json();
      setClaims(data.claims || []);
    } catch (error) {
      console.error('Error fetching claims:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const handleClaimAdded = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    fetchClaims();
  }, [fetchClaims]);

  return (
    <>
      <Head>
        <title>Claims Management | ClaimSphere AI</title>
        <meta name="description" content="Manage and process your claims" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <h1 className={styles.title}>
                <span>📋</span>
                Claims Management
              </h1>
              <p className={styles.subtitle}>
                Upload, track, and manage all your insurance claims
              </p>
            </div>
            <div className={styles.headerStats}>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{claims.length}</span>
                <span className={styles.statLabel}>Total Claims</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>
                  {claims.filter(c => c.status === 'pending').length}
                </span>
                <span className={styles.statLabel}>Pending</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>
                  {claims.filter(c => c.status === 'approved').length}
                </span>
                <span className={styles.statLabel}>Approved</span>
              </div>
            </div>
          </div>

          <div className={styles.grid}>
            {/* Upload Section */}
            <div className={styles.uploadSection}>
              <div className={styles.sectionCard}>
                <div className={styles.sectionHeader}>
                  <h2>
                    <span>📤</span>
                    Upload New Claim
                  </h2>
                </div>
                <div className={styles.sectionBody}>
                  <ClaimUpload onClaimAdded={handleClaimAdded} />
                </div>
              </div>
            </div>

            {/* Claims List Section */}
            <div className={styles.listSection}>
              <div className={styles.sectionCard}>
                <div className={styles.sectionHeader}>
                  <h2>
                    <span>📑</span>
                    All Claims
                  </h2>
                  <button 
                    className={styles.refreshBtn}
                    onClick={fetchClaims}
                    disabled={isLoading}
                  >
                    {isLoading ? '⟳ Loading...' : '⟳ Refresh'}
                  </button>
                </div>
                <div className={styles.sectionBody}>
                  <ClaimList 
                    claims={claims} 
                    refreshKey={refreshKey}
                    onRefresh={fetchClaims}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

