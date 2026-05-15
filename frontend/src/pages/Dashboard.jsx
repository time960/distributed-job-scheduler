import { useState, useEffect } from 'react';
import api from '../api';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      const res = await api.get('/metrics/simple');
      setMetrics(res.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) return <div>Loading dashboard...</div>;
  if (error) return <div style={{ color: 'var(--danger-color)' }}>{error}</div>;

  return (
    <div>
      <h1 className="page-title">Dashboard Overview</h1>
      
      <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>Jobs Metrics</h2>
      <div className="grid-cards">
        <div className="glass-panel metric-card">
          <div className="metric-title">Total Jobs</div>
          <div className="metric-value">{metrics?.jobs.total || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid var(--accent-color)' }}>
          <div className="metric-title">Pending Jobs</div>
          <div className="metric-value">{metrics?.jobs.pending || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid #8b5cf6' }}>
          <div className="metric-title">Running Jobs</div>
          <div className="metric-value">{metrics?.jobs.running || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid var(--success-color)' }}>
          <div className="metric-title">Success Jobs</div>
          <div className="metric-value">{metrics?.jobs.success || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid var(--danger-color)' }}>
          <div className="metric-title">Failed Jobs</div>
          <div className="metric-value">{metrics?.jobs.failed || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid #64748b' }}>
          <div className="metric-title">Dead Letter Jobs</div>
          <div className="metric-value">{metrics?.jobs.dead_letter || 0}</div>
        </div>
      </div>

      <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>Worker Metrics</h2>
      <div className="grid-cards">
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid var(--success-color)' }}>
          <div className="metric-title">Active Workers</div>
          <div className="metric-value">{metrics?.workers.active || 0}</div>
        </div>
        <div className="glass-panel metric-card" style={{ borderTop: '3px solid var(--danger-color)' }}>
          <div className="metric-title">Dead Workers</div>
          <div className="metric-value">{metrics?.workers.dead || 0}</div>
        </div>
      </div>
    </div>
  );
}
