import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/About.module.css';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Head>
        <title>ClaimSphere AI - Intelligent Claim Processing</title>
        <meta name="description" content="Learn how ClaimSphere AI processes insurance claims using CAMEL-AI multi-agent system and ERNIE 5.0 Thinking" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Hero Section */}
          <section className={styles.hero}>
            <h1 className={styles.heroTitle}>
              ClaimSphere AI
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
                <div className={styles.stepContent}>
                  <div className={styles.stepNumber}>1</div>
                  <div className={styles.stepIcon}>📤</div>
                  <h3 className={styles.stepTitle}>Document Upload</h3>
                  <p className={styles.stepDescription}>
                    Users upload claim documents (PDF, images) through our intuitive 3-step wizard.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Formats:</strong> PDF, PNG, JPG, JPEG
                    <br />
                    <strong>Max Size:</strong> 10MB per file
                  </div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 2 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>2</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>🔍</div>
                  <h3 className={styles.stepTitle}>OCR Processing</h3>
                  <p className={styles.stepDescription}>
                    The <strong>OCR Agent</strong> uses PaddleOCR 3.x to extract text and layout information.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> PaddleOCR 3.x
                    <br />
                    <strong>Output:</strong> Text, layout, quality score
                  </div>
                  <div className={styles.agentBadge}>OCR Agent</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 3 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>3</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>🧠</div>
                  <h3 className={styles.stepTitle}>AI Extraction</h3>
                  <p className={styles.stepDescription}>
                    The <strong>Extraction Agent</strong> uses CAMEL-AI ChatAgent with ERNIE 5.0 Thinking to extract structured data.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent + ERNIE 5.0
                    <br />
                    <strong>Output:</strong> Structured fields with reasoning
                  </div>
                  <div className={styles.agentBadge}>Extraction Agent</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 4 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>4</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>✅</div>
                  <h3 className={styles.stepTitle}>Validation</h3>
                  <p className={styles.stepDescription}>
                    The <strong>Validation Agent</strong> validates data against business rules and policies.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent
                    <br />
                    <strong>Output:</strong> Validation results & recommendations
                  </div>
                  <div className={styles.agentBadge}>Validation Agent</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 5 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>5</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>🛡️</div>
                  <h3 className={styles.stepTitle}>Fraud Detection</h3>
                  <p className={styles.stepDescription}>
                    The <strong>Fraud Detection Agent</strong> analyzes patterns to assess fraud risk.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI ChatAgent
                    <br />
                    <strong>Output:</strong> Risk score & pattern analysis
                  </div>
                  <div className={styles.agentBadge}>Fraud Detection Agent</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 6 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>6</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>🔁</div>
                  <h3 className={styles.stepTitle}>Duplicate Check</h3>
                  <p className={styles.stepDescription}>
                    The <strong>Duplicate Agent</strong> compares against existing claims to identify duplicates.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> Similarity algorithms
                    <br />
                    <strong>Output:</strong> Duplicate matches & scores
                  </div>
                  <div className={styles.agentBadge}>Duplicate Agent</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 7 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>7</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>🤖</div>
                  <h3 className={styles.stepTitle}>Auto-Approval</h3>
                  <p className={styles.stepDescription}>
                    System evaluates criteria and auto-approves or sends for review.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Criteria:</strong> Amount, quality, confidence
                    <br />
                    <strong>Decision:</strong> AUTO_APPROVED or REVIEW
                  </div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 8 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>8</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>👥</div>
                  <h3 className={styles.stepTitle}>AI Review</h3>
                  <p className={styles.stepDescription}>
                    <strong>Role-Playing Agents</strong> simulate human review for complex claims.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI Role-Playing
                    <br />
                    <strong>Output:</strong> Review & decision with reasoning
                  </div>
                  <div className={styles.agentBadge}>Review + Approval Agents</div>
                </div>
              </div>
              
              <div className={styles.stepConnector} aria-hidden="true">→</div>

              {/* Step 9 */}
              <div className={styles.step}>
                <div className={styles.stepNumber}>9</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepIcon}>📊</div>
                  <h3 className={styles.stepTitle}>Final Status</h3>
                  <p className={styles.stepDescription}>
                    Claim reaches final status and user is notified with complete audit trail.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Status:</strong> APPROVED, DENIED, or PENDED
                    <br />
                    <strong>Audit:</strong> Complete log of all actions
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
        </div>
      </main>
    </>
  );
}
