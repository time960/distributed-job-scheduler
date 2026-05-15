import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Schedules from './pages/Schedules';
import Workers from './pages/Workers';
import Leader from './pages/Leader';
import Monitoring from './pages/Monitoring';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="jobs" element={<Jobs />} />
          <Route path="schedules" element={<Schedules />} />
          <Route path="workers" element={<Workers />} />
          <Route path="leader" element={<Leader />} />
          <Route path="monitoring" element={<Monitoring />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
