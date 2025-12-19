import { useState } from 'react';
import axios from 'axios';
import styles from './NaturalLanguageQuery.module.css';

interface NaturalLanguageQueryProps {
  claims: any[];
}

export default function NaturalLanguageQuery({ claims }: NaturalLanguageQueryProps) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exampleQueries = [
    "What's the total amount of pending claims?",
    "Show me all medical claims",
    "What's the average processing time?",
    "Which claim type has the highest amount?",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setAnswer('');

    try {
      const response = await axios.post('/api/claims/query', {
        query: query,
      });

      setAnswer(response.data.answer);
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
    <div className={styles.card}>
      <h2>💬 Ask Questions About Claims</h2>
      <p className={styles.subtitle}>
        Use natural language to query your claim data powered by ERNIE
      </p>

      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What's the total amount of pending claims?"
          className="input"
          disabled={loading || claims.length === 0}
        />
        <button
          type="submit"
          className="btn"
          disabled={loading || !query.trim() || claims.length === 0}
        >
          {loading ? 'Processing...' : 'Ask'}
        </button>
      </form>

      {claims.length === 0 && (
        <p className={styles.empty}>Upload some claims to ask questions!</p>
      )}

      <div className={styles.examples}>
        <p className={styles.examplesLabel}>Try these examples:</p>
        <div className={styles.exampleButtons}>
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              className={styles.exampleBtn}
              disabled={claims.length === 0}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {answer && (
        <div className={styles.answer}>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

