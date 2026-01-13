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
                    Role-Playing Review (Optional - Agent Only)
                  </h3>
                  <p className={styles.stepDescription}>
                    For complex claims, agents can use <strong>Role-Playing Agents</strong> to simulate a human review process. 
                    The Review Agent acts as a Senior Claims Reviewer (15 years experience), and the Approval Agent makes final 
                    decisions through multi-turn discussions. This provides detailed assessments with reasoning, confidence scores, 
                    and policy references.
                  </p>
                  <div className={styles.stepDetails}>
                    <strong>Technology:</strong> CAMEL-AI Role-Playing Agents + OLLAMA (phi3:mini)
                    <br />
                    <strong>Process:</strong> Multi-turn conversation, discussion of concerns, consensus building
                    <br />
                    <strong>Output:</strong> Review assessment, final decision, reasoning traces, discussion log, confidence scores
                    <br />
                    <strong>Access:</strong> Available to Agents and Admins via "Gen AI Review" button
                  </div>
                  <div className={styles.agentBadge}>Agents: Review Agent + Approval Agent (CAMEL-AI Role-Playing + OLLAMA)</div>
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

          {/* AI Assistant Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>AI Assistant - Natural Language Queries</h2>
            <p className={styles.sectionDescription}>
              Ask questions about your claims in plain English and get concise, relevant answers with full transparency.
            </p>

            <div className={styles.featureHighlight}>
              <div className={styles.highlightIcon}>💬</div>
              <div className={styles.highlightContent}>
                <h3>How It Works</h3>
                <p>
                  The <strong>Query Agent</strong> uses CAMEL-AI ChatAgent with OLLAMA (phi3:mini) to understand your questions 
                  and provide focused answers. It analyzes your claims data, extracts relevant information, and presents it in 
                  a clear, concise format.
                </p>
                <ul className={styles.highlightList}>
                  <li><strong>Concise Answers:</strong> Short, focused responses (max 150 chars) with key facts</li>
                  <li><strong>Cited Claims:</strong> See exactly which claims were used in the answer</li>
                  <li><strong>Fields Used:</strong> Understand which data fields were analyzed</li>
                  <li><strong>Reasoning:</strong> View the AI's analysis process (when available)</li>
                  <li><strong>RBAC-Enforced:</strong> Access is restricted based on your role</li>
                </ul>
              </div>
            </div>

            <div className={styles.exampleQueries}>
              <h3>Example Queries</h3>
              <div className={styles.queryExamples}>
                <div className={styles.queryExample}>
                  <strong>For Users:</strong>
                  <ul>
                    <li>"What's the status of my latest claim?"</li>
                    <li>"How much have I claimed this year?"</li>
                    <li>"Which of my claims are still pending?"</li>
                  </ul>
                </div>
                <div className={styles.queryExample}>
                  <strong>For Agents:</strong>
                  <ul>
                    <li>"How many claims are in my queue?"</li>
                    <li>"What's the total value of pending claims?"</li>
                    <li>"Which claims have been waiting the longest?"</li>
                  </ul>
                </div>
                <div className={styles.queryExample}>
                  <strong>For Admins:</strong>
                  <ul>
                    <li>"What's the total amount of all pending claims?"</li>
                    <li>"How many claims were approved this month?"</li>
                    <li>"Which category has the highest claim amounts?"</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* Role Playing Review Section */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Role-Playing Review - AI-Powered Claim Analysis</h2>
            <p className={styles.sectionDescription}>
              Experience human-like claim review through AI agents that simulate real-world review and approval processes.
            </p>

            <div className={styles.featureHighlight}>
              <div className={styles.highlightIcon}>👥</div>
              <div className={styles.highlightContent}>
                <h3>How It Works</h3>
                <p>
                  The <strong>Role-Playing Coordinator</strong> orchestrates a conversation between two specialized AI agents:
                </p>
                <ol className={styles.highlightList}>
                  <li><strong>Review Agent:</strong> Acts as a Senior Claims Reviewer with 15 years of experience. 
                    Thoroughly reviews the claim and provides detailed assessment with key findings, concerns, and recommendations.</li>
                  <li><strong>Approval Agent:</strong> Acts as a Claims Approver with decision-making authority. 
                    Reviews the assessment and makes a final decision (Approve/Deny/Request Info) with reasoning and policy references.</li>
                  <li><strong>Optional Discussion:</strong> Agents can engage in multi-turn conversations to discuss concerns, 
                    clarify issues, and reach consensus before making a decision.</li>
                </ol>
              </div>
            </div>

            <div className={styles.reviewFeatures}>
              <h3>Review Output Includes</h3>
              <div className={styles.reviewFeaturesGrid}>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>📋</span>
                  <h4>Overall Assessment</h4>
                  <p>Clear recommendation: Approve, Deny, or Request More Info</p>
                </div>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>📊</span>
                  <h4>Confidence Level</h4>
                  <p>Confidence score (0-1.0) indicating certainty of the assessment</p>
                </div>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>🔍</span>
                  <h4>Key Findings</h4>
                  <p>Important observations and patterns identified in the claim</p>
                </div>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>⚠️</span>
                  <h4>Concerns</h4>
                  <p>Potential issues, red flags, or areas requiring attention</p>
                </div>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>💡</span>
                  <h4>Recommendations</h4>
                  <p>Actionable recommendations for claim processing</p>
                </div>
                <div className={styles.reviewFeature}>
                  <span className={styles.reviewFeatureIcon}>📚</span>
                  <h4>Policy References</h4>
                  <p>Relevant policies and rules that influenced the decision</p>
                </div>
              </div>
            </div>

            <div className={styles.accessNote}>
              <strong>Note:</strong> Role-Playing Review is available to <strong>Agents and Admins only</strong>. 
              Access it via the "Gen AI Review" button on claim details pages.
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
                  <h3>Query Agent (AI Assistant)</h3>
                </div>
                <p className={styles.agentDescription}>
                  Answers natural language questions with concise, relevant answers. Provides reasoning traces, cited claims, and fields used.
                </p>
                <div className={styles.agentTech}>CAMEL-AI ChatAgent + OLLAMA (phi3:mini)</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>👨‍💼</span>
                  <h3>Review Agent (Role-Playing)</h3>
                </div>
                <p className={styles.agentDescription}>
                  Role-playing agent that acts as a Senior Claims Reviewer with 15 years of experience. Provides detailed assessments with reasoning.
                </p>
                <div className={styles.agentTech}>CAMEL-AI Role-Playing + OLLAMA (phi3:mini)</div>
              </div>

              <div className={styles.agentCard}>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>✅</span>
                  <h3>Approval Agent (Role-Playing)</h3>
                </div>
                <p className={styles.agentDescription}>
                  Role-playing agent that makes final approval decisions with authority and reasoning. Can discuss with Review Agent.
                </p>
                <div className={styles.agentTech}>CAMEL-AI Role-Playing + OLLAMA (phi3:mini)</div>
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
                <h3>AI Assistant</h3>
                <p>Ask questions in plain English. Get concise answers with reasoning, cited claims, and fields used</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>👥</span>
                <h3>Role-Playing Review</h3>
                <p>AI agents simulate human-like review and approval processes with multi-turn discussions</p>
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
                  <li>OLLAMA (phi3:mini) - Local, Fast, Free</li>
                  <li>ERNIE 5.0 Thinking (Qianfan Platform - Fallback)</li>
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
