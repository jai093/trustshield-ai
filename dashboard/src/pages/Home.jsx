import React, { useEffect, useState } from 'react';
import { 
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, 
  Title, Tooltip as ChartTooltip, Legend as ChartLegend, Filler, ArcElement 
} from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';
import { 
  ShieldAlert, ShieldCheck, Mail, Activity, AlertTriangle, Moon, Sun, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { format, addMonths, subMonths } from 'date-fns';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, ChartTooltip, ChartLegend, Filler, ArcElement
);

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

export default function Home() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [totalHistory, setTotalHistory] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [graphMonth, setGraphMonth] = useState(new Date());

  const fetchDashboardData = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-User-Id': 'dashboard-user',
      };
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const [statsRes, historyRes] = await Promise.all([
        fetch(`${apiUrl}/api/dashboard/stats`, { headers }),
        fetch(`${apiUrl}/api/history?limit=10&offset=${(historyPage - 1) * 10}`, { headers })
      ]);
      
      if (!statsRes.ok || !historyRes.ok) throw new Error('Failed to fetch dashboard data');
      
      const statsData = await statsRes.json();
      const historyData = await historyRes.json();
      
      setStats(statsData?.data ?? null);
      setHistory(historyData?.data ?? []);
      setTotalHistory(historyData?.total ?? 0);
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
  }, [historyPage]); // Re-run when page changes

  // Apply dark class to body if necessary
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  if (loading && !stats) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Filter timeline for current month
  const currentMonthStr = format(graphMonth, 'yyyy-MM');
  const filteredTimeline = (stats?.timeline || []).filter(t => t.date.startsWith(currentMonthStr));

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { color: isDarkMode ? '#cbd5e1' : '#475569' } },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      y: { beginAtZero: true, grid: { color: isDarkMode ? '#334155' : '#e2e8f0' }, ticks: { color: isDarkMode ? '#cbd5e1' : '#475569' } },
      x: { grid: { display: false }, ticks: { color: isDarkMode ? '#cbd5e1' : '#475569' } }
    }
  };

  const lineData = {
    labels: filteredTimeline.map(t => t.date) || [],
    datasets: [
      {
        label: 'Phishing Detected',
        data: filteredTimeline.map(t => t.phishing) || [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.3)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Total Analyzed',
        data: filteredTimeline.map(t => t.total) || [],
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
      legend: { position: 'right', labels: { color: isDarkMode ? '#cbd5e1' : '#475569' } }
    }
  };

  const pieData = {
    labels: stats?.top_threats?.map(t => t.threat.replace('_', ' ').toUpperCase()) || [],
    datasets: [
      {
        data: stats?.top_threats?.map(t => t.count) || [],
        backgroundColor: COLORS,
        borderColor: isDarkMode ? '#1e293b' : '#ffffff',
        borderWidth: 2,
      }
    ]
  };

  return (
    <div className={`min-h-screen p-6 md:p-8 lg:p-10 font-sans transition-colors duration-200 ${isDarkMode ? 'bg-slate-900 text-slate-200' : 'bg-slate-50 text-slate-800'}`}>
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className={`text-3xl font-bold tracking-tight flex items-center gap-3 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
              <img src="/trustshieldlogo.png" alt="TrustShield AI" className="h-12 w-auto object-contain" />
              TrustShield AI Dashboard
            </h1>
            <p className="text-slate-500 mt-1">Real-time Phishing & Cyber Threat Intelligence</p>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`p-2.5 rounded-full transition-colors ${isDarkMode ? 'bg-slate-800 hover:bg-slate-700 text-amber-400' : 'bg-white hover:bg-slate-100 text-slate-600 shadow-sm border border-slate-200'}`}
              title="Toggle Theme"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
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
            isDark={isDarkMode}
          />
          <StatCard 
            title="Phishing Detected" 
            value={stats?.total_phishing_detected || 0} 
            icon={<AlertTriangle className="h-6 w-6 text-amber-500" />} 
            trend="Threats intercepted"
            alert={stats?.total_phishing_detected > 0}
            isDark={isDarkMode}
          />
          <StatCard 
            title="Total Blocked" 
            value={stats?.total_blocked || 0} 
            icon={<ShieldAlert className="h-6 w-6 text-red-500" />} 
            trend="Actions taken automatically"
            alert={stats?.total_blocked > 0}
            isDark={isDarkMode}
          />
          <StatCard 
            title="Detection Rate" 
            value={`${(stats?.detection_rate * 100 || 0).toFixed(0)}%`} 
            icon={<Activity className="h-6 w-6 text-emerald-500" />} 
            trend="Current efficacy"
            isDark={isDarkMode}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Timeline Chart */}
          <div className={`p-6 rounded-xl shadow-sm border flex flex-col ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'}`}>
            <div className="flex justify-between items-center mb-6">
              <h2 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>Threat Detection Timeline</h2>
              <div className="flex items-center gap-3">
                <button onClick={() => setGraphMonth(subMonths(graphMonth, 1))} className={`p-1.5 rounded-md ${isDarkMode ? 'hover:bg-slate-700 text-slate-300' : 'hover:bg-slate-100 text-slate-600'}`}>
                  <ChevronLeft size={18} />
                </button>
                <span className={`text-sm font-medium ${isDarkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  {format(graphMonth, 'MMMM yyyy')}
                </span>
                <button onClick={() => setGraphMonth(addMonths(graphMonth, 1))} className={`p-1.5 rounded-md ${isDarkMode ? 'hover:bg-slate-700 text-slate-300' : 'hover:bg-slate-100 text-slate-600'}`}>
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
            <div className="flex-1 w-full" style={{ minHeight: '300px' }}>
              {filteredTimeline.length > 0 ? (
                <Line options={lineOptions} data={lineData} />
              ) : (
                <div className={`flex h-full items-center justify-center ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  No detection data for this month.
                </div>
              )}
            </div>
          </div>

          {/* Threat Distribution */}
          <div className={`p-6 rounded-xl shadow-sm border flex flex-col ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'}`}>
            <h2 className={`text-lg font-semibold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>Attack Type Distribution</h2>
            <div className="flex-1 w-full" style={{ minHeight: '300px' }}>
              {stats?.top_threats && stats.top_threats.length > 0 ? (
                <Pie options={pieOptions} data={pieData} />
              ) : (
                <div className={`flex h-full items-center justify-center ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  No threats detected yet.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Audit Trail History */}
        <div className={`rounded-xl shadow-sm border overflow-hidden ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'}`}>
          <div className={`p-6 border-b flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 ${isDarkMode ? 'border-slate-700 bg-slate-800' : 'border-slate-100 bg-slate-50/50'}`}>
            <div className="flex items-center gap-3">
              <h2 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>Live Audit Trail</h2>
              <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Live Tracking
              </span>
            </div>
            
            <div className={`flex p-1 rounded-lg ${isDarkMode ? 'bg-slate-900' : 'bg-slate-200'}`}>
              {['ALL', 'SAFE', 'SPAM', 'PHISHING'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    filter === f 
                      ? (isDarkMode ? 'bg-slate-700 text-white shadow-sm' : 'bg-white text-slate-900 shadow-sm') 
                      : (isDarkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900')
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
                <tr className={`text-sm border-b ${isDarkMode ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-white text-slate-500 border-slate-100'}`}>
                  <th className="px-6 py-4 font-medium">Timestamp</th>
                  <th className="px-6 py-4 font-medium">Sender</th>
                  <th className="px-6 py-4 font-medium w-1/3">Subject</th>
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
                      <tr key={record.id} className={`border-b transition-colors ${isDarkMode ? 'border-slate-700 hover:bg-slate-700/50' : 'border-slate-50 hover:bg-slate-50/80'}`}>
                        <td className={`px-6 py-4 whitespace-nowrap ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                        {format(new Date(record.timestamp), 'MMM dd, HH:mm:ss')}
                      </td>
                      <td className={`px-6 py-4 font-medium max-w-[200px] break-words ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>
                        {record.sender}
                      </td>
                      <td className={`px-6 py-4 break-words ${isDarkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                        {record.subject || 'No Subject'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className={`w-16 h-2 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
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
                          <span className={`capitalize px-2.5 py-1 rounded-md text-xs font-medium ${isDarkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-700'}`}>
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
                              <span className={`inline-flex items-center gap-1 font-medium px-2.5 py-1 rounded-md text-xs ${isDarkMode ? 'bg-red-900/30 text-red-400' : 'bg-red-50 text-red-600'}`}>
                                <ShieldAlert className="w-3 h-3" />
                                BLOCKED
                              </span>
                            );
                          } else if (action === 'warn') {
                            return (
                              <span className={`inline-flex items-center gap-1 font-medium px-2.5 py-1 rounded-md text-xs ${isDarkMode ? 'bg-amber-900/30 text-amber-400' : 'bg-amber-50 text-amber-600'}`}>
                                <AlertTriangle className="w-3 h-3" />
                                WARNING
                              </span>
                            );
                          } else {
                            return (
                              <span className={`inline-flex items-center gap-1 font-medium px-2.5 py-1 rounded-md text-xs ${isDarkMode ? 'bg-emerald-900/30 text-emerald-400' : 'bg-emerald-50 text-emerald-600'}`}>
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
                    <td colSpan={6} className={`px-6 py-12 text-center ${isDarkMode ? 'text-slate-500 bg-slate-800' : 'text-slate-500 bg-slate-50/50'}`}>
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
          {/* Pagination Controls */}
          {totalHistory > 10 && (
            <div className={`p-4 border-t flex justify-between items-center ${isDarkMode ? 'border-slate-700 bg-slate-800' : 'border-slate-100 bg-white'}`}>
              <div className={`text-sm ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                Showing {(historyPage - 1) * 10 + 1} to {Math.min(historyPage * 10, totalHistory)} of {totalHistory} emails
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => setHistoryPage(p => Math.max(1, p - 1))}
                  disabled={historyPage === 1}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    historyPage === 1 
                      ? (isDarkMode ? 'bg-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-50 text-slate-400 cursor-not-allowed') 
                      : (isDarkMode ? 'bg-slate-700 text-slate-200 hover:bg-slate-600' : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200')
                  }`}
                >
                  Previous
                </button>
                <button 
                  onClick={() => setHistoryPage(p => p + 1)}
                  disabled={historyPage * 10 >= totalHistory}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    historyPage * 10 >= totalHistory 
                      ? (isDarkMode ? 'bg-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-50 text-slate-400 cursor-not-allowed') 
                      : (isDarkMode ? 'bg-slate-700 text-slate-200 hover:bg-slate-600' : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200')
                  }`}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Reusable Summary Card Component
function StatCard({ title, value, icon, trend, alert = false, isDark = false }) {
  const bgClass = isDark ? 'bg-slate-800' : 'bg-white';
  const borderClass = isDark 
    ? (alert ? 'border-red-900/50' : 'border-slate-700')
    : (alert ? 'border-red-100' : 'border-slate-100');
  const titleColor = isDark ? 'text-slate-400' : 'text-slate-500';
  const valueColor = isDark ? 'text-white' : 'text-slate-800';
  const iconBg = isDark 
    ? (alert ? 'bg-red-900/30' : 'bg-slate-900')
    : (alert ? 'bg-red-50' : 'bg-slate-50');
  const trendColor = isDark ? 'text-slate-500' : 'text-slate-400';

  return (
    <div className={`${bgClass} rounded-xl shadow-sm border p-6 flex flex-col justify-between transition-all hover:shadow-md ${borderClass}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className={`${titleColor} text-sm font-medium mb-1`}>{title}</p>
          <h3 className={`text-3xl font-bold ${valueColor}`}>{value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${iconBg}`}>
          {icon}
        </div>
      </div>
      <p className={`text-xs ${trendColor} mt-4 flex items-center gap-1`}>
        {trend}
      </p>
    </div>
  );
}
