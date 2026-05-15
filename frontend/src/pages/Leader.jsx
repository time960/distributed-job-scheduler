import { useState, useEffect } from 'react';
import api from '../api';
import { Crown } from 'lucide-react';

export default function Leader() {
  const [leader, setLeader] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchLeader = async () => {
    try {
      const res = await api.get('/leader');
      setLeader(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeader();
    const interval = setInterval(fetchLeader, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1 className="page-title">Scheduler Leader Election</h1>
      
      <div className="glass-panel" style={{ padding: '3rem', display: 'flex', flexDirection: 'column', alignItems: 'center', maxWidth: '600px', margin: '0 auto' }}>
        <Crown size={64} color="var(--warning-color)" style={{ marginBottom: '1.5rem' }} />
        
        {loading && !leader ? (
          <div>Checking leader status...</div>
        ) : (
          <>
            <div style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Current Leader</div>
            <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'monospace', color: 'white', marginBottom: '2rem' }}>
              {leader?.leader_id || 'No Active Leader'}
            </div>
            
            <div style={{ display: 'flex', gap: '2rem', width: '100%', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Status</div>
                <span className={leader?.status === 'active' ? 'badge success' : 'badge danger'}>
                  {leader?.status === 'active' ? 'ACTIVE' : 'NO LEADER'}
                </span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Lock TTL</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'white' }}>
                  {leader?.ttl ? `${leader.ttl}s` : 'N/A'}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
