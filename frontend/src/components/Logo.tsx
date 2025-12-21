import React from 'react';
import styles from './Logo.module.css';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  className?: string;
}

export default function Logo({ size = 'medium', showText = false, className = '' }: LogoProps) {
  const sizeMap = {
    small: 40,
    medium: 56,
    large: 80,
  };

  const logoSize = sizeMap[size];

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
          <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#166534" />
            <stop offset="50%" stopColor="#15803D" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>
        </defs>
        
        {/* Circular boundary with automation feel */}
        <circle
          cx="60"
          cy="60"
          r="55"
          fill="none"
          stroke="url(#logoGradient)"
          strokeWidth="2"
          strokeDasharray="3 3"
          opacity="0.5"
        />
        
        {/* AI Agent Head/Robot Head - Center */}
        <g transform="translate(60, 50)">
          {/* Main head shape */}
          <rect x="-18" y="-20" width="36" height="28" rx="4" fill="url(#logoGradient)" opacity="0.95" />
          <rect x="-16" y="-18" width="32" height="24" rx="3" fill="white" opacity="0.1" />
          
          {/* AI Eyes - representing intelligence */}
          <circle cx="-8" cy="-8" r="4" fill="white" />
          <circle cx="8" cy="-8" r="4" fill="white" />
          <circle cx="-8" cy="-8" r="2" fill="url(#logoGradient)" />
          <circle cx="8" cy="-8" r="2" fill="url(#logoGradient)" />
          
          {/* Processing indicator lines */}
          <line x1="-12" y1="2" x2="-6" y2="2" stroke="white" strokeWidth="1.5" opacity="0.8" />
          <line x1="6" y1="2" x2="12" y2="2" stroke="white" strokeWidth="1.5" opacity="0.8" />
        </g>
        
        {/* Documents/Claims being processed - around the agent */}
        <g transform="translate(30, 45)">
          <rect x="0" y="0" width="10" height="14" fill="url(#logoGradient)" opacity="0.7" rx="1" />
          <line x1="2" y1="2" x2="8" y2="2" stroke="white" strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="5" x2="7" y2="5" stroke="white" strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="8" x2="6" y2="8" stroke="white" strokeWidth="0.8" opacity="0.6" />
        </g>
        <g transform="translate(80, 45)">
          <rect x="0" y="0" width="10" height="14" fill="url(#logoGradient)" opacity="0.7" rx="1" />
          <line x1="2" y1="2" x2="8" y2="2" stroke="white" strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="5" x2="7" y2="5" stroke="white" strokeWidth="0.8" opacity="0.6" />
          <line x1="2" y1="8" x2="6" y2="8" stroke="white" strokeWidth="0.8" opacity="0.6" />
        </g>
        
        {/* Processing arrows - showing automation flow */}
        <g transform="translate(42, 52)">
          <path d="M 0 0 L 8 0 L 6 -2 M 8 0 L 6 2" stroke="url(#logoGradient)" strokeWidth="1.5" fill="none" opacity="0.8" />
        </g>
        <g transform="translate(70, 52)">
          <path d="M 0 0 L -8 0 L -6 -2 M -8 0 L -6 2" stroke="url(#logoGradient)" strokeWidth="1.5" fill="none" opacity="0.8" />
        </g>
        
        {/* Neural network nodes - representing AI processing */}
        <circle cx="25" cy="75" r="3" fill="url(#logoGradient)" opacity="0.6" />
        <circle cx="95" cy="75" r="3" fill="url(#logoGradient)" opacity="0.6" />
        <circle cx="40" cy="90" r="3" fill="url(#logoGradient)" opacity="0.6" />
        <circle cx="80" cy="90" r="3" fill="url(#logoGradient)" opacity="0.6" />
        
        {/* Connection lines between nodes */}
        <line x1="28" y1="75" x2="60" y2="60" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" />
        <line x1="92" y1="75" x2="60" y2="60" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" />
        <line x1="40" y1="90" x2="60" y2="70" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" />
        <line x1="80" y1="90" x2="60" y2="70" stroke="url(#logoGradient)" strokeWidth="1" opacity="0.3" />
        
        {/* Checkmark - representing validation/approval */}
        <g transform="translate(60, 85)">
          <circle cx="0" cy="0" r="8" fill="url(#logoGradient)" opacity="0.9" />
          <path d="M -3 -1 L -1 1 L 3 -3" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      </svg>
      {showText && (
        <span className={styles.logoText} style={{ fontSize: logoSize * 0.4 }}>
          AUTOMATED CLAIM PROCESSING AGENT
        </span>
      )}
    </div>
  );
}

