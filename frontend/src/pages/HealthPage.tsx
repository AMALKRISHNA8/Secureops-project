/**
 * System Health page.
 */

import { useState, useEffect } from 'react';
import { Activity, Database, Server, Clock, RefreshCw } from 'lucide-react';
import { healthAPI } from '../services/api';
import type { HealthStatus } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadHealth = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const data = await healthAPI.check();
      setHealth(data);
    } catch (err) {
      console.error('Health check failed:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadHealth();
    const interval = setInterval(() => loadHealth(), 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner text="Checking system health..." />;

  const statusColor = health?.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400';
  const statusBg = health?.status === 'healthy' ? 'bg-emerald-500/15' : 'bg-amber-500/15';
  const dbColor = health?.database === 'healthy' ? 'text-emerald-400' : 'text-red-400';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Health</h1>
          <p className="text-sm text-gray-400 mt-1">Infrastructure status monitoring</p>
        </div>
        <button
          onClick={() => loadHealth(true)}
          disabled={refreshing}
          className="btn-ghost text-sm flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Overall status */}
      <div className="glass-card p-6 text-center">
        <div className={`inline-flex p-4 rounded-2xl ${statusBg} mb-4`}>
          <Activity className={`w-8 h-8 ${statusColor}`} />
        </div>
        <h2 className={`text-2xl font-bold capitalize ${statusColor}`}>
          System {health?.status}
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Last checked: {health?.timestamp ? new Date(health.timestamp).toLocaleString() : 'N/A'}
        </p>
      </div>

      {/* Health details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <HealthCard
          icon={<Server className="w-5 h-5 text-cyber-400" />}
          title="API Status"
          value={health?.api || 'unknown'}
          valueColor={health?.api === 'online' ? 'text-emerald-400' : 'text-red-400'}
        />
        <HealthCard
          icon={<Database className="w-5 h-5 text-cyber-400" />}
          title="Database"
          value={health?.database || 'unknown'}
          valueColor={dbColor}
        />
        <HealthCard
          icon={<Activity className="w-5 h-5 text-cyber-400" />}
          title="Version"
          value={`v${health?.version || '?'}`}
          valueColor="text-gray-200"
        />
        <HealthCard
          icon={<Clock className="w-5 h-5 text-cyber-400" />}
          title="Uptime"
          value={health?.uptime || 'N/A'}
          valueColor="text-gray-200"
        />
      </div>
    </div>
  );
}

function HealthCard({
  icon,
  title,
  value,
  valueColor,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  valueColor: string;
}) {
  return (
    <div className="glass-card-hover p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 bg-cyber-600/10 rounded-lg">{icon}</div>
        <span className="text-sm text-gray-400">{title}</span>
      </div>
      <p className={`text-xl font-bold capitalize ${valueColor}`}>{value}</p>
    </div>
  );
}
