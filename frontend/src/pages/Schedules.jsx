import { useState, useEffect } from 'react';
import api from '../api';

export default function Schedules() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Form state
  const [name, setName] = useState('');
  const [cron, setCron] = useState('* * * * *');
  const [jobName, setJobName] = useState('');
  const [jobPayload, setJobPayload] = useState('{}');

  const fetchSchedules = async () => {
    try {
      const res = await api.get('/schedules');
      setSchedules(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules();
    const interval = setInterval(fetchSchedules, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/schedules', {
        name,
        cron_expression: cron,
        job_name: jobName,
        job_payload: JSON.parse(jobPayload)
      });
      setName('');
      setCron('* * * * *');
      setJobName('');
      setJobPayload('{}');
      fetchSchedules();
    } catch (err) {
      alert('Failed to create schedule');
    }
  };

  const handlePause = async (id) => {
    try {
      await api.post(`/schedules/${id}/pause`);
      fetchSchedules();
    } catch (err) {
      alert('Failed to pause schedule');
    }
  };

  const handleResume = async (id) => {
    try {
      await api.post(`/schedules/${id}/resume`);
      fetchSchedules();
    } catch (err) {
      alert('Failed to resume schedule');
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/schedules/${id}`);
      fetchSchedules();
    } catch (err) {
      alert('Failed to delete schedule');
    }
  };

  return (
    <div>
      <h1 className="page-title">Schedules Management</h1>
      
      <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', flex: 1 }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Create Schedule</h2>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>Schedule Name</label>
              <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Cron Expression</label>
              <input type="text" className="form-control" value={cron} onChange={e => setCron(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Job Name</label>
              <input type="text" className="form-control" value={jobName} onChange={e => setJobName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Job Payload (JSON)</label>
              <input type="text" className="form-control" value={jobPayload} onChange={e => setJobPayload(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary">Create Schedule</button>
          </form>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', flex: 2 }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Active Schedules</h2>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Cron</th>
                  <th>Job Name</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {schedules.length === 0 ? (
                  <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No schedules found</td></tr>
                ) : (
                  schedules.map(schedule => (
                    <tr key={schedule.id}>
                      <td>{schedule.name}</td>
                      <td><code>{schedule.cron_expression}</code></td>
                      <td>{schedule.job_name}</td>
                      <td>
                        <span className={schedule.is_paused ? 'badge warning' : 'badge success'}>
                          {schedule.is_paused ? 'PAUSED' : 'ACTIVE'}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          {schedule.is_paused ? (
                            <button className="btn btn-success" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleResume(schedule.id)}>Resume</button>
                          ) : (
                            <button className="btn btn-warning" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.2)', color: 'var(--warning-color)', border: '1px solid rgba(245, 158, 11, 0.3)' }} onClick={() => handlePause(schedule.id)}>Pause</button>
                          )}
                          <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDelete(schedule.id)}>Delete</button>
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
