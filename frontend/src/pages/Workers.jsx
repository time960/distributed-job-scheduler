import { useState, useEffect } from 'react';
import api from '../api';

export default function Workers() {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchWorkers = async () => {
    try {
      const res = await api.get('/workers');
      setWorkers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkers();
    const interval = setInterval(fetchWorkers, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleString();
  };

  return (
    <div>
      <h1 className="page-title">Workers Status</h1>
      
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Worker ID</th>
                <th>Hostname</th>
                <th>Status</th>
                <th>Jobs Processed</th>
                <th>Last Heartbeat</th>
              </tr>
            </thead>
            <tbody>
              {workers.length === 0 ? (
                <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No workers found</td></tr>
              ) : (
                workers.map(worker => (
                  <tr key={worker.id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{worker.id}</td>
                    <td>{worker.hostname}</td>
                    <td>
                      <span className={worker.status === 'ACTIVE' ? 'badge success' : 'badge danger'}>
                        {worker.status}
                      </span>
                    </td>
                    <td>{worker.jobs_processed}</td>
                    <td>{formatDate(worker.last_heartbeat_at || worker.last_heartbeat)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
