import { useTheme } from '@/contexts/ThemeContext';
import { useState, useEffect } from 'react';
import styles from './ThemeToggle.module.css';

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  
  // Always call hooks at the top level - React rules
  // ThemeProvider should always be available, but we handle gracefully
  const themeContext = useTheme();
  const { theme, toggleTheme } = themeContext;
  
  useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <button
        className={styles.themeToggle}
        aria-label="Toggle theme"
        title="Toggle theme"
        disabled
      >
        <span className={styles.icon}>🌙</span>
      </button>
    );
  }

  return (
    <button
      className={styles.themeToggle}
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <span className={styles.icon}>
        {theme === 'light' ? '🌙' : '☀️'}
      </span>
    </button>
  );
}
