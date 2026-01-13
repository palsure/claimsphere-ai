import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import styles from './Logo.module.css';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  className?: string;
}

export default function Logo({ size = 'medium', showText = false, className = '' }: LogoProps) {
  const { theme } = useTheme();
  const sizeMap = {
    small: 56,    // Increased from 40
    medium: 72,   // Increased from 56
    large: 96,    // Increased from 80
  };

  const logoSize = sizeMap[size];
  const isDark = theme === 'dark';

  // Theme-aware colors
  const primaryColor = isDark ? '#60a5fa' : '#1e40af';
  const secondaryColor = isDark ? '#38bdf8' : '#3b82f6';
  const tertiaryColor = isDark ? '#22d3ee' : '#0ea5e9';
  const glowColor = isDark ? 'rgba(96, 165, 250, 0.4)' : 'rgba(30, 64, 175, 0.3)';

  return (
    <div className={`${styles.logoContainer} ${className}`}>
      <svg
        width={logoSize}
        height={logoSize}
        viewBox="0 0 120 120"
        className={styles.logo}
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Main gradient */}
          <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={primaryColor} />
            <stop offset="50%" stopColor={secondaryColor} />
            <stop offset="100%" stopColor={tertiaryColor} />
          </linearGradient>
          
          {/* Glow filter for animations */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          {/* Pulsing glow filter */}
          <filter id="pulseGlow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Animated outer ring - rotating */}
        <circle
          cx="60"
          cy="60"
          r="55"
          fill="none"
          stroke="url(#logoGradient)"
          strokeWidth="2"
          strokeDasharray="3 3"
          opacity="0.5"
          className={styles.rotatingRing}
        />
        
        {/* Pulsing glow circle */}
        <circle
          cx="60"
          cy="60"
          r="50"
          fill="none"
          stroke={glowColor}
          strokeWidth="1"
          opacity="0.6"
          className={styles.pulsingGlow}
        />
        
        {/* AI Agent Head/Robot Head - Center with glow */}
        <g transform="translate(60, 50)" className={styles.agentHead}>
          {/* Main head shape */}
          <rect x="-18" y="-20" width="36" height="28" rx="4" fill="url(#logoGradient)" opacity="0.95" filter="url(#glow)" />
          <rect x="-16" y="-18" width="32" height="24" rx="3" fill={isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.2)'} />
          
          {/* AI Eyes - pulsing animation */}
          <g className={styles.eyes}>
            <circle cx="-8" cy="-8" r="4" fill={isDark ? '#e2e8f0' : 'white'} />
            <circle cx="8" cy="-8" r="4" fill={isDark ? '#e2e8f0' : 'white'} />
            <circle cx="-8" cy="-8" r="2" fill="url(#logoGradient)" className={styles.eyePulse} />
            <circle cx="8" cy="-8" r="2" fill="url(#logoGradient)" className={styles.eyePulse} style={{ animationDelay: '0.5s' }} />
          </g>
          
          {/* Processing indicator lines - animated */}
          <g className={styles.processingLines}>
            <line x1="-12" y1="2" x2="-6" y2="2" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="1.5" opacity="0.8" className={styles.linePulse} />
            <line x1="6" y1="2" x2="12" y2="2" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="1.5" opacity="0.8" className={styles.linePulse} style={{ animationDelay: '0.3s' }} />
          </g>
        </g>
        
        {/* Documents/Claims being processed - floating animation */}
        <g transform="translate(30, 45)" className={styles.documentLeft}>
          <rect x="0" y="0" width="10" height="14" fill="url(#logoGradient)" opacity="0.7" rx="1" />
          <line x1="2" y1="2" x2="8" y2="2" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="5" x2="7" y2="5" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="8" x2="6" y2="8" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
        </g>
        <g transform="translate(80, 45)" className={styles.documentRight}>
          <rect x="0" y="0" width="10" height="14" fill="url(#logoGradient)" opacity="0.7" rx="1" />
          <line x1="2" y1="2" x2="8" y2="2" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="5" x2="7" y2="5" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="8" x2="6" y2="8" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="0.8" opacity="0.6" />
        </g>
        
        {/* Processing arrows - animated flow */}
        <g transform="translate(42, 52)" className={styles.arrowLeft}>
          <path d="M 0 0 L 8 0 L 6 -2 M 8 0 L 6 2" stroke="url(#logoGradient)" strokeWidth="1.5" fill="none" opacity="0.8" className={styles.arrowFlow} />
        </g>
        <g transform="translate(70, 52)" className={styles.arrowRight}>
          <path d="M 0 0 L -8 0 L -6 -2 M -8 0 L -6 2" stroke="url(#logoGradient)" strokeWidth="1.5" fill="none" opacity="0.8" className={styles.arrowFlow} style={{ animationDelay: '0.5s' }} />
        </g>
        
        {/* Neural network nodes - pulsing animation */}
        <circle cx="25" cy="75" r="3" fill="url(#logoGradient)" opacity="0.6" className={styles.nodePulse} />
        <circle cx="95" cy="75" r="3" fill="url(#logoGradient)" opacity="0.6" className={styles.nodePulse} style={{ animationDelay: '0.2s' }} />
        <circle cx="40" cy="90" r="3" fill="url(#logoGradient)" opacity="0.6" className={styles.nodePulse} style={{ animationDelay: '0.4s' }} />
        <circle cx="80" cy="90" r="3" fill="url(#logoGradient)" opacity="0.6" className={styles.nodePulse} style={{ animationDelay: '0.6s' }} />
        
        {/* Connection lines between nodes - animated */}
        <line x1="28" y1="75" x2="60" y2="60" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" className={styles.connectionLine} />
        <line x1="92" y1="75" x2="60" y2="60" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" className={styles.connectionLine} style={{ animationDelay: '0.2s' }} />
        <line x1="40" y1="90" x2="60" y2="70" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" className={styles.connectionLine} style={{ animationDelay: '0.4s' }} />
        <line x1="80" y1="90" x2="60" y2="70" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" className={styles.connectionLine} style={{ animationDelay: '0.6s' }} />
        
        {/* Checkmark - representing validation/approval with pulse */}
        <g transform="translate(60, 85)" className={styles.checkmark}>
          <circle cx="0" cy="0" r="8" fill="url(#logoGradient)" opacity="0.9" filter="url(#pulseGlow)" className={styles.checkPulse} />
          <path d="M -3 -1 L -1 1 L 3 -3" stroke={isDark ? '#e2e8f0' : 'white'} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      </svg>
      {showText && (
        <span className={styles.logoText} style={{ fontSize: logoSize * 0.4 }}>
          ClaimSphere AI
        </span>
      )}
    </div>
  );
}

