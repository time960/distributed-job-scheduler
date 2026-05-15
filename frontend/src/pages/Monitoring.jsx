import { ExternalLink } from 'lucide-react';

export default function Monitoring() {
  const links = [
    { name: 'FastAPI Swagger', url: 'http://localhost:8000/docs', desc: 'API Documentation & Testing' },
    { name: 'Prometheus', url: 'http://localhost:9090', desc: 'Metrics Data Source' },
    { name: 'Grafana', url: 'http://localhost:3000', desc: 'System Dashboards' },
    { name: 'Locust', url: 'http://localhost:8089', desc: 'Load Testing Interface' },
    { name: 'Metrics Endpoint', url: 'http://localhost:8000/metrics', desc: 'Raw Prometheus Metrics' },
    { name: 'Chaos Status', url: 'http://localhost:8000/chaos/status', desc: 'Chaos Engineering Controls' }
  ];

  return (
    <div>
      <h1 className="page-title">Monitoring & Infrastructure</h1>
      
      <div className="grid-cards">
        {links.map((link, idx) => (
          <a key={idx} href={link.url} target="_blank" rel="noopener noreferrer" className="glass-panel metric-card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white', marginBottom: '0.25rem' }}>{link.name}</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{link.desc}</div>
            </div>
            <ExternalLink size={20} color="var(--text-secondary)" />
          </a>
        ))}
      </div>
    </div>
  );
}
