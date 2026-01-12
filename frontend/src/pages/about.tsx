import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/About.module.css';

export default function About() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Head>
        <title>About - ClaimSphere AI</title>
        <meta name="description" content="Learn how ClaimSphere AI processes insurance claims using CAMEL-AI multi-agent system" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Hero Section */}
          <section className={styles.hero}>
            <h1 className={styles.heroTitle}>
              <span className={styles.heroIcon}>🤖</span>
              About ClaimSphere AI
            </h1>
            <p className={styles.heroSubtitle}>
              Intelligent claim processing powered by CAMEL-AI multi-agent system and ERNIE 5.0 Thinking
            </p>
          </section>

          {/* Overview Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>System Overview</h2>
            <div className={styles.overviewGrid}>
              <div className={styles.overviewCard}>
                <div className={styles.cardIcon}>🔍</div>
                <h3>Intelligent Extraction</h3>
                <p>AI-powered extraction of claim data from documents using ERNIE 5.0 Thinking</p>
              </div>
              <div className={styles.overviewCard}>
                <div className={styles.cardIcon}>✅</div>
                <h3>Smart Validation</h3>
                <p>Automated validation with reasoning traces for transparent decision-making</p>
              </div>
              <div className={styles.overviewCard}>
                <div className={styles.cardIcon}>🛡️</div>
                <h3>Fraud Detection</h3>
                <p>Advanced fraud risk assessment using pattern analysis and anomaly detection</p>
              </div>
              <div className={styles.overviewCard}>
                <div className={styles.cardIcon}>💬</div>
                <h3>Natural Language</h3>
                <p>Ask questions about claims in plain English with AI-powered responses</p>
              </div>
            </div>
          </section>

          {/* Claim Processing Steps */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Claim Processing Workflow</h2>
            <p className={styles.sectionDescription}>
              Our system uses a sophisticated multi-agent architecture powered by CAMEL-AI to process claims intelligently and transparently.
            </p>

            <div className={styles.stepsContainer}>
              {/* Step 1 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>1</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>📤</span>
                    Document Upload
                  </h3>
                  <p className={styles.stepDescription}>
                    Users upload claim documents (PDF, images) through our intuitive 3-step wizard. 
                    The system accepts medical bills, insurance forms, receipts, and other claim-related documents.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Supported Formats:</strong> PDF, PNG, JPG, JPEG
                    <br />
                    <strong>Max Size:</strong> 10MB per file
                    <br />
                    <strong>Features:</strong> Drag & drop, sample files, batch upload
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>2</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>🔍</span>
                    OCR Processing (OCR Agent)
                  </h3>
                  <p className={styles.stepDescription}>
                    The <strong>OCR Agent</strong> uses PaddleOCR 3.x to extract text and layout information from documents. 
                    This agent identifies text regions, preserves document structure, and provides quality scores.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> PaddleOCR 3.x
                    <br />
                    <strong>Output:</strong> Raw text, layout coordinates, quality score, language detection
                    <br />
                    <strong>Features:</strong> Multi-language support, layout preservation, quality assessment
                  </div>
                  <div className={styles.agentBadge}>Agent: OCR Agent</div>
                </div>
              </div>

              {/* Step 3 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>3</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>🧠</span>
                    AI Field Extraction (Extraction Agent)
                  </h3>
                  <p className={styles.stepDescription}>
                    The <strong>Extraction Agent</strong> uses CAMEL-AI ChatAgent with ERNIE 5.0 Thinking to analyze 
                    the OCR text and extract structured claim data. This agent identifies key fields like claimant name, 
                    provider, dates, amounts, and claim types.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
                    <br />
                    <strong>Output:</strong> Structured JSON with claim fields, confidence scores, reasoning traces
                    <br />
                    <strong>Fields Extracted:</strong> Claimant name, provider name, date of incident, total amount, 
                    currency, claim type, policy number, diagnosis, procedure, description
                  </div>
                  <div className={styles.agentBadge}>Agent: Extraction Agent (CAMEL-AI ChatAgent)</div>
                </div>
              </div>

              {/* Step 4 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>4</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>✅</span>
                    Validation (Validation Agent)
                  </h3>
                  <p className={styles.stepDescription}>
                    The <strong>Validation Agent</strong> uses CAMEL-AI ChatAgent to validate extracted data against 
                    business rules and policies. It identifies inconsistencies, missing information, and potential issues, 
                    providing clear recommendations.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
                    <br />
                    <strong>Output:</strong> Validation results (is_valid, errors, recommendations, risk_level, requires_manual_review)
                    <br />
                    <strong>Checks:</strong> Data completeness, consistency, policy compliance, date validation, amount verification
                  </div>
                  <div className={styles.agentBadge}>Agent: Validation Agent (CAMEL-AI ChatAgent)</div>
                </div>
              </div>

              {/* Step 5 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>5</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>🛡️</span>
                    Fraud Detection (Fraud Detection Agent)
                  </h3>
                  <p className={styles.stepDescription}>
                    The <strong>Fraud Detection Agent</strong> analyzes claim patterns and compares against historical data 
                    to assess fraud risk. It identifies suspicious patterns, anomalies, and red flags.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
                    <br />
                    <strong>Output:</strong> Fraud risk score (0.0-1.0), reasons for assessment, pattern analysis
                    <br />
                    <strong>Analysis:</strong> Amount patterns, frequency analysis, provider patterns, claimant history
                  </div>
                  <div className={styles.agentBadge}>Agent: Fraud Detection Agent (CAMEL-AI ChatAgent)</div>
                </div>
              </div>

              {/* Step 6 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>6</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>🔁</span>
                    Duplicate Detection (Duplicate Agent)
                  </h3>
                  <p className={styles.stepDescription}>
                    The <strong>Duplicate Detection Agent</strong> compares the new claim against existing claims to identify 
                    potential duplicates. It uses similarity algorithms to match claims based on multiple criteria.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> Rule-based similarity + optional AI analysis
                    <br />
                    <strong>Output:</strong> Duplicate matches with similarity scores, matching claim IDs
                    <br />
                    <strong>Matching Criteria:</strong> Claimant name, amount, date, provider, claim type, procedure codes
                  </div>
                  <div className={styles.agentBadge}>Agent: Duplicate Detection Agent</div>
                </div>
              </div>

              {/* Step 7 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>7</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>🤖</span>
                    Auto-Approval Decision
                  </h3>
                  <p className={styles.stepDescription}>
                    The system evaluates auto-approval criteria based on configured thresholds. Claims that meet all criteria 
                    are automatically approved, while others are sent for manual review.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Criteria:</strong> Amount threshold, OCR quality, extraction confidence, duplicate score, fraud risk
                    <br />
                    <strong>Decision:</strong> AUTO_APPROVED or PENDING_REVIEW
                    <br />
                    <strong>Configuration:</strong> Per-plan thresholds, customizable rules
                  </div>
                </div>
              </div>

              {/* Step 8 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>8</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>👥</span>
                    Role-Playing Review (Optional)
                  </h3>
                  <p className={styles.stepDescription}>
                    For complex claims, the system can use <strong>Role-Playing Agents</strong> to simulate a human review process. 
                    The Review Agent acts as a Senior Claims Reviewer, and the Approval Agent makes final decisions through 
                    multi-turn discussions.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI Role-Playing Agents (Review Agent + Approval Agent)
                    <br />
                    <strong>Process:</strong> Multi-turn conversation, discussion of concerns, consensus building
                    <br />
                    <strong>Output:</strong> Review assessment, final decision, reasoning traces, discussion log
                  </div>
                  <div className={styles.agentBadge}>Agents: Review Agent + Approval Agent (CAMEL-AI Role-Playing)</div>
                </div>
              </div>

              {/* Step 9 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>9</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>
                    <span className={styles.stepIcon}>📊</span>
                    Final Status & Notification
                  </h3>
                  <p className={styles.stepDescription}>
                    The claim reaches its final status (APPROVED, DENIED, or PENDED) and the user is notified. 
                    All processing steps, reasoning traces, and agent decisions are logged for transparency and audit.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Status Options:</strong> APPROVED, DENIED, PENDED (needs more info), AUTO_APPROVED
                    <br />
                    <strong>Audit Trail:</strong> Complete log of all agent actions, decisions, and reasoning
                    <br />
                    <strong>User Actions:</strong> View status, respond to info requests, track timeline
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* CAMEL-AI Agents Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>CAMEL-AI Multi-Agent System</h2>
            <p className={styles.sectionDescription}>
              Our system leverages the CAMEL-AI framework to create specialized AI agents that work together seamlessly.
            </p>

            <div className={styles.agentsGrid}>
              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>🔍</span>
                  <h3>OCR Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Extracts text and layout from documents using PaddleOCR. Provides quality scores and language detection.
                </p>
                <div className={styles.agentTech}>PaddleOCR 3.x</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>🧠</span>
                  <h3>Extraction Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Uses CAMEL-AI ChatAgent with ERNIE 5.0 Thinking to extract structured data from OCR text.
                </p>
                <div className={styles.agentTech}>CAMEL-AI ChatAgent + ERNIE 5.0 Thinking</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>✅</span>
                  <h3>Validation Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Validates claims using CAMEL-AI ChatAgent with reasoning traces for transparent decisions.
                </p>
                <div className={styles.agentTech}>CAMEL-AI ChatAgent + ERNIE 5.0 Thinking</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>🛡️</span>
                  <h3>Fraud Detection Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Assesses fraud risk using pattern analysis and anomaly detection with explainable AI.
                </p>
                <div className={styles.agentTech}>CAMEL-AI ChatAgent + ERNIE 5.0 Thinking</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>🔁</span>
                  <h3>Duplicate Detection Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Identifies duplicate claims using similarity algorithms and pattern matching.
                </p>
                <div className={styles.agentTech}>Rule-based + AI Analysis</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>💬</span>
                  <h3>Query Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Answers natural language questions about claims using CAMEL-AI ChatAgent with citations.
                </p>
                <div className={styles.agentTech}>CAMEL-AI ChatAgent + ERNIE 5.0 Thinking</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>👨‍💼</span>
                  <h3>Review Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Role-playing agent that acts as a Senior Claims Reviewer with 15 years of experience.
                </p>
                <div className={styles.agentTech}>CAMEL-AI Role-Playing + ERNIE 5.0 Thinking</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>✅</span>
                  <h3>Approval Agent</h3>
                </div>
                <p className={styles.agentDescription}>
                  Role-playing agent that makes final approval decisions with authority and reasoning.
                </p>
                <div className={styles.agentTech}>CAMEL-AI Role-Playing + ERNIE 5.0 Thinking</div>
              </div>
            </div>
          </section>

          {/* Key Features Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Key Features</h2>
            <div className={styles.featuresGrid}>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🔍</span>
                <h3>Intelligent Extraction</h3>
                <p>AI-powered extraction with reasoning traces for transparency</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🤖</span>
                <h3>Multi-Agent System</h3>
                <p>Specialized agents working together for optimal results</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>💬</span>
                <h3>Natural Language Queries</h3>
                <p>Ask questions in plain English with AI-powered responses</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>👥</span>
                <h3>Role-Playing Agents</h3>
                <p>Simulated human-like review and approval processes</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🛡️</span>
                <h3>Fraud Detection</h3>
                <p>Advanced risk assessment with pattern analysis</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>✅</span>
                <h3>Auto-Approval</h3>
                <p>Intelligent auto-approval based on configurable thresholds</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>📊</span>
                <h3>Analytics & Insights</h3>
                <p>Comprehensive analytics with trend analysis</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🔐</span>
                <h3>Role-Based Access</h3>
                <p>Secure access control with granular permissions</p>
              </div>
            </div>
          </section>

          {/* Technology Stack Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Technology Stack</h2>
            <div className={styles.techGrid}>
              <div className={styles.techCategory}>
                <h3>AI Framework</h3>
                <ul>
                  <li>CAMEL-AI Multi-Agent Framework</li>
                  <li>ERNIE 5.0 Thinking (Qianfan Platform)</li>
                  <li>PaddleOCR 3.x</li>
                </ul>
              </div>
              <div className={styles.techCategory}>
                <h3>Backend</h3>
                <ul>
                  <li>FastAPI (Python 3.10+)</li>
                  <li>PostgreSQL / SQLite</li>
                  <li>SQLAlchemy ORM</li>
                  <li>JWT Authentication</li>
                </ul>
              </div>
              <div className={styles.techCategory}>
                <h3>Frontend</h3>
                <ul>
                  <li>Next.js 14</li>
                  <li>React + TypeScript</li>
                  <li>CSS Modules</li>
                  <li>React Context API</li>
                </ul>
              </div>
            </div>
          </section>

          {/* CTA Section */}
          {!isAuthenticated && (
            <section className={styles.ctaSection}>
              <h2 className={styles.ctaTitle}>Ready to Get Started?</h2>
              <p className={styles.ctaDescription}>
                Experience intelligent claim processing powered by CAMEL-AI and ERNIE 5.0 Thinking
              </p>
              <div className={styles.ctaButtons}>
                <Link href="/signup" className={styles.ctaButtonPrimary}>
                  Get Started
                </Link>
                <Link href="/login" className={styles.ctaButtonSecondary}>
                  Sign In
                </Link>
              </div>
            </section>
          )}

          {isAuthenticated && (
            <section className={styles.ctaSection}>
              <h2 className={styles.ctaTitle}>Start Processing Claims</h2>
              <p className={styles.ctaDescription}>
                Upload your first claim and see the CAMEL-AI multi-agent system in action
              </p>
              <div className={styles.ctaButtons}>
                <Link href="/claims/new" className={styles.ctaButtonPrimary}>
                  Submit a Claim
                </Link>
                <Link href="/claims" className={styles.ctaButtonSecondary}>
                  View My Claims
                </Link>
              </div>
            </section>
          )}
        </div>
      </main>
    </>
  );
}
