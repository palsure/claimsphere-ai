import { useState, useEffect } from 'react';
import styles from './RolePlayingReview.module.css';

interface RolePlayingReviewProps {
  review: {
    review?: {
      overall_assessment?: string;
      confidence_level?: number;
      key_findings?: string[];
      concerns?: string[];
      recommendations?: string[];
      reasoning?: string;
    };
    decision?: {
      decision?: string;
      approved_amount?: number;
      confidence?: number;
      reasoning?: string;
      policy_references?: string[];
      conditions?: string[];
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
}

export default function RolePlayingReview({ review, onClose }: RolePlayingReviewProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['review', 'decision']));
  
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };
  
  const reviewData = review.review || {};
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
                {reviewData.overall_assessment}
              </span>
            )}
          </div>
          
          {expandedSections.has('review') && (
            <div className={styles.sectionContent}>
              {reviewData.confidence_level !== undefined && (
                <div className={styles.confidence}>
                  <span>Confidence: </span>
                  <div className={styles.confidenceBar}>
                    <div 
                      className={styles.confidenceFill}
                      style={{ width: `${reviewData.confidence_level * 100}%` }}
                    />
                  </div>
                  <span>{(reviewData.confidence_level * 100).toFixed(0)}%</span>
                </div>
              )}
              
              {reviewData.key_findings && reviewData.key_findings.length > 0 && (
                <div className={styles.findings}>
                  <h5>Key Findings</h5>
                  <ul>
                    {reviewData.key_findings.map((finding, idx) => (
                      <li key={idx}>{finding}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {reviewData.concerns && reviewData.concerns.length > 0 && (
                <div className={styles.concerns}>
                  <h5>⚠️ Concerns</h5>
                  <ul>
                    {reviewData.concerns.map((concern, idx) => (
                      <li key={idx}>{concern}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {reviewData.recommendations && reviewData.recommendations.length > 0 && (
                <div className={styles.recommendations}>
                  <h5>💡 Recommendations</h5>
                  <ul>
                    {reviewData.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {reviewData.reasoning && (
                <div className={styles.reasoning}>
                  <h5>Reasoning</h5>
                  <p>{reviewData.reasoning}</p>
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
                <div className={styles.policies}>
                  <h5>Policy References</h5>
                  <ul>
                    {decisionData.policy_references.map((policy, idx) => (
                      <li key={idx}>{policy}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {decisionData.conditions && decisionData.conditions.length > 0 && (
                <div className={styles.conditions}>
                  <h5>Conditions</h5>
                  <ul>
                    {decisionData.conditions.map((condition, idx) => (
                      <li key={idx}>{condition}</li>
                    ))}
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
    </div>
  );
}
