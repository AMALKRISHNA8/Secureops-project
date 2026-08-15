/**
 * Dashboard page — main security overview.
 */

import { useState, useEffect } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import {
  Shield, AlertTriangle, AlertOctagon, Activity,
  TrendingUp, Clock,
} from 'lucide-react';
import { dashboardAPI, alertsAPI } from '../services/api';
import type { DashboardStats, DashboardTimeline, Alert } from '../types';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#ff1744',
  high: '#ff9100',
  medium: '#ffab00',
  low: '#00e676',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeline, setTimeline] = useState<DashboardTimeline | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsData, timelineData, alertsData] = await Promise.all([
        dashboardAPI.stats(),
        dashboardAPI.timeline(),
        alertsAPI.list({ page: 1, page_size: 5 }),
      ]);
      setStats(statsData);
      setTimeline(timelineData);
      setRecentAlerts(alertsData.alerts);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading dashboard..." />;

  const statCards = [
    {
      label: 'Total Events',
      value: stats?.total_events ?? 0,
      icon: Shield,
      color: 'text-cyber-400',
      bgColor: 'bg-cyber-600/10',
    },
    {
      label: 'Active Alerts',
      value: (stats?.open_alerts ?? 0) + (stats?.investigating_alerts ?? 0),
      icon: AlertTriangle,
      color: 'text-amber-400',
      bgColor: 'bg-amber-600/10',
    },
    {
      label: 'Critical Alerts',
      value: stats?.critical_alerts ?? 0,
      icon: AlertOctagon,
      color: 'text-red-400',
      bgColor: 'bg-red-600/10',
    },
    {
      label: 'Events Today',
      value: stats?.events_today ?? 0,
      icon: TrendingUp,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-600/10',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">Real-time threat monitoring overview</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Clock className="w-3.5 h-3.5" />
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="glass-card-hover p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="stat-value">{card.value.toLocaleString()}</p>
                <p className="stat-label">{card.label}</p>
              </div>
              <div className={`p-2.5 rounded-lg ${card.bgColor}`}>
                <card.icon className={`w-5 h-5 ${card.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 glass-card p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Event Timeline (30 days)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={timeline?.timeline ?? []}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2332" />
              <XAxis
                dataKey="date"
                tick={{ fill: '#6b7280', fontSize: 10 }}
                tickFormatter={(val) => val.slice(5)}
                stroke="#1a2332"
              />
              <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} stroke="#1a2332" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141c27',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#e5e7eb',
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#00d4ff"
                fill="url(#colorCount)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={timeline?.severity_distribution ?? []}
                dataKey="count"
                nameKey="severity"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={3}
                stroke="none"
              >
                {(timeline?.severity_distribution ?? []).map((entry) => (
                  <Cell
                    key={entry.severity}
                    fill={SEVERITY_COLORS[entry.severity] || '#6b7280'}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141c27',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#e5e7eb',
                  fontSize: 12,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-3 justify-center mt-2">
            {(timeline?.severity_distribution ?? []).map((entry) => (
              <div key={entry.severity} className="flex items-center gap-1.5 text-xs">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: SEVERITY_COLORS[entry.severity] }}
                />
                <span className="text-gray-400 capitalize">{entry.severity}</span>
                <span className="text-gray-500">({entry.count})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Alerts */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Recent Alerts</h3>
          {recentAlerts.length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No alerts found</p>
          ) : (
            <div className="space-y-3">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start justify-between p-3 rounded-lg bg-surface-200/50 border border-gray-800/50 hover:border-gray-700/50 transition-colors"
                >
                  <div className="min-w-0 flex-1 mr-3">
                    <p className="text-sm font-medium text-gray-200 truncate">
                      {alert.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {alert.rule_name.replace(/_/g, ' ')} •{' '}
                      {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <SeverityBadge severity={alert.severity} showIcon={false} />
                    <StatusBadge status={alert.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Source IPs */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Top Source IPs</h3>
          {(timeline?.top_source_ips ?? []).length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart
                data={timeline?.top_source_ips?.slice(0, 6) ?? []}
                layout="vertical"
                margin={{ left: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2332" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 10 }} stroke="#1a2332" />
                <YAxis
                  dataKey="source_ip"
                  type="category"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  width={120}
                  stroke="#1a2332"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#141c27',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#e5e7eb',
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="count" fill="#00d4ff" radius={[0, 4, 4, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
