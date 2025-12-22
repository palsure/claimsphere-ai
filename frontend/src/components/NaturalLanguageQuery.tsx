import { useState } from 'react';
import { queryAPI } from '@/utils/api';
import styles from './NaturalLanguageQuery.module.css';

interface NaturalLanguageQueryProps {
  claims: any[];
}

interface QueryResponseData {
  answer?: string;
  message?: string;
  summary?: {
    total_claims?: number;
    total_amount?: number;
    pending_claims?: number;
    approved_claims?: number;
    denied_claims?: number;
    average_amount?: number;
  };
  claims?: Array<{
    id: string;
    claim_number: string;
    status: string;
    total_amount?: number;
    claimant_name?: string;
    category?: string;
  }>;
  metrics?: Array<{
    label: string;
    value: string | number;
    icon?: string;
  }>;
}

// Helper to format currency
const formatCurrency = (amount: number | string | undefined): string => {
  if (amount === undefined || amount === null) return '$0.00';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(num);
};

// Helper to format the answer text with nice styling
const formatAnswerText = (text: string): JSX.Element[] => {
  const lines = text.split('\n').filter(line => line.trim());
  const elements: JSX.Element[] = [];
  
  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    
    // Check for bullet points or numbered lists
    if (trimmedLine.match(/^[-•]\s/)) {
      elements.push(
        <div key={index} className={styles.bulletItem}>
          <span className={styles.bulletIcon}>•</span>
          <span>{trimmedLine.replace(/^[-•]\s/, '')}</span>
        </div>
      );
    }
    // Check for numbered lists
    else if (trimmedLine.match(/^\d+\.\s/)) {
      elements.push(
        <div key={index} className={styles.numberedItem}>
          <span className={styles.numberIcon}>{trimmedLine.match(/^\d+/)?.[0]}</span>
          <span>{trimmedLine.replace(/^\d+\.\s/, '')}</span>
        </div>
      );
    }
    // Check for key: value pairs
    else if (trimmedLine.includes(':') && !trimmedLine.includes('://')) {
      const [key, ...valueParts] = trimmedLine.split(':');
      const value = valueParts.join(':').trim();
      if (key.length < 40 && value) {
        elements.push(
          <div key={index} className={styles.keyValueItem}>
            <span className={styles.keyLabel}>{key}:</span>
            <span className={styles.valueLabel}>{highlightNumbers(value)}</span>
          </div>
        );
      } else {
        elements.push(
          <p key={index} className={styles.textParagraph}>
            {highlightNumbers(trimmedLine)}
          </p>
        );
      }
    }
    // Check for headers (lines ending with :)
    else if (trimmedLine.endsWith(':') && trimmedLine.length < 50) {
      elements.push(
        <h4 key={index} className={styles.sectionHeader}>
          {trimmedLine.replace(/:$/, '')}
        </h4>
      );
    }
    // Regular text
    else {
      elements.push(
        <p key={index} className={styles.textParagraph}>
          {highlightNumbers(trimmedLine)}
        </p>
      );
    }
  });
  
  return elements;
};

// Helper to highlight numbers and amounts in text
const highlightNumbers = (text: string): JSX.Element => {
  // Match currency amounts or plain numbers
  const parts = text.split(/(\$[\d,]+\.?\d*|\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?=\s|$|[,.](?!\d)))/g);
  
  return (
    <>
      {parts.map((part, i) => {
        if (part.match(/^\$[\d,]+\.?\d*$/) || part.match(/^\d{1,3}(?:,\d{3})*(?:\.\d{2})?$/)) {
          return <span key={i} className={styles.highlightNumber}>{part}</span>;
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
};

export default function NaturalLanguageQuery({ claims }: NaturalLanguageQueryProps) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [responseData, setResponseData] = useState<QueryResponseData | null>(null);
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
      const response = await queryAPI.ask(query);
      const newAnswer = response.answer || response.message || 'No response';
      setAnswer(newAnswer);
      setResponseData(response);
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
            <button 
              className={styles.clearBtn}
              onClick={() => { setAnswer(''); setResponseData(null); }}
              title="Clear response"
            >
              ✕
            </button>
          </div>
          
          {/* Summary Stats */}
          {responseData?.summary && (
            <div className={styles.summaryGrid}>
              {responseData.summary.total_claims !== undefined && (
                <div className={styles.summaryCard}>
                  <span className={styles.summaryIcon}>📊</span>
                  <span className={styles.summaryValue}>{responseData.summary.total_claims}</span>
                  <span className={styles.summaryLabel}>Total Claims</span>
                </div>
              )}
              {responseData.summary.total_amount !== undefined && (
                <div className={styles.summaryCard}>
                  <span className={styles.summaryIcon}>💰</span>
                  <span className={styles.summaryValue}>{formatCurrency(responseData.summary.total_amount)}</span>
                  <span className={styles.summaryLabel}>Total Amount</span>
                </div>
              )}
              {responseData.summary.pending_claims !== undefined && (
                <div className={styles.summaryCard}>
                  <span className={styles.summaryIcon}>⏳</span>
                  <span className={styles.summaryValue}>{responseData.summary.pending_claims}</span>
                  <span className={styles.summaryLabel}>Pending</span>
                </div>
              )}
              {responseData.summary.approved_claims !== undefined && (
                <div className={styles.summaryCard}>
                  <span className={styles.summaryIcon}>✅</span>
                  <span className={styles.summaryValue}>{responseData.summary.approved_claims}</span>
                  <span className={styles.summaryLabel}>Approved</span>
                </div>
              )}
              {responseData.summary.average_amount !== undefined && (
                <div className={styles.summaryCard}>
                  <span className={styles.summaryIcon}>📈</span>
                  <span className={styles.summaryValue}>{formatCurrency(responseData.summary.average_amount)}</span>
                  <span className={styles.summaryLabel}>Average</span>
                </div>
              )}
            </div>
          )}

          {/* Metrics */}
          {responseData?.metrics && responseData.metrics.length > 0 && (
            <div className={styles.metricsGrid}>
              {responseData.metrics.map((metric, idx) => (
                <div key={idx} className={styles.metricCard}>
                  <span className={styles.metricIcon}>{metric.icon || '📌'}</span>
                  <div className={styles.metricContent}>
                    <span className={styles.metricValue}>{metric.value}</span>
                    <span className={styles.metricLabel}>{metric.label}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Claims List */}
          {responseData?.claims && responseData.claims.length > 0 && (
            <div className={styles.claimsList}>
              <div className={styles.claimsListHeader}>
                <span>📋</span> Referenced Claims ({responseData.claims.length})
              </div>
              <div className={styles.claimsCards}>
                {responseData.claims.slice(0, 5).map((claim) => (
                  <div key={claim.id} className={styles.claimCard}>
                    <div className={styles.claimCardHeader}>
                      <span className={styles.claimNumber}>{claim.claim_number}</span>
                      <span className={`${styles.claimStatus} ${styles[claim.status?.toLowerCase() || 'pending']}`}>
                        {claim.status}
                      </span>
                    </div>
                    <div className={styles.claimCardBody}>
                      {claim.claimant_name && (
                        <div className={styles.claimDetail}>
                          <span>👤</span> {claim.claimant_name}
                        </div>
                      )}
                      {claim.category && (
                        <div className={styles.claimDetail}>
                          <span>🏷️</span> {claim.category}
                        </div>
                      )}
                      {claim.total_amount !== undefined && (
                        <div className={styles.claimDetail}>
                          <span>💵</span> {formatCurrency(claim.total_amount)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {responseData.claims.length > 5 && (
                  <div className={styles.moreClaimsNote}>
                    + {responseData.claims.length - 5} more claims
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Formatted Answer Text */}
          <div className={styles.answerContent}>
            {formatAnswerText(answer)}
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
