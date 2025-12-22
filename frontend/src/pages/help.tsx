import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styles from '@/styles/Help.module.css';

interface FAQItem {
  question: string;
  answer: string;
}

export default function HelpPage() {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  const faqs: FAQItem[] = [
    {
      question: "How do I submit a new claim?",
      answer: "To submit a claim, log in to your account, navigate to the Claims page, and click 'Submit New Claim'. Upload your claim documents (PDF, JPG, or PNG), and our AI system will automatically extract the information. Review the extracted data and submit."
    },
    {
      question: "What document formats are supported?",
      answer: "We support PDF, JPG, and PNG formats. Maximum file size is 10MB per document. For best results, ensure your documents are clear, well-lit, and readable."
    },
    {
      question: "How long does claim processing take?",
      answer: "Document processing typically takes 30-60 seconds. Low-risk claims may be automatically approved within minutes. Claims requiring manual review are typically processed within 1-2 business days."
    },
    {
      question: "What is auto-approval?",
      answer: "Our AI system automatically approves claims that meet certain criteria: amount under threshold, high OCR quality, high AI confidence score, no duplicate matches, and low fraud risk. This speeds up processing for straightforward claims."
    },
    {
      question: "How accurate is the AI extraction?",
      answer: "Our system uses PaddleOCR and ClaimSphere AI (powered by ERNIE 4.5) with over 95% accuracy for standard claim formats. Each extracted field includes a confidence score. You can review and correct any fields before submitting."
    },
    {
      question: "Can I edit extracted information?",
      answer: "Yes! After the AI extracts information from your documents, you can review and edit any fields before submitting your claim. Simply click on any field to make corrections."
    },
    {
      question: "What happens after I submit a claim?",
      answer: "Once submitted, your claim goes through validation. If it meets auto-approval criteria, it's approved immediately. Otherwise, it enters the review queue for an agent to evaluate. You can track your claim status in real-time on the Claims page."
    },
    {
      question: "How do I check my claim status?",
      answer: "Log in to your account and navigate to the Claims page. You'll see all your claims with their current status: Draft, Submitted, Extracted, Validated, Pending Review, Approved, Denied, or Closed."
    },
    {
      question: "What are the different user roles?",
      answer: "USER (Claimant): Submit and view your own claims. AGENT (Adjuster): Review and approve/deny claims in the queue. ADMIN: Full system access including user management, analytics, and configuration."
    },
    {
      question: "Can I upload multiple documents for one claim?",
      answer: "Yes, you can upload multiple supporting documents for a single claim. This is useful when you have receipts, medical records, and insurance forms that all relate to one claim."
    },
    {
      question: "What is duplicate detection?",
      answer: "Our system automatically checks for potential duplicate claims by comparing new submissions with existing claims. This helps prevent fraud and accidental duplicate submissions."
    },
    {
      question: "How secure is my data?",
      answer: "We use industry-standard security measures including JWT authentication, password hashing, role-based access control, and complete audit logging. Your data is encrypted both in transit and at rest."
    },
    {
      question: "What should I do if the OCR extraction is incorrect?",
      answer: "If the AI doesn't extract information correctly, you can manually correct any fields during the review step before submitting. The system learns from corrections to improve future extractions."
    },
    {
      question: "Can I use natural language queries?",
      answer: "Yes! Use the Natural Language Query feature to ask questions about your claims in plain English, such as 'What is the total amount of my approved claims?' or 'Show me claims from last month.'"
    },
    {
      question: "What if my claim is denied?",
      answer: "If your claim is denied, you'll receive a detailed explanation. You can view the denial reason in your claim details and contact support if you believe there was an error."
    },
    {
      question: "How do I reset my password?",
      answer: "Click 'Forgot Password?' on the login page, enter your email address, and follow the instructions sent to your email to reset your password."
    },
    {
      question: "What browsers are supported?",
      answer: "ClaimSphere AI works best on modern browsers including Chrome, Firefox, Safari, and Edge. We recommend using the latest version of your preferred browser for the best experience."
    },
    {
      question: "Is there a mobile app?",
      answer: "Currently, ClaimSphere AI is a web-based application optimized for both desktop and mobile browsers. A native mobile app is planned for future release."
    }
  ];

  return (
    <>
      <Head>
        <title>Help & Support | ClaimSphere AI</title>
        <meta name="description" content="Get help with ClaimSphere AI - FAQs, documentation, and support" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Hero Section */}
          <div className={styles.hero}>
            <div className={styles.heroContent}>
              <h1 className={styles.heroTitle}>
                Help & Support
              </h1>
              <p className={styles.heroSubtitle}>
                Find answers to common questions and get the support you need
              </p>
            </div>
          </div>

          {/* Quick Links */}
          <div className={styles.quickLinks}>
            <Link href="#faq" className={styles.quickLink}>
              <span>📚</span>
              <div>
                <h3>FAQs</h3>
                <p>Common questions answered</p>
              </div>
            </Link>
            <Link href="#contact" className={styles.quickLink}>
              <span>📧</span>
              <div>
                <h3>Contact Us</h3>
                <p>Get in touch with support</p>
              </div>
            </Link>
            <Link href="#guides" className={styles.quickLink}>
              <span>📖</span>
              <div>
                <h3>Guides</h3>
                <p>Step-by-step tutorials</p>
              </div>
            </Link>
            <Link href="/claims/new" className={styles.quickLink}>
              <span>🚀</span>
              <div>
                <h3>Submit Claim</h3>
                <p>Start a new claim</p>
              </div>
            </Link>
          </div>

          {/* FAQs Section */}
          <section id="faq" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <span>📚</span>
                Frequently Asked Questions
              </h2>
              <p className={styles.sectionSubtitle}>
                Find quick answers to the most common questions about ClaimSphere AI
              </p>
            </div>

            <div className={styles.faqList}>
              {faqs.map((faq, index) => (
                <div key={index} className={styles.faqItem}>
                  <button
                    className={`${styles.faqQuestion} ${openFAQ === index ? styles.faqQuestionOpen : ''}`}
                    onClick={() => toggleFAQ(index)}
                  >
                    <span>{faq.question}</span>
                    <span className={styles.faqIcon}>
                      {openFAQ === index ? '−' : '+'}
                    </span>
                  </button>
                  {openFAQ === index && (
                    <div className={styles.faqAnswer}>
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Guides Section */}
          <section id="guides" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <span>📖</span>
                User Guides
              </h2>
            </div>

            <div className={styles.guidesGrid}>
              <div className={styles.guideCard}>
                <div className={styles.guideIcon}>🚀</div>
                <h3>Getting Started</h3>
                <p>Learn how to create an account and submit your first claim</p>
                <Link href="/claims/new" className={styles.guideLink}>
                  Start Tutorial →
                </Link>
              </div>

              <div className={styles.guideCard}>
                <div className={styles.guideIcon}>📤</div>
                <h3>Submitting Claims</h3>
                <p>Best practices for uploading documents and getting accurate results</p>
                <Link href="/claims/new" className={styles.guideLink}>
                  Learn More →
                </Link>
              </div>

              <div className={styles.guideCard}>
                <div className={styles.guideIcon}>📊</div>
                <h3>Understanding Analytics</h3>
                <p>How to use the dashboard and analytics features</p>
                <Link href="/analytics" className={styles.guideLink}>
                  View Analytics →
                </Link>
              </div>

              <div className={styles.guideCard}>
                <div className={styles.guideIcon}>🤖</div>
                <h3>AI Features</h3>
                <p>Learn about our AI-powered extraction and validation</p>
                <Link href="/claims/new" className={styles.guideLink}>
                  Explore AI →
                </Link>
              </div>
            </div>
          </section>

          {/* Contact Section */}
          <section id="contact" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <span>📧</span>
                Contact Support
              </h2>
              <p className={styles.sectionSubtitle}>
                Can't find what you're looking for? Our support team is here to help
              </p>
            </div>

            <div className={styles.contactGrid}>
              <div className={styles.contactCard}>
                <div className={styles.contactIcon}>📧</div>
                <h3>Email Support</h3>
                <p>Get help via email</p>
                <a href="mailto:support@claimsphere.ai" className={styles.contactLink}>
                  support@claimsphere.ai
                </a>
                <p className={styles.contactNote}>Response within 24 hours</p>
              </div>

              <div className={styles.contactCard}>
                <div className={styles.contactIcon}>📞</div>
                <h3>Phone Support</h3>
                <p>Speak with our team</p>
                <a href="tel:1-800-CLAIMS-AI" className={styles.contactLink}>
                  1-800-CLAIMS-AI
                </a>
                <p className={styles.contactNote}>Mon-Fri, 9AM-5PM EST</p>
              </div>

              <div className={styles.contactCard}>
                <div className={styles.contactIcon}>💬</div>
                <h3>Live Chat</h3>
                <p>Chat with support</p>
                <button className={styles.contactLink} onClick={() => alert('Chat feature coming soon!')}>
                  Start Chat
                </button>
                <p className={styles.contactNote}>Available during business hours</p>
              </div>

              <div className={styles.contactCard}>
                <div className={styles.contactIcon}>📍</div>
                <h3>Office Location</h3>
                <p>Visit us in person</p>
                <address className={styles.contactAddress}>
                  123 Innovation Drive<br />
                  Suite 100<br />
                  San Francisco, CA 94105
                </address>
              </div>
            </div>
          </section>

          {/* Additional Resources */}
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <span>🔗</span>
                Additional Resources
              </h2>
            </div>

            <div className={styles.resourcesList}>
              <Link href="/" className={styles.resourceItem}>
                <span>🏠</span>
                <div>
                  <h4>Dashboard</h4>
                  <p>Return to your dashboard</p>
                </div>
              </Link>
              
              <Link href="/claims" className={styles.resourceItem}>
                <span>📋</span>
                <div>
                  <h4>My Claims</h4>
                  <p>View and manage your claims</p>
                </div>
              </Link>
              
              <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" className={styles.resourceItem}>
                <span>💻</span>
                <div>
                  <h4>API Documentation</h4>
                  <p>Developer resources and API docs</p>
                </div>
              </a>
              
              <a href="https://status.claimsphere.ai" target="_blank" rel="noopener noreferrer" className={styles.resourceItem}>
                <span>✅</span>
                <div>
                  <h4>System Status</h4>
                  <p>Check service availability</p>
                </div>
              </a>
            </div>
          </section>

          {/* CTA Section */}
          <div className={styles.ctaSection}>
            <h2>Still have questions?</h2>
            <p>Our support team is ready to help you succeed</p>
            <div className={styles.ctaButtons}>
              <a href="mailto:support@claimsphere.ai" className={styles.ctaButton}>
                Contact Support
              </a>
              <Link href="/claims/new" className={styles.ctaButtonSecondary}>
                Submit a Claim
              </Link>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

