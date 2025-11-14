import React from 'react';
import { CheckCircle, AlertTriangle, Info, TrendingUp } from 'lucide-react';
import './AnalysisResults.css';

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

interface AnalysisResultsProps {
  result: AnalysisResult;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => {
  const { analysis } = result;
  const confidencePercentage = (analysis.confidence * 100).toFixed(1);
  const isAuthentic = !analysis.is_deepfake;

  return (
    <div className="analysis-results">
      <div className={`result-header ${isAuthentic ? 'authentic' : 'fake'}`}>
        {isAuthentic ? (
          <>
            <CheckCircle size={32} />
            <h2>Authentic Media</h2>
          </>
        ) : (
          <>
            <AlertTriangle size={32} />
            <h2>Manipulation Detected</h2>
          </>
        )}
      </div>

      <div className="result-content">
        <div className="confidence-section">
          <h3>Confidence Score</h3>
          <div className="confidence-meter">
            <div
              className={`confidence-bar ${isAuthentic ? 'authentic' : 'fake'}`}
              style={{ width: `${confidencePercentage}%` }}
            >
              <span className="confidence-value">{confidencePercentage}%</span>
            </div>
          </div>
        </div>

        <div className="info-grid">
          <div className="info-card">
            <h4>File Name</h4>
            <p>{result.file_name}</p>
          </div>

          <div className="info-card">
            <h4>Manipulation Type</h4>
            <p className="manipulation-type">
              {analysis.manipulation_type.replace(/_/g, ' ').toUpperCase()}
            </p>
          </div>

          {analysis.is_ai_generated !== undefined && (
            <div className="info-card">
              <h4>AI Generated</h4>
              <p>{analysis.is_ai_generated ? 'Yes' : 'No'}</p>
            </div>
          )}

          {analysis.is_voice_cloned !== undefined && (
            <div className="info-card">
              <h4>Voice Cloning</h4>
              <p>{analysis.is_voice_cloned ? 'Detected' : 'Not Detected'}</p>
            </div>
          )}
        </div>

        <div className="explanation-section">
          <div className="explanation-header">
            <Info size={20} />
            <h3>Analysis Explanation</h3>
          </div>
          <p className="explanation-text">{analysis.explanation}</p>
        </div>

        <div className="details-section">
          <h3>Technical Details</h3>
          <div className="details-grid">
            {Object.entries(analysis.details).map(([key, value]) => (
              <div key={key} className="detail-item">
                <span className="detail-key">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:
                </span>
                <span className="detail-value">
                  {typeof value === 'number'
                    ? value.toFixed(4)
                    : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="timestamp">
          <small>Analysis completed at: {new Date(result.timestamp).toLocaleString()}</small>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;
