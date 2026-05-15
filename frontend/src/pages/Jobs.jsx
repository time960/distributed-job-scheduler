import { useState, useEffect } from 'react';
import api from '../api';

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filter state
  const [statusFilter, setStatusFilter] = useState('');
  
  // Form state
  const [name, setName] = useState('');
  const [payload, setPayload] = useState('{}');
  const [priority, setPriority] = useState(0);

  // Action state
  const [actionLoading, setActionLoading] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  const fetchJobs = async () => {
    try {
      let url = '/jobs?limit=50';
      if (statusFilter) url += `&status=${statusFilter}`;
      const res = await api.get(url);
      setJobs(res.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  const handleCreateJob = async (e) => {
    e.preventDefault();
    try {
      await api.post('/jobs', {
        name,
        payload: JSON.parse(payload),
        priority: parseInt(priority)
      });
      setName('');
      setPayload('{}');
      setPriority(0);
      fetchJobs();
    } catch (err) {
      alert('Failed to create job');
    }
  };

  const handleCancelJob = async (id) => {
    setActionLoading(id);
    setActionMessage(null);
    try {
      await api.post(`/jobs/${id}/cancel`);
      setActionMessage({ type: 'success', text: 'Job cancelled successfully' });
      fetchJobs();
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Failed to cancel job' });
    } finally {
      setActionLoading(null);
      setTimeout(() => setActionMessage(null), 3000);
    }
  };

  const handleRetryJob = async (id) => {
    setActionLoading(id);
    setActionMessage(null);
    try {
      await api.post(`/jobs/${id}/retry`);
      setActionMessage({ type: 'success', text: 'Job retried successfully' });
      fetchJobs();
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Failed to retry job' });
    } finally {
      setActionLoading(null);
      setTimeout(() => setActionMessage(null), 3000);
    }
  };

  const getStatusBadge = (status) => {
    const s = status.toUpperCase();
    if (s === 'SUCCESS') return 'badge success';
    if (s === 'FAILED' || s === 'DEAD_LETTER') return 'badge danger';
    if (s === 'PENDING') return 'badge warning';
    if (s === 'RUNNING') return 'badge primary';
    return 'badge secondary';
  };

  return (
    <div>
      <h1 className="page-title">Jobs Management</h1>
      
      <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', flex: 1 }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Create New Job</h2>
          <form onSubmit={handleCreateJob}>
            <div className="form-group">
              <label>Job Name</label>
              <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Payload (JSON)</label>
              <input type="text" className="form-control" value={payload} onChange={e => setPayload(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Priority</label>
              <input type="number" className="form-control" value={priority} onChange={e => setPriority(e.target.value)} />
            </div>
            <button type="submit" className="btn btn-primary">Create Job</button>
          </form>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', flex: 2 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem' }}>Recent Jobs</h2>
            <select className="form-control" style={{ width: 'auto' }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="RUNNING">Running</option>
              <option value="SUCCESS">Success</option>
              <option value="FAILED">Failed</option>
              <option value="DEAD_LETTER">Dead Letter</option>
            </select>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem' }}>{error}</div>}
            {actionMessage && (
              <div style={{ 
                padding: '0.75rem', 
                marginBottom: '1rem', 
                borderRadius: '6px', 
                backgroundColor: actionMessage.type === 'success' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: actionMessage.type === 'success' ? 'var(--success-color)' : 'var(--danger-color)'
              }}>
                {actionMessage.text}
              </div>
            )}
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Attempts</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length === 0 ? (
                  <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No jobs found</td></tr>
                ) : (
                  jobs.map(job => (
                    <tr key={job.id}>
                      <td>{job.name}</td>
                      <td><span className={getStatusBadge(job.status)}>{job.status}</span></td>
                      <td>{job.priority}</td>
                      <td>{job.attempts}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          {(job.status.toUpperCase() === 'PENDING' || job.status.toUpperCase() === 'RUNNING') && (
                            <button 
                              className="btn btn-danger" 
                              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} 
                              onClick={() => handleCancelJob(job.id)}
                              disabled={actionLoading === job.id}
                            >
                              {actionLoading === job.id ? 'Cancelling...' : 'Cancel'}
                            </button>
                          )}
                          {(job.status.toUpperCase() === 'FAILED' || job.status.toUpperCase() === 'DEAD_LETTER') && (
                            <button 
                              className="btn btn-primary" 
                              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} 
                              onClick={() => handleRetryJob(job.id)}
                              disabled={actionLoading === job.id}
                            >
                              {actionLoading === job.id ? 'Retrying...' : 'Retry'}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
