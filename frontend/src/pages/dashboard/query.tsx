/**
 * Natural Language Query Page
 */
import { useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { queryAPI } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';
import styles from '../../styles/Query.module.css';

interface QueryResult {
  query: string;
  answer: string;
  claims_analyzed: number;
  cited_claims: string[];
  fields_used: string[];
}

export default function QueryPage() {
  const { hasRole } = useAuth();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [history, setHistory] = useState<QueryResult[]>([]);
  const [error, setError] = useState('');

  const exampleQueries = hasRole('admin') ? [
    "What's the total amount of all pending claims?",
    "How many claims were approved this month?",
    "Which category has the highest claim amounts?",
    "What's the average processing time for claims?",
    "Show me claims with amounts over $1000",
  ] : hasRole('agent') ? [
    "How many claims are in my queue?",
    "What's the total value of pending claims?",
    "Show me high-value claims pending review",
    "Which claims have been waiting the longest?",
  ] : [
    "What's the status of my latest claim?",
    "How much have I claimed this year?",
    "Which of my claims are still pending?",
    "Show me my approved claims",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await queryAPI.ask(query);
      setResult(response);
      setHistory([response, ...history.slice(0, 4)]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  return (
    <DashboardLayout title="Ask AI">
      <div className={styles.container}>
        {/* Info Banner */}
        <div className={styles.infoBanner}>
          <span className={styles.infoIcon}>🤖</span>
          <div className={styles.infoContent}>
            <h3>AI-Powered Claims Assistant</h3>
            <p>
              Ask questions about your claims in natural language. 
              {hasRole('admin') 
                ? ' As an admin, you can query all claims in the system.'
                : hasRole('agent')
                ? ' As an agent, you can query claims in your queue or pending review.'
                : ' You can only query your own claims.'}
            </p>
          </div>
        </div>

        {/* Query Form */}
        <form onSubmit={handleSubmit} className={styles.queryForm}>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about claims..."
              className={styles.queryInput}
              disabled={loading}
            />
            <button
              type="submit"
              className={styles.submitButton}
              disabled={loading || !query.trim()}
            >
              {loading ? '...' : '→'}
            </button>
          </div>
        </form>

        {/* Example Queries */}
        <div className={styles.examples}>
          <span className={styles.examplesLabel}>Try asking:</span>
          <div className={styles.examplesList}>
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className={styles.exampleButton}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className={styles.resultCard}>
            <div className={styles.resultHeader}>
              <span className={styles.resultIcon}>💬</span>
              <span className={styles.resultQuery}>{result.query}</span>
            </div>
            
            <div className={styles.resultAnswer}>
              {result.answer}
            </div>
            
            <div className={styles.resultMeta}>
              <span className={styles.metaItem}>
                📊 Analyzed {result.claims_analyzed} claims
              </span>
              {result.cited_claims.length > 0 && (
                <span className={styles.metaItem}>
                  📋 References: {result.cited_claims.join(', ')}
                </span>
              )}
              {result.fields_used.length > 0 && (
                <span className={styles.metaItem}>
                  🔍 Fields: {result.fields_used.join(', ')}
                </span>
              )}
            </div>
          </div>
        )}

        {/* History */}
        {history.length > 1 && (
          <div className={styles.historySection}>
            <h3>Recent Questions</h3>
            <div className={styles.historyList}>
              {history.slice(1).map((item, index) => (
                <div key={index} className={styles.historyItem}>
                  <span className={styles.historyQuery}>{item.query}</span>
                  <span className={styles.historyAnswer}>
                    {item.answer.slice(0, 100)}...
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

