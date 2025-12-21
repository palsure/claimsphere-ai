import { useState } from 'react';
import axios from 'axios';
import { API_URL } from '@/config/api';
import styles from './NaturalLanguageQuery.module.css';

interface NaturalLanguageQueryProps {
  claims: any[];
}

export default function NaturalLanguageQuery({ claims }: NaturalLanguageQueryProps) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryHistory, setQueryHistory] = useState<{query: string, answer: string}[]>([]);

  const exampleQueries = [
    { icon: '💰', text: "What's the total amount of pending claims?" },
    { icon: '🏥', text: "Show me all medical claims" },
    { icon: '⏱️', text: "What's the average claim amount?" },
    { icon: '📊', text: "Which claim type has the highest amount?" },
    { icon: '✅', text: "How many claims are approved?" },
    { icon: '📈', text: "Give me a summary of all claims" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setAnswer('');

    try {
      const response = await axios.post(`${API_URL}/api/claims/query`, {
        query: query,
      });

      const newAnswer = response.data.answer;
      setAnswer(newAnswer);
      setQueryHistory(prev => [...prev.slice(-4), { query, answer: newAnswer }]);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error processing query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.aiIcon}>🤖</div>
        <div>
          <h3 className={styles.title}>AI Claims Assistant</h3>
          <p className={styles.subtitle}>Ask questions about your claims in natural language</p>
        </div>
      </div>

      {/* Query Input */}
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputWrapper}>
          <span className={styles.inputIcon}>💬</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={claims.length === 0 ? "Upload claims first..." : "Ask me anything about your claims..."}
            className={styles.input}
            disabled={loading || claims.length === 0}
          />
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading || !query.trim() || claims.length === 0}
          >
            {loading ? (
              <span className={styles.loadingSpinner}></span>
            ) : (
              <span>➤</span>
            )}
          </button>
        </div>
      </form>

      {/* Status Indicator */}
      <div className={styles.statusBar}>
        <span className={`${styles.statusDot} ${claims.length > 0 ? styles.active : ''}`}></span>
        <span className={styles.statusText}>
          {claims.length > 0 
            ? `${claims.length} claims available for analysis` 
            : 'No claims loaded - upload documents first'}
        </span>
      </div>

      {/* Example Queries */}
      {claims.length > 0 && (
        <div className={styles.examples}>
          <p className={styles.examplesLabel}>
            <span>✨</span> Quick queries
          </p>
          <div className={styles.exampleGrid}>
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example.text)}
                className={styles.exampleBtn}
                disabled={loading}
              >
                <span className={styles.exampleIcon}>{example.icon}</span>
                <span className={styles.exampleText}>{example.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className={styles.error}>
          <span>⚠️</span>
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className={styles.loadingState}>
          <div className={styles.loadingAnimation}>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <p>Analyzing your claims data...</p>
        </div>
      )}

      {/* Answer */}
      {answer && !loading && (
        <div className={styles.answer}>
          <div className={styles.answerHeader}>
            <span className={styles.answerIcon}>🤖</span>
            <span>AI Response</span>
          </div>
          <div className={styles.answerContent}>
            {answer}
          </div>
        </div>
      )}

      {/* Query History */}
      {queryHistory.length > 0 && !loading && !answer && (
        <div className={styles.history}>
          <p className={styles.historyLabel}>
            <span>🕐</span> Recent queries
          </p>
          <div className={styles.historyList}>
            {queryHistory.slice().reverse().map((item, index) => (
              <button
                key={index}
                className={styles.historyItem}
                onClick={() => setQuery(item.query)}
              >
                <span className={styles.historyQuery}>{item.query}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {claims.length === 0 && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📄</div>
          <h4>No Claims Yet</h4>
          <p>Upload claim documents to start asking questions about your data</p>
        </div>
      )}
    </div>
  );
}
