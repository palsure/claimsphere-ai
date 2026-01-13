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
              {/* Show observation and evidence if available */}
              {(reviewData as any).observation && (
                <div style={{ marginBottom: '20px', padding: '12px', background: 'var(--bg-elevated)', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                  <h5 style={{ marginBottom: '8px', fontWeight: '600', color: 'var(--text-primary)' }}>📝 Observation</h5>
                  <p style={{ lineHeight: '1.6', color: 'var(--text-secondary)' }}>{(reviewData as any).observation}</p>
                </div>
              )}
              
              {(reviewData as any).evidence && (
                <div style={{ marginBottom: '20px', padding: '12px', background: 'var(--bg-elevated)', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                  <h5 style={{ marginBottom: '8px', fontWeight: '600', color: 'var(--text-primary)' }}>🔍 Evidence</h5>
                  <p style={{ lineHeight: '1.6', color: 'var(--text-secondary)' }}>{(reviewData as any).evidence}</p>
                </div>
              )}
              
              {reviewData.confidence_level !== undefined && (
                <div className={styles.confidence} style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '500' }}>Confidence Level:</span>
                    <span style={{ 
                      fontWeight: '600', 
                      color: 'var(--accent-primary)',
                      fontSize: '1.1rem'
                    }}>
                      {(reviewData.confidence_level * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className={styles.confidenceBar} style={{ height: '8px', borderRadius: '4px' }}>
                    <div 
                      className={styles.confidenceFill}
                      style={{ 
                        width: `${reviewData.confidence_level * 100}%`,
                        height: '100%',
                        borderRadius: '4px',
                        transition: 'width 0.3s ease'
                      }}
                    />
                  </div>
                </div>
              )}
              
              {reviewData.key_findings && reviewData.key_findings.length > 0 && (
                <div className={styles.findings} style={{ marginBottom: '20px' }}>
                  <h5 style={{ 
                    marginBottom: '12px', 
                    color: 'var(--text-primary)',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    🔍 Key Findings
                  </h5>
                  <ul style={{ 
                    listStyle: 'none', 
                    padding: 0, 
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px'
                  }}>
                    {reviewData.key_findings.map((finding, idx) => {
                      // Type guard: check if finding is an object with observation property
                      const isObjectWithObservation = typeof finding === 'object' && finding !== null && 'observation' in finding;
                      const findingObj = finding as any; // Type assertion for flexible handling
                      
                      return (
                        <li key={idx} style={{
                          padding: '12px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          lineHeight: '1.5'
                        }}>
                          {isObjectWithObservation ? (
                            <div>
                              <div style={{ fontWeight: '500', marginBottom: '6px' }}>
                                {findingObj.observation}
                              </div>
                              {findingObj.evidence && (
                                <div style={{ 
                                  marginTop: '6px', 
                                  fontSize: '0.9em', 
                                  color: 'var(--text-secondary)',
                                  fontStyle: 'italic',
                                  paddingLeft: '12px',
                                  borderLeft: '2px solid var(--border-color)'
                                }}>
                                  {findingObj.evidence}
                                </div>
                              )}
                            </div>
                          ) : (
                            <span>{String(finding)}</span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              
              {reviewData.concerns && reviewData.concerns.length > 0 && (
                <div className={styles.concerns} style={{ marginBottom: '20px' }}>
                  <h5 style={{ 
                    marginBottom: '12px', 
                    color: 'var(--warning)',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    ⚠️ Concerns
                  </h5>
                  <ul style={{ 
                    listStyle: 'none', 
                    padding: 0, 
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px'
                  }}>
                    {reviewData.concerns.map((concern, idx) => (
                      <li key={idx} style={{
                        padding: '12px',
                        background: 'rgba(251, 191, 36, 0.1)',
                        borderRadius: '6px',
                        border: '1px solid rgba(251, 191, 36, 0.3)',
                        lineHeight: '1.5'
                      }}>
                        {typeof concern === 'object' && concern !== null ? (
                          concern.concern || concern.text || JSON.stringify(concern)
                        ) : (
                          String(concern)
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {reviewData.recommendations && reviewData.recommendations.length > 0 && (
                <div className={styles.recommendations} style={{ marginBottom: '20px' }}>
                  <h5 style={{ 
                    marginBottom: '12px', 
                    color: 'var(--info)',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    💡 Recommendations
                  </h5>
                  <ul style={{ 
                    listStyle: 'none', 
                    padding: 0, 
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px'
                  }}>
                    {reviewData.recommendations.map((rec, idx) => (
                      <li key={idx} style={{
                        padding: '12px',
                        background: 'rgba(56, 189, 248, 0.1)',
                        borderRadius: '6px',
                        border: '1px solid rgba(56, 189, 248, 0.3)',
                        lineHeight: '1.5'
                      }}>
                        {typeof rec === 'object' && rec !== null ? (
                          rec.recommendation || rec.text || JSON.stringify(rec)
                        ) : (
                          String(rec)
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Show detailed reasoning only if it's an object with additional info not already displayed */}
              {reviewData.reasoning && typeof reviewData.reasoning === 'object' && (
                <div className={styles.reasoning}>
                  <h5>Detailed Reasoning</h5>
                  <div style={{
                    padding: '12px',
                    background: 'var(--bg-elevated)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                    lineHeight: '1.6'
                  }}>
                    {Object.entries(reviewData.reasoning).map(([key, value]) => {
                      // Skip fields already displayed above
                      if (['overall_assessment', 'confidence_level', 'key_findings', 'concerns', 'recommendations'].includes(key)) {
                        return null;
                      }
                      
                      return (
                        <div key={key} style={{ marginBottom: '12px' }}>
                          <strong style={{ 
                            textTransform: 'capitalize', 
                            color: 'var(--text-primary)',
                            display: 'block',
                            marginBottom: '4px'
                          }}>
                            {key.replace(/_/g, ' ')}:
                          </strong>
                          {Array.isArray(value) ? (
                            <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                              {value.map((item, idx) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>
                                  {typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)}
                                </li>
                              ))}
                            </ul>
                          ) : typeof value === 'object' && value !== null ? (
                            <pre style={{
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-word',
                              fontSize: '0.85rem',
                              padding: '8px',
                              background: 'var(--bg-card)',
                              borderRadius: '4px',
                              margin: '4px 0'
                            }}>
                              {JSON.stringify(value, null, 2)}
                            </pre>
                          ) : (
                            <span style={{ color: 'var(--text-secondary)' }}>{String(value)}</span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {/* Show raw reasoning text if it's a string and not JSON */}
              {reviewData.reasoning && typeof reviewData.reasoning === 'string' && !reviewData.reasoning.trim().startsWith('{') && (
                <div className={styles.reasoning}>
                  <h5>Reasoning</h5>
                  <p style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: '1.6' }}>
                    {reviewData.reasoning}
                  </p>
                </div>
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
              {decisionData.approved_amount !== undefined && decisionData.approved_amount !== null && (
                <div className={styles.amount}>
                  <strong>Approved Amount:</strong> ${decisionData.approved_amount.toFixed(2)}
                </div>
              )}
              
              {decisionData.confidence !== undefined && (
                <div className={styles.confidence}>
                  <span>Decision Confidence: </span>
                  <div className={styles.confidenceBar}>
                    <div 
                      className={styles.confidenceFill}
                      style={{ width: `${decisionData.confidence * 100}%` }}
                    />
                  </div>
                  <span>{(decisionData.confidence * 100).toFixed(0)}%</span>
                </div>
              )}
              
              {decisionData.reasoning && (
                <div className={styles.reasoning}>
                  <h5>Decision Reasoning</h5>
                  <p>{decisionData.reasoning}</p>
                </div>
              )}
              
              {decisionData.policy_references && decisionData.policy_references.length > 0 && (
                <div className={styles.policies} style={{ marginBottom: '20px' }}>
                  <h5 style={{ 
                    marginBottom: '12px', 
                    color: 'var(--text-primary)',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    📋 Policy References
                  </h5>
                  <ul style={{ 
                    listStyle: 'none', 
                    padding: 0, 
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {decisionData.policy_references.map((policy, idx) => {
                      // Type guard: check if policy is an object with properties
                      const isObjectWithProperties = typeof policy === 'object' && policy !== null && ('policy' in policy || 'reference' in policy || 'text' in policy);
                      const policyObj = policy as any; // Type assertion for flexible handling
                      
                      return (
                        <li key={idx} style={{
                          padding: '10px 12px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.95rem'
                        }}>
                          {isObjectWithProperties ? (
                            policyObj.policy || policyObj.reference || policyObj.text || JSON.stringify(policyObj)
                          ) : (
                            String(policy)
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              
              {decisionData.conditions && decisionData.conditions.length > 0 && (
                <div className={styles.conditions} style={{ marginBottom: '20px' }}>
                  <h5 style={{ 
                    marginBottom: '12px', 
                    color: 'var(--text-primary)',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    📝 Conditions
                  </h5>
                  <ul style={{ 
                    listStyle: 'none', 
                    padding: 0, 
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    {decisionData.conditions.map((condition, idx) => {
                      // Type guard: check if condition is an object with properties
                      const isObjectWithProperties = typeof condition === 'object' && condition !== null && ('condition' in condition || 'text' in condition);
                      const conditionObj = condition as any; // Type assertion for flexible handling
                      
                      return (
                        <li key={idx} style={{
                          padding: '10px 12px',
                          background: 'var(--bg-elevated)',
                          borderRadius: '6px',
                          border: '1px solid var(--border-color)',
                          fontSize: '0.95rem'
                        }}>
                          {isObjectWithProperties ? (
                            conditionObj.condition || conditionObj.text || JSON.stringify(conditionObj)
                          ) : (
                            String(condition)
                          )}
                        </li>
                      );
                    })}
                  </ul>
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
