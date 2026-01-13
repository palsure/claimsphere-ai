/**
 * AI Assistant Page
 */
import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { queryAPI } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import styles from '../styles/Query.module.css';

interface QueryResult {
  query: string;
  answer: string;
  claims_analyzed: number;
  cited_claims: string[];
  fields_used: string[];
  reasoning?: string | null;
}

export default function AIAssistantPage() {
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

    const currentQuery = query;
    setQuery(''); // Clear input immediately
    setLoading(true);
    setError('');

    try {
      const response = await queryAPI.ask(currentQuery);
      // Add to history with latest at the top
      const newHistoryItem = { ...response, query: currentQuery };
      setHistory([newHistoryItem, ...history]);
      setResult(newHistoryItem);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = async (example: string) => {
    setQuery(''); // Clear input
    setLoading(true);
    setError('');

    try {
      const response = await queryAPI.ask(example);
      // Add to history with latest at the top
      const newHistoryItem = { ...response, query: example };
      setHistory([newHistoryItem, ...history]);
      setResult(newHistoryItem);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className={styles.container}>
        {/* Info Banner */}
        <div className={styles.infoBanner}>
          <span className={styles.infoIcon}>💬</span>
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
                disabled={loading}
                type="button"
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

        {/* Chat Messages - Latest at top */}
        {history.length > 0 && (
          <div className={styles.chatContainer}>
            {history.map((item, index) => (
              <div key={index} className={styles.chatMessage}>
                {/* User Question */}
                <div className={styles.userMessage}>
                  <div className={styles.messageHeader}>
                    <span className={styles.userIcon}>👤</span>
                    <span className={styles.messageLabel}>You</span>
                  </div>
                  <div className={styles.messageContent}>
                    {item.query}
                  </div>
                </div>

                {/* AI Answer */}
                <div className={styles.aiMessage}>
                  <div className={styles.messageHeader}>
                    <span className={styles.aiIcon}>🤖</span>
                    <span className={styles.messageLabel}>AI Assistant</span>
                  </div>
                  <div className={styles.messageContent}>
                    <div className={styles.answerText}>
                      {item.answer.split('\n').map((line, lineIdx) => {
                        const trimmedLine = line.trim();
                        // Format bullet points
                        if (trimmedLine.match(/^[-•]\s/)) {
                          return (
                            <div key={lineIdx} className={styles.bulletLine}>
                              <span className={styles.bullet}>•</span>
                              <span>{trimmedLine.replace(/^[-•]\s/, '')}</span>
                            </div>
                          );
                        }
                        // Format key: value pairs
                        if (trimmedLine.includes(':') && !trimmedLine.includes('://') && trimmedLine.length < 100) {
                          const [key, ...valueParts] = trimmedLine.split(':');
                          const value = valueParts.join(':').trim();
                          return (
                            <div key={lineIdx} className={styles.keyValueLine}>
                              <span className={styles.key}>{key}:</span>
                              <span className={styles.value}>{value}</span>
                            </div>
                          );
                        }
                        // Regular text
                        if (trimmedLine) {
                          return (
                            <p key={lineIdx} className={styles.textLine}>
                              {trimmedLine}
                            </p>
                          );
                        }
                        return null;
                      })}
                    </div>
                    
                    {/* Cited Claims */}
                    {item.cited_claims && item.cited_claims.length > 0 && (
                      <div className={styles.citedSection}>
                        <div className={styles.citedHeader}>
                          <span className={styles.citedIcon}>📋</span>
                          <span className={styles.citedTitle}>Cited Claims ({item.cited_claims.length}):</span>
                        </div>
                        <div className={styles.citedList}>
                          {item.cited_claims.map((claim, idx) => {
                            // Clean up quoted strings (remove extra quotes)
                            const cleanClaim = claim.replace(/^["']|["']$/g, '').trim();
                            return (
                              <span key={idx} className={styles.citedItem}>
                                {cleanClaim}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Fields Used */}
                    {item.fields_used && item.fields_used.length > 0 && (
                      <div className={styles.citedSection}>
                        <div className={styles.citedHeader}>
                          <span className={styles.citedIcon}>🔍</span>
                          <span className={styles.citedTitle}>Fields Used ({item.fields_used.length}):</span>
                        </div>
                        <div className={styles.citedList}>
                          {item.fields_used.map((field, idx) => {
                            // Clean up quoted strings (remove extra quotes)
                            const cleanField = field.replace(/^["']|["']$/g, '').trim();
                            return (
                              <span key={idx} className={styles.citedItem}>
                                {cleanField}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Reasoning (if available and not already in answer) */}
                    {item.reasoning && item.reasoning.trim() && !item.answer.includes(item.reasoning) && (
                      <div className={styles.citedSection}>
                        <div className={styles.citedHeader}>
                          <span className={styles.citedIcon}>💭</span>
                          <span className={styles.citedTitle}>Analysis & Reasoning:</span>
                        </div>
                        <div className={styles.reasoningText}>
                          {item.reasoning.split('\n').map((line, idx) => (
                            <p key={idx} className={styles.reasoningLine}>
                              {line.trim()}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className={styles.messageMeta}>
                      <span className={styles.metaItem}>
                        📊 Analyzed {item.claims_analyzed} claims
                      </span>
                      {item.cited_claims && item.cited_claims.length > 0 && (
                        <span className={styles.metaItem}>
                          📋 {item.cited_claims.length} reference{item.cited_claims.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className={styles.loadingState}>
            <div className={styles.loadingSpinner}></div>
            <p>Processing your query...</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
