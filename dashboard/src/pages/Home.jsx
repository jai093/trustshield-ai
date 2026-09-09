import React, { useEffect, useState } from 'react';
import { 
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, 
  Title, Tooltip as ChartTooltip, Legend as ChartLegend, Filler, ArcElement 
} from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';
import { 
  ShieldAlert, ShieldCheck, Mail, Activity, AlertTriangle 
} from 'lucide-react';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, ChartTooltip, ChartLegend, Filler, ArcElement
);

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

export default function Home() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-User-Id': 'dashboard-user',
      };
      
      const [statsRes, historyRes] = await Promise.all([
        fetch('http://localhost:8000/api/dashboard/stats', { headers }),
        fetch('http://localhost:8000/api/history?limit=10', { headers })
      ]);
      
      if (!statsRes.ok || !historyRes.ok) throw new Error('Failed to fetch dashboard data');
      
      const statsData = await statsRes.json();
      const historyData = await historyRes.json();
      
      setStats(statsData?.data ?? null);
      setHistory(historyData?.data ?? []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Unable to load dashboard stats.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const intervalId = window.setInterval(fetchDashboardData, 5000);
    return () => window.clearInterval(intervalId);
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
      x: { grid: { display: false } }
    }
  };

  const lineData = {
    labels: stats?.timeline?.map(t => t.date) || [],
    datasets: [
      {
        label: 'Phishing Detected',
        data: stats?.timeline?.map(t => t.phishing) || [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.3)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Total Analyzed',
        data: stats?.timeline?.map(t => t.total) || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.3)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'right' }
    }
  };

  const pieData = {
    labels: stats?.top_threats?.map(t => t.threat.replace('_', ' ').toUpperCase()) || [],
    datasets: [
      {
        data: stats?.top_threats?.map(t => t.count) || [],
        backgroundColor: COLORS,
        borderWidth: 1,
      }
    ]
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-8 lg:p-10 font-sans text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
              <img src="/trustshieldlogo.png" alt="TrustShield AI" className="h-12 w-auto object-contain" />
              TrustShield AI Dashboard
            </h1>
            <p className="text-slate-500 mt-1">Real-time Phishing & Cyber Threat Intelligence</p>
          </div>
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-sm" role="alert">
              <p className="font-bold">Connection Error</p>
              <p>{error}</p>
            </div>
          )}
        </header>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard 
            title="Total Analyzed" 
            value={stats?.total_emails_analyzed || 0} 
            icon={<Mail className="h-6 w-6 text-blue-500" />} 
            trend="Live monitoring active"
          />
          <StatCard 
            title="Phishing Detected" 
            value={stats?.total_phishing_detected || 0} 
            icon={<AlertTriangle className="h-6 w-6 text-amber-500" />} 
            trend="Threats intercepted"
            alert={stats?.total_phishing_detected > 0}
          />
          <StatCard 
            title="Total Blocked" 
            value={stats?.total_blocked || 0} 
            icon={<ShieldAlert className="h-6 w-6 text-red-500" />} 
            trend="Actions taken automatically"
            alert={stats?.total_blocked > 0}
          />
          <StatCard 
            title="Detection Rate" 
            value={`${(stats?.detection_rate * 100 || 0).toFixed(0)}%`} 
            icon={<Activity className="h-6 w-6 text-emerald-500" />} 
            trend="Current efficacy"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Timeline Chart */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-6">Threat Detection Timeline</h2>
            <div className="flex-1 w-full" style={{ minHeight: '300px' }}>
              {stats?.timeline && stats.timeline.length > 0 ? (
                <Line options={lineOptions} data={lineData} />
              ) : (
                <div className="flex h-full items-center justify-center text-slate-400">
                  Waiting for detection data...
                </div>
              )}
            </div>
          </div>

          {/* Threat Distribution */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-6">Attack Type Distribution</h2>
            <div className="flex-1 w-full" style={{ minHeight: '300px' }}>
              {stats?.top_threats && stats.top_threats.length > 0 ? (
                <Pie options={pieOptions} data={pieData} />
              ) : (
                <div className="flex h-full items-center justify-center text-slate-400">
                  No threats detected yet.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Audit Trail History */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 bg-slate-50/50">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold text-slate-800">Live Audit Trail</h2>
              <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Live Tracking
              </span>
            </div>
            
            <div className="flex bg-slate-200 p-1 rounded-lg">
              {['ALL', 'SAFE', 'SPAM', 'PHISHING'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    filter === f 
                      ? 'bg-white text-slate-900 shadow-sm' 
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white text-slate-500 text-sm border-b border-slate-100">
                  <th className="px-6 py-4 font-medium">Timestamp</th>
                  <th className="px-6 py-4 font-medium">Sender</th>
                  <th className="px-6 py-4 font-medium">Subject</th>
                  <th className="px-6 py-4 font-medium">Risk Score</th>
                  <th className="px-6 py-4 font-medium">Threat Category</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {(() => {
                  const filteredHistory = history.filter(record => {
                    if (filter === 'ALL') return true;
                    if (filter === 'SAFE') return record.risk_score < 40;
                    if (filter === 'SPAM') return record.threat_category === 'spam';
                    if (filter === 'PHISHING') return record.risk_score >= 70 || record.threat_category === 'phishing';
                    return true;
                  });

                  return filteredHistory.length > 0 ? (
                    filteredHistory.map((record) => (
                      <tr key={record.id} className="border-b border-slate-50 hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 text-slate-500 whitespace-nowrap">
                        {format(new Date(record.timestamp), 'MMM dd, HH:mm:ss')}
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-800 truncate max-w-xs" title={record.sender}>
                        {record.sender}
                      </td>
                      <td className="px-6 py-4 text-slate-600 truncate max-w-xs" title={record.subject}>
                        {record.subject || 'No Subject'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                record.risk_score >= 70 ? 'bg-red-500' : 
                                record.risk_score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
                              }`}
                              style={{ width: `${record.risk_score}%` }}
                            ></div>
                          </div>
                          <span className="font-semibold">{record.risk_score}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {record.threat_category ? (
                          <span className="capitalize px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                            {record.threat_category.replace('_', ' ')}
                          </span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {(() => {
                          const action = record.suggested_action || (record.risk_score >= 75 ? 'block' : record.risk_score >= 50 ? 'warn' : 'allow');
                          if (action === 'block') {
                            return (
                              <span className="inline-flex items-center gap-1 text-red-600 font-medium bg-red-50 px-2.5 py-1 rounded-md text-xs">
                                <ShieldAlert className="w-3 h-3" />
                                BLOCKED
                              </span>
                            );
                          } else if (action === 'warn') {
                            return (
                              <span className="inline-flex items-center gap-1 text-amber-600 font-medium bg-amber-50 px-2.5 py-1 rounded-md text-xs">
                                <AlertTriangle className="w-3 h-3" />
                                WARNING
                              </span>
                            );
                          } else {
                            return (
                              <span className="inline-flex items-center gap-1 text-emerald-600 font-medium bg-emerald-50 px-2.5 py-1 rounded-md text-xs">
                                <ShieldCheck className="w-3 h-3" />
                                SAFE
                              </span>
                            );
                          }
                        })()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-500 bg-slate-50/50">
                      {filter === 'ALL' 
                        ? 'No emails analyzed yet. Open an email in Gmail with the extension enabled to see live data.'
                        : `No ${filter.toLowerCase()} emails detected yet.`}
                    </td>
                  </tr>
                );
                })()}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Reusable Summary Card Component
function StatCard({ title, value, icon, trend, alert = false }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border p-6 flex flex-col justify-between transition-all hover:shadow-md ${alert ? 'border-red-100' : 'border-slate-100'}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-500 text-sm font-medium mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-slate-800">{value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${alert ? 'bg-red-50' : 'bg-slate-50'}`}>
          {icon}
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-4 flex items-center gap-1">
        {trend}
      </p>
    </div>
  );
}
