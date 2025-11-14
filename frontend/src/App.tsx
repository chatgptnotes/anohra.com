import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import AnalysisResults from './components/AnalysisResults';
import Dashboard from './components/Dashboard';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface AnalysisResult {
  file_id: string;
  file_name: string;
  analysis: {
    is_deepfake: boolean;
    is_ai_generated?: boolean;
    is_voice_cloned?: boolean;
    confidence: number;
    manipulation_type: string;
    details: any;
    explanation: string;
  };
  timestamp: string;
}

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard'>('upload');

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result);
    setLoading(false);
    setError(null);
  };

  const handleAnalysisStart = () => {
    setLoading(true);
    setError(null);
    setAnalysisResult(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Shield size={32} />
            <h1>DeepGuard AI</h1>
          </div>
          <p className="tagline">Advanced Deepfake Detection Platform</p>
        </div>
        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            Upload & Analyze
          </button>
          <button
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'upload' ? (
          <div className="upload-section">
            <div className="info-banner">
              <Info size={20} />
              <p>
                Upload images, videos, or audio files to detect deepfakes, AI-generated content,
                and voice cloning with industry-leading accuracy.
              </p>
            </div>

            <FileUpload
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisStart={handleAnalysisStart}
              onError={handleError}
            />

            {loading && (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Analyzing media... This may take a few moments.</p>
              </div>
            )}

            {error && (
              <div className="error-banner">
                <AlertTriangle size={20} />
                <p>{error}</p>
              </div>
            )}

            {analysisResult && !loading && (
              <AnalysisResults result={analysisResult} />
            )}
          </div>
        ) : (
          <Dashboard />
        )}
      </main>

      <footer className="app-footer">
        <p>
          DeepGuard AI - Protecting authenticity in the age of synthetic media |{' '}
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
