import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  // Mock data for demonstration
  const analysisStats = [
    { name: 'Images', analyzed: 145, deepfakes: 23 },
    { name: 'Videos', analyzed: 89, deepfakes: 34 },
    { name: 'Audio', analyzed: 67, deepfakes: 12 },
  ];

  const detectionTypes = [
    { name: 'Face Swap', value: 35, color: '#ef4444' },
    { name: 'AI Generated', value: 28, color: '#f59e0b' },
    { name: 'Voice Clone', value: 12, color: '#8b5cf6' },
    { name: 'Lip Sync', value: 15, color: '#ec4899' },
    { name: 'Authentic', value: 210, color: '#10b981' },
  ];

  const totalAnalyzed = analysisStats.reduce((sum, stat) => sum + stat.analyzed, 0);
  const totalDeepfakes = analysisStats.reduce((sum, stat) => sum + stat.deepfakes, 0);
  const detectionRate = ((totalDeepfakes / totalAnalyzed) * 100).toFixed(1);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Analytics Dashboard</h2>
        <p>Overview of all analyzed media and detection statistics</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#3b82f6' }}>
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Analyzed</h3>
            <p className="stat-value">{totalAnalyzed}</p>
            <span className="stat-label">Media files</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#ef4444' }}>
            <AlertCircle size={24} />
          </div>
          <div className="stat-content">
            <h3>Deepfakes Found</h3>
            <p className="stat-value">{totalDeepfakes}</p>
            <span className="stat-label">Manipulated files</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#10b981' }}>
            <CheckCircle2 size={24} />
          </div>
          <div className="stat-content">
            <h3>Authentic Files</h3>
            <p className="stat-value">{totalAnalyzed - totalDeepfakes}</p>
            <span className="stat-label">Verified genuine</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#8b5cf6' }}>
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <h3>Detection Rate</h3>
            <p className="stat-value">{detectionRate}%</p>
            <span className="stat-label">Manipulation rate</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Analysis by Media Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analysisStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="analyzed" fill="#3b82f6" name="Total Analyzed" />
              <Bar dataKey="deepfakes" fill="#ef4444" name="Deepfakes Detected" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Detection Types Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={detectionTypes}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {detectionTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="recent-analyses">
        <h3>Recent Analyses</h3>
        <div className="analysis-table">
          <div className="table-header">
            <span>File Name</span>
            <span>Type</span>
            <span>Result</span>
            <span>Confidence</span>
            <span>Date</span>
          </div>
          {/* Mock recent analyses */}
          {[
            { name: 'video_sample.mp4', type: 'Video', result: 'Deepfake', confidence: 94.5, date: '2025-11-15' },
            { name: 'profile_photo.jpg', type: 'Image', result: 'Authentic', confidence: 98.2, date: '2025-11-15' },
            { name: 'voice_recording.mp3', type: 'Audio', result: 'Voice Clone', confidence: 87.3, date: '2025-11-14' },
            { name: 'portrait_ai.png', type: 'Image', result: 'AI Generated', confidence: 96.8, date: '2025-11-14' },
            { name: 'interview_clip.mp4', type: 'Video', result: 'Authentic', confidence: 99.1, date: '2025-11-13' },
          ].map((analysis, index) => (
            <div key={index} className="table-row">
              <span>{analysis.name}</span>
              <span className="type-badge">{analysis.type}</span>
              <span className={`result-badge ${analysis.result === 'Authentic' ? 'authentic' : 'fake'}`}>
                {analysis.result}
              </span>
              <span>{analysis.confidence}%</span>
              <span>{analysis.date}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
