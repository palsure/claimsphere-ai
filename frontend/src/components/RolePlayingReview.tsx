import { useState, useEffect } from 'react';
import styles from './RolePlayingReview.module.css';

interface RolePlayingReviewProps {
  review: {
    review?: {
      overall_assessment?: string;
      confidence_level?: number;
      key_findings?: (string | { observation?: string; evidence?: string; [key: string]: any })[];
      concerns?: (string | { concern?: string; text?: string; [key: string]: any })[];
      recommendations?: (string | { recommendation?: string; text?: string; [key: string]: any })[];
      reasoning?: string | Record<string, any>;
      observation?: string;
      evidence?: string;
    };
    decision?: {
      decision?: string;
      approved_amount?: number;
      confidence?: number;
      reasoning?: string;
      policy_references?: (string | { policy?: string; reference?: string; text?: string; [key: string]: any })[];
      conditions?: (string | { condition?: string; text?: string; [key: string]: any })[];
    };
    discussion?: {
      turns?: number;
      log?: Array<{
        turn: number;
        speaker: string;
        message: string;
      }>;
    };
    reasoning_traces?: Record<string, string>;
  };
  onClose?: () => void;
  onApprove?: (approvedAmount?: number) => void;
  onDeny?: () => void;
  onRequestInfo?: () => void;
  claimId?: string;
}

export default function RolePlayingReview({ review, onClose, onApprove, onDeny, onRequestInfo, claimId }: RolePlayingReviewProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['review', 'decision']));
  const [isProcessing, setIsProcessing] = useState(false);
  
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };
  
  // Parse review data and handle nested JSON strings
  let reviewData = review.review || {};
  
  // If reasoning is a JSON string, parse it and merge with review data
  if (typeof reviewData.reasoning === 'string') {
    try {
      const parsedReasoning = JSON.parse(reviewData.reasoning);
      // If parsed reasoning contains the actual review data, merge it
      if (parsedReasoning.overall_assessment || parsedReasoning.key_findings) {
        reviewData = {
          ...reviewData,
          // Merge parsed reasoning data, prioritizing parsed data
          overall_assessment: parsedReasoning.overall_assessment || reviewData.overall_assessment,
          confidence_level: parsedReasoning.confidence_level ?? reviewData.confidence_level,
          key_findings: parsedReasoning.key_findings || reviewData.key_findings,
          concerns: parsedReasoning.concerns || reviewData.concerns,
          recommendations: parsedReasoning.recommendations || reviewData.recommendations,
          reasoning: parsedReasoning // Keep the parsed reasoning for detailed view
        };
      } else {
        // Otherwise, just parse the reasoning field
        reviewData.reasoning = parsedReasoning;
      }
    } catch (e) {
      // If parsing fails, keep as string
      console.warn('Could not parse reasoning JSON:', e);
    }
  }
  
  const decisionData = review.decision || {};
  const discussion = review.discussion;
  const reasoningTraces = review.reasoning_traces || {};
  
  const getDecisionColor = (decision?: string) => {
    switch (decision?.toLowerCase()) {
      case 'approve':
        return styles.approve;
      case 'deny':
        return styles.deny;
      case 'pend':
        return styles.pend;
      default:
        return '';
    }
  };
  
  const getAssessmentColor = (assessment?: string) => {
    switch (assessment?.toLowerCase()) {
      case 'approve':
        return styles.approve;
      case 'deny':
        return styles.deny;
      case 'pend':
      case 'needs_more_info':
        return styles.pend;
      default:
        return '';
    }
  };
  
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>🤖 AI Agent Review</h3>
        <p className={styles.subtitle}>Review and decision by CAMEL-AI role-playing agents</p>
        {onClose && (
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        )}
      </div>
      
      {/* Review Section */}
      {reviewData && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('review')}
          >
            <h4>
              <span className={styles.icon}>
                {expandedSections.has('review') ? '▼' : '▶'}
              </span>
              📋 Review Assessment
            </h4>
            {reviewData.overall_assessment && (
              <span className={`${styles.badge} ${getAssessmentColor(reviewData.overall_assessment)}`}>
                {reviewData.overall_assessment.toUpperCase().replace(/_/g, ' ')}
              </span>
            )}
          </div>
          
          {expandedSections.has('review') && (
            <div className={styles.sectionContent}>
              {/* Summary Card - Quick Overview */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px',
                marginBottom: '20px'
              }}>
                {reviewData.confidence_level !== undefined && (
                  <div style={{
                    padding: '12px',
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))',
                    borderRadius: '8px',
                    border: '1px solid rgba(59, 130, 246, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Confidence</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-primary)' }}>
                      {(reviewData.confidence_level * 100).toFixed(0)}%
                    </div>
                    <div className={styles.confidenceBar} style={{ height: '4px', borderRadius: '2px', marginTop: '8px', background: 'rgba(59, 130, 246, 0.2)' }}>
                      <div 
                        className={styles.confidenceFill}
                        style={{ 
                          width: `${reviewData.confidence_level * 100}%`,
                          height: '100%',
                          borderRadius: '2px',
                          background: 'var(--accent-primary)',
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>
                )}
                
                {reviewData.overall_assessment && (
                  <div style={{
                    padding: '12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Assessment</div>
                    <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {reviewData.overall_assessment.toUpperCase().replace(/_/g, ' ')}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Show observation and evidence if available - Compact */}
              {((reviewData as any).observation || (reviewData as any).evidence) && (
                <div style={{ 
                  marginBottom: '16px', 
                  padding: '12px', 
                  background: 'var(--bg-elevated)', 
                  borderRadius: '8px', 
                  border: '1px solid var(--border-color)',
                  fontSize: '0.9rem',
                  lineHeight: '1.5'
                }}>
                  {(reviewData as any).observation && (
                    <div style={{ marginBottom: (reviewData as any).evidence ? '8px' : '0' }}>
                      <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>📝 </span>
                      <span style={{ color: 'var(--text-secondary)' }}>{(reviewData as any).observation}</span>
                    </div>
                  )}
                  {(reviewData as any).evidence && (
                    <div>
                      <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>🔍 </span>
                      <span style={{ color: 'var(--text-secondary)' }}>{(reviewData as any).evidence}</span>
                    </div>
                  )}
                </div>
              )}
              
              {reviewData.key_findings && reviewData.key_findings.length > 0 && (
                <div className={styles.findings} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '10px', 
                    color: 'var(--text-primary)',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span>🔍</span>
                    <span>Key Findings</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: '400', color: 'var(--text-secondary)' }}>({reviewData.key_findings.length})</span>
                  </h5>
                  <div style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {reviewData.key_findings.map((finding, idx) => {
                      const isObjectWithObservation = typeof finding === 'object' && finding !== null && 'observation' in finding;
                      const findingObj = finding as any;
                      const findingText = isObjectWithObservation ? findingObj.observation : String(finding);
                      // Truncate long findings
                      const maxLength = 150;
                      const displayText = findingText.length > maxLength 
                        ? findingText.substring(0, maxLength) + '...' 
                        : findingText;
                      
                      return (
                        <div key={idx} style={{
                          padding: '10px 12px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.9rem',
                          lineHeight: '1.5',
                          color: 'var(--text-primary)'
                        }}>
                          <span style={{ color: 'var(--accent-primary)', marginRight: '6px' }}>•</span>
                          {displayText}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {reviewData.concerns && reviewData.concerns.length > 0 && (
                <div className={styles.concerns} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '10px', 
                    color: 'var(--warning)',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span>⚠️</span>
                    <span>Concerns</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: '400', color: 'var(--text-secondary)' }}>({reviewData.concerns.length})</span>
                  </h5>
                  <div style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {reviewData.concerns.map((concern, idx) => {
                      const concernText = typeof concern === 'object' && concern !== null 
                        ? (concern.concern || concern.text || JSON.stringify(concern))
                        : String(concern);
                      // Truncate long concerns
                      const maxLength = 120;
                      const displayText = concernText.length > maxLength 
                        ? concernText.substring(0, maxLength) + '...' 
                        : concernText;
                      
                      return (
                        <div key={idx} style={{
                          padding: '10px 12px',
                          background: 'rgba(251, 191, 36, 0.1)',
                          borderRadius: '6px',
                          border: '1px solid rgba(251, 191, 36, 0.3)',
                          fontSize: '0.9rem',
                          lineHeight: '1.5',
                          color: 'var(--text-primary)'
                        }}>
                          <span style={{ color: 'var(--warning)', marginRight: '6px' }}>⚠</span>
                          {displayText}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {reviewData.recommendations && reviewData.recommendations.length > 0 && (
                <div className={styles.recommendations} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '10px', 
                    color: 'var(--info, #3b82f6)',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span>💡</span>
                    <span>Recommendations</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: '400', color: 'var(--text-secondary)' }}>({reviewData.recommendations.length})</span>
                  </h5>
                  <div style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {reviewData.recommendations.map((rec, idx) => {
                      const recText = typeof rec === 'object' && rec !== null 
                        ? (rec.recommendation || rec.text || JSON.stringify(rec))
                        : String(rec);
                      // Truncate long recommendations
                      const maxLength = 120;
                      const displayText = recText.length > maxLength 
                        ? recText.substring(0, maxLength) + '...' 
                        : recText;
                      
                      return (
                        <div key={idx} style={{
                          padding: '10px 12px',
                          background: 'rgba(56, 189, 248, 0.1)',
                          borderRadius: '6px',
                          border: '1px solid rgba(56, 189, 248, 0.3)',
                          fontSize: '0.9rem',
                          lineHeight: '1.5',
                          color: 'var(--text-primary)'
                        }}>
                          <span style={{ color: 'var(--info, #3b82f6)', marginRight: '6px' }}>💡</span>
                          {displayText}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {/* Hide raw JSON reasoning - only show if it contains unique info not already displayed */}
              {reviewData.reasoning && typeof reviewData.reasoning === 'object' && 
               Object.keys(reviewData.reasoning).some(key => 
                 !['overall_assessment', 'confidence_level', 'key_findings', 'concerns', 'recommendations'].includes(key)
               ) && (
                <details style={{ marginTop: '12px' }}>
                  <summary style={{ 
                    cursor: 'pointer', 
                    color: 'var(--text-secondary)', 
                    fontSize: '0.85rem',
                    fontWeight: '500',
                    padding: '8px',
                    borderRadius: '4px',
                    background: 'var(--bg-elevated)'
                  }}>
                    🔍 View Detailed Reasoning
                  </summary>
                  <div style={{
                    marginTop: '8px',
                    padding: '12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.85rem',
                    lineHeight: '1.6',
                    maxHeight: '300px',
                    overflowY: 'auto'
                  }}>
                    <pre style={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      margin: 0,
                      fontFamily: 'inherit'
                    }}>
                      {JSON.stringify(reviewData.reasoning, null, 2)}
                    </pre>
                  </div>
                </details>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Discussion Section */}
      {discussion && discussion.log && discussion.log.length > 0 && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('discussion')}
          >
            <h4>
              <span className={styles.icon}>
                {expandedSections.has('discussion') ? '▼' : '▶'}
              </span>
              💬 Agent Discussion ({discussion.turns || discussion.log.length} turns)
            </h4>
          </div>
          
          {expandedSections.has('discussion') && (
            <div className={styles.sectionContent}>
              <div className={styles.discussionLog}>
                {discussion.log.map((turn, idx) => (
                  <div key={idx} className={styles.discussionTurn}>
                    <div className={styles.discussionSpeaker}>
                      {turn.speaker === 'Reviewer' ? '👤' : '✅'} {turn.speaker}
                    </div>
                    <div className={styles.discussionMessage}>
                      {turn.message}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Decision Section */}
      {decisionData && decisionData.decision && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('decision')}
          >
            <h4>
              <span className={styles.icon}>
                {expandedSections.has('decision') ? '▼' : '▶'}
              </span>
              ✅ Final Decision
            </h4>
            <span className={`${styles.badge} ${getDecisionColor(decisionData.decision)}`}>
              {decisionData.decision.toUpperCase()}
            </span>
          </div>
          
          {expandedSections.has('decision') && (
            <div className={styles.sectionContent}>
              {/* Summary Cards for Decision */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '12px',
                marginBottom: '16px'
              }}>
                {decisionData.confidence !== undefined && (
                  <div style={{
                    padding: '12px',
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))',
                    borderRadius: '8px',
                    border: '1px solid rgba(59, 130, 246, 0.2)'
                  }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Confidence</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-primary)' }}>
                      {(decisionData.confidence * 100).toFixed(0)}%
                    </div>
                    <div className={styles.confidenceBar} style={{ height: '4px', borderRadius: '2px', marginTop: '8px', background: 'rgba(59, 130, 246, 0.2)' }}>
                      <div 
                        className={styles.confidenceFill}
                        style={{ 
                          width: `${decisionData.confidence * 100}%`,
                          height: '100%',
                          borderRadius: '2px',
                          background: 'var(--accent-primary)',
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>
                )}
                
                {decisionData.approved_amount !== undefined && decisionData.approved_amount !== null && (
                  <div style={{
                    padding: '12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Approved Amount</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--success, #10b981)' }}>
                      ${decisionData.approved_amount.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
              
              {decisionData.reasoning && (
                <div className={styles.reasoning} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '8px', 
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    color: 'var(--text-primary)'
                  }}>
                    💭 Decision Reasoning
                  </h5>
                  <p style={{ 
                    fontSize: '0.9rem',
                    lineHeight: '1.6',
                    color: 'var(--text-secondary)',
                    padding: '10px 12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color)',
                    margin: 0
                  }}>
                    {decisionData.reasoning.length > 200 
                      ? decisionData.reasoning.substring(0, 200) + '...' 
                      : decisionData.reasoning}
                  </p>
                </div>
              )}
              
              {decisionData.policy_references && decisionData.policy_references.length > 0 && (
                <div className={styles.policies} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '10px', 
                    color: 'var(--text-primary)',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span>📋</span>
                    <span>Policy References</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: '400', color: 'var(--text-secondary)' }}>({decisionData.policy_references.length})</span>
                  </h5>
                  <div style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}>
                    {decisionData.policy_references.map((policy, idx) => {
                      const isObjectWithProperties = typeof policy === 'object' && policy !== null && ('policy' in policy || 'reference' in policy || 'text' in policy);
                      const policyObj = policy as any;
                      const policyText = isObjectWithProperties 
                        ? (policyObj.policy || policyObj.reference || policyObj.text || JSON.stringify(policyObj))
                        : String(policy);
                      // Truncate long policy text
                      const maxLength = 100;
                      const displayText = policyText.length > maxLength 
                        ? policyText.substring(0, maxLength) + '...' 
                        : policyText;
                      
                      return (
                        <div key={idx} style={{
                          padding: '8px 10px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.85rem',
                          lineHeight: '1.4',
                          color: 'var(--text-primary)'
                        }}>
                          <span style={{ color: 'var(--accent-primary)', marginRight: '6px' }}>📄</span>
                          {displayText}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {decisionData.conditions && decisionData.conditions.length > 0 && (
                <div className={styles.conditions} style={{ marginBottom: '16px' }}>
                  <h5 style={{ 
                    marginBottom: '10px', 
                    color: 'var(--text-primary)',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span>📝</span>
                    <span>Conditions</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: '400', color: 'var(--text-secondary)' }}>({decisionData.conditions.length})</span>
                  </h5>
                  <div style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}>
                    {decisionData.conditions.map((condition, idx) => {
                      const isObjectWithProperties = typeof condition === 'object' && condition !== null && ('condition' in condition || 'text' in condition);
                      const conditionObj = condition as any;
                      const conditionText = isObjectWithProperties 
                        ? (conditionObj.condition || conditionObj.text || JSON.stringify(conditionObj))
                        : String(condition);
                      // Truncate long conditions
                      const maxLength = 100;
                      const displayText = conditionText.length > maxLength 
                        ? conditionText.substring(0, maxLength) + '...' 
                        : conditionText;
                      
                      return (
                        <div key={idx} style={{
                          padding: '8px 10px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.85rem',
                          lineHeight: '1.4',
                          color: 'var(--text-primary)',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '8px'
                        }}>
                          <span style={{ color: 'var(--accent-primary)', flexShrink: 0 }}>✓</span>
                          <span>{displayText}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Reasoning Traces */}
      {Object.keys(reasoningTraces).length > 0 && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('reasoning')}
          >
            <h4>
              <span className={styles.icon}>
                {expandedSections.has('reasoning') ? '▼' : '▶'}
              </span>
              🧠 Reasoning Traces
            </h4>
          </div>
          
          {expandedSections.has('reasoning') && (
            <div className={styles.sectionContent}>
              {Object.entries(reasoningTraces).map(([step, reasoning]) => (
                <div key={step} className={styles.reasoningTrace}>
                  <h5>{step.charAt(0).toUpperCase() + step.slice(1)} Agent Reasoning</h5>
                  <p>{reasoning}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Action Buttons - Show after AI review */}
      {(onApprove || onDeny || onRequestInfo) && (reviewData || decisionData) && (
        <div style={{
          marginTop: '24px',
          padding: '20px',
          background: 'var(--bg-elevated)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)'
        }}>
          <h4 style={{ 
            marginBottom: '16px', 
            fontSize: '1.1rem', 
            fontWeight: '600',
            color: 'var(--text-primary)'
          }}>
            Take Action
          </h4>
          <div style={{
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap'
          }}>
            {onApprove && (
              <button
                onClick={async () => {
                  if (isProcessing) return;
                  setIsProcessing(true);
                  try {
                    const approvedAmount = decisionData?.approved_amount;
                    await onApprove(approvedAmount);
                  } catch (error) {
                    console.error('Approve failed:', error);
                  } finally {
                    setIsProcessing(false);
                  }
                }}
                disabled={isProcessing}
                style={{
                  flex: '1',
                  minWidth: '150px',
                  padding: '12px 24px',
                  background: 'var(--success)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.6 : 1,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '0.9';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {isProcessing ? 'Processing...' : '✅ Approve'}
              </button>
            )}
            
            {onDeny && (
              <button
                onClick={async () => {
                  if (isProcessing) return;
                  setIsProcessing(true);
                  try {
                    await onDeny();
                  } catch (error) {
                    console.error('Deny failed:', error);
                  } finally {
                    setIsProcessing(false);
                  }
                }}
                disabled={isProcessing}
                style={{
                  flex: '1',
                  minWidth: '150px',
                  padding: '12px 24px',
                  background: 'var(--danger)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.6 : 1,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '0.9';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {isProcessing ? 'Processing...' : '❌ Deny'}
              </button>
            )}
            
            {onRequestInfo && (
              <button
                onClick={async () => {
                  if (isProcessing) return;
                  setIsProcessing(true);
                  try {
                    await onRequestInfo();
                  } catch (error) {
                    console.error('Request info failed:', error);
                  } finally {
                    setIsProcessing(false);
                  }
                }}
                disabled={isProcessing}
                style={{
                  flex: '1',
                  minWidth: '150px',
                  padding: '12px 24px',
                  background: 'var(--warning)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.6 : 1,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '0.9';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isProcessing) {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {isProcessing ? 'Processing...' : '📋 Request Info'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
