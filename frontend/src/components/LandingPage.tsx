import React from 'react';
import { Shield, Zap, Lock, Database, Users, Globe, CheckCircle, ArrowRight, Play, Award } from 'lucide-react';
import './LandingPage.css';

interface LandingPageProps {
  onGetStarted: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <Award size={16} />
            <span>98% Detection Accuracy</span>
          </div>
          <h1 className="hero-title">
            All-In-One <span className="gradient-text">Deepfake Detection</span>
          </h1>
          <p className="hero-description">
            Deepfake Detection for videos, images, audio. Boost your investigations with our
            deepfake detection hub. Anohra Deep Guard AI is a user-friendly application with
            API access, cloud-based and on-premise deployment. Upload files or URLs and get a
            multilayer assessment in a few seconds.
          </p>
          <div className="hero-cta">
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started
              <ArrowRight size={20} />
            </button>
            <button className="btn-secondary">
              <Play size={20} />
              Watch Demo
            </button>
          </div>
          <div className="trust-badges">
            <span>Trusted by law enforcement, enterprises, and cybersecurity teams worldwide</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card card-1">
            <Shield size={32} className="card-icon" />
            <h4>Real-time Detection</h4>
            <p>Instant analysis in seconds</p>
          </div>
          <div className="floating-card card-2">
            <Zap size={32} className="card-icon" />
            <h4>98% Accuracy</h4>
            <p>Industry-leading precision</p>
          </div>
          <div className="floating-card card-3">
            <Lock size={32} className="card-icon" />
            <h4>Secure & Private</h4>
            <p>Enterprise-grade security</p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stat-item">
          <h3>98%</h3>
          <p>Detection Accuracy</p>
          <span>vs 70% non-AI tools</span>
        </div>
        <div className="stat-item">
          <h3>35,000+</h3>
          <p>Deepfakes Identified</p>
          <span>In the last 12 months</span>
        </div>
        <div className="stat-item">
          <h3>14 min</h3>
          <p>Time Saved</p>
          <span>Per manual review</span>
        </div>
        <div className="stat-item">
          <h3>9,000+</h3>
          <p>Sources Monitored</p>
          <span>Real-time tracking</span>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>Advanced Detection Capabilities</h2>
          <p>Powered by cutting-edge AI and deep learning technology</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <Shield size={28} />
            </div>
            <h3>Multi-Format Detection</h3>
            <p>Analyze videos, images, audio files, and identities with a single platform. Comprehensive coverage for all media types.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> Video deepfake detection</li>
              <li><CheckCircle size={16} /> AI-generated image analysis</li>
              <li><CheckCircle size={16} /> Voice cloning identification</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <Zap size={28} />
            </div>
            <h3>Detection at Scale</h3>
            <p>Process thousands of files simultaneously with our advanced AI algorithms. Identify synthetic media imperceptible to humans.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> Batch processing</li>
              <li><CheckCircle size={16} /> Real-time analysis</li>
              <li><CheckCircle size={16} /> Automated workflows</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <Database size={28} />
            </div>
            <h3>Multilayer Assessment</h3>
            <p>Multiple detection algorithms working in parallel to ensure the highest accuracy and minimize false positives.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> Pixel-level analysis</li>
              <li><CheckCircle size={16} /> Frequency domain detection</li>
              <li><CheckCircle size={16} /> Temporal consistency checks</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <Lock size={28} />
            </div>
            <h3>Enterprise Security</h3>
            <p>GDPR compliant with enterprise-grade security. On-premise deployment available for maximum data privacy.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> ISO 27001 certified</li>
              <li><CheckCircle size={16} /> End-to-end encryption</li>
              <li><CheckCircle size={16} /> On-premise options</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <Globe size={28} />
            </div>
            <h3>API & Integration</h3>
            <p>Seamlessly integrate deepfake detection into your existing workflows with our comprehensive RESTful API.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> RESTful API access</li>
              <li><CheckCircle size={16} /> SDK libraries</li>
              <li><CheckCircle size={16} /> Webhook support</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <Users size={28} />
            </div>
            <h3>Training & Support</h3>
            <p>Interactive training modules and real-world scenario analysis to help your team develop detection expertise.</p>
            <ul className="feature-list">
              <li><CheckCircle size={16} /> Expert training programs</li>
              <li><CheckCircle size={16} /> 24/7 technical support</li>
              <li><CheckCircle size={16} /> Regular updates</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="use-cases-section">
        <div className="section-header">
          <h2>Trusted Across Industries</h2>
          <p>Protecting organizations from AI-powered threats</p>
        </div>
        <div className="use-cases-grid">
          <div className="use-case-card">
            <h4>Law Enforcement</h4>
            <p>Support criminal investigations with forensic-grade deepfake detection</p>
          </div>
          <div className="use-case-card">
            <h4>Cybersecurity</h4>
            <p>Detect and prevent social engineering attacks using synthetic media</p>
          </div>
          <div className="use-case-card">
            <h4>Media & Journalism</h4>
            <p>Verify authenticity of user-generated content and news sources</p>
          </div>
          <div className="use-case-card">
            <h4>Financial Services</h4>
            <p>Enhanced KYC verification and fraud prevention capabilities</p>
          </div>
          <div className="use-case-card">
            <h4>Enterprise Security</h4>
            <p>Protect your organization from deepfake-based attacks</p>
          </div>
          <div className="use-case-card">
            <h4>Government & Defense</h4>
            <p>National security and intelligence operations support</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Protect Your Organization?</h2>
          <p>Start detecting deepfakes with industry-leading accuracy today</p>
          <div className="cta-buttons">
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started Free
              <ArrowRight size={20} />
            </button>
            <button className="btn-secondary">
              Contact Sales
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
