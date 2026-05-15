import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Calendar, Users, Crown, Activity } from 'lucide-react';

export default function Layout() {
  return (
    <div className="layout-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <Activity size={24} color="var(--accent-color)" />
          Job Scheduler
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={20} /> Dashboard
          </NavLink>
          <NavLink to="/jobs" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Briefcase size={20} /> Jobs
          </NavLink>
          <NavLink to="/schedules" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Calendar size={20} /> Schedules
          </NavLink>
          <NavLink to="/workers" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Users size={20} /> Workers
          </NavLink>
          <NavLink to="/leader" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Crown size={20} /> Leader Election
          </NavLink>
          <NavLink to="/monitoring" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Activity size={20} /> Monitoring
          </NavLink>
        </nav>
      </aside>
      
      <main className="main-content">
        <header className="header">
          <div style={{ fontWeight: 500 }}>Admin Dashboard</div>
          <div>
            <span className="badge success">System Online</span>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
