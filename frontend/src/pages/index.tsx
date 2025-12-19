import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import ClaimUpload from '@/components/ClaimUpload';
import ClaimList from '@/components/ClaimList';
import ClaimAnalytics from '@/components/ClaimAnalytics';
import NaturalLanguageQuery from '@/components/NaturalLanguageQuery';
import styles from '@/styles/Home.module.css';

export default function Home() {
  const [claims, setClaims] = useState<any[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchClaims = useCallback(async () => {
    try {
      const response = await fetch('/api/claims?limit=100');
      const data = await response.json();
      setClaims(data.claims || []);
    } catch (error) {
      console.error('Error fetching claims:', error);
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
        <title>Automated Claim Processing Agent</title>
        <meta name="description" content="AI-powered automated claim processing system" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>
            🏥 Automated Claim Processing Agent
          </h1>
          <p className={styles.subtitle}>
            AI-powered claim processing using PaddleOCR and ERNIE
          </p>
        </div>

        <div className={styles.container}>
          <div className={styles.section}>
            <ClaimUpload onClaimAdded={handleClaimAdded} />
          </div>

          <div className={styles.section}>
            <NaturalLanguageQuery claims={claims} />
          </div>

          <div className={styles.section}>
            <ClaimAnalytics claims={claims} refreshKey={refreshKey} />
          </div>

          <div className={styles.section}>
            <ClaimList 
              claims={claims} 
              refreshKey={refreshKey}
              onRefresh={fetchClaims}
            />
          </div>
        </div>
      </main>
    </>
  );
}
