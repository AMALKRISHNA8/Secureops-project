/**
 * Alerts page — view and manage security alerts.
 */

import { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, AlertTriangle, CheckCircle, Search as SearchIcon } from 'lucide-react';
import { alertsAPI } from '../services/api';
import type { AlertListResponse, Alert } from '../types';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const STATUS_OPTIONS = ['open', 'investigating', 'resolved'] as const;

export default function AlertsPage() {
  const [data, setData] = useState<AlertListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const result = await alertsAPI.list({
        page,
        page_size: 15,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });
      setData(result);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  }, [page, severityFilter, statusFilter]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  useEffect(() => {
    setPage(1);
  }, [severityFilter, statusFilter]);

  const handleStatusChange = async (alertId: string, newStatus: string) => {
    setUpdatingId(alertId);
    try {
      await alertsAPI.updateStatus(alertId, newStatus);
      await loadAlerts();
    } catch (err) {
      console.error('Failed to update alert:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Alerts</h1>
        <p className="text-sm text-gray-400 mt-1">
          {data ? `${data.total.toLocaleString()} total alerts` : 'Loading...'}
        </p>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap gap-3 items-center">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="input-field w-auto min-w-[140px] text-sm"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field w-auto min-w-[160px] text-sm"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Alerts list */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <LoadingSpinner text="Loading alerts..." />
        ) : (data?.alerts.length ?? 0) === 0 ? (
          <div className="py-16 text-center">
            <CheckCircle className="w-10 h-10 text-emerald-500/50 mx-auto mb-3" />
            <p className="text-gray-400">No alerts found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Alert</th>
                  <th>Rule</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {data?.alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td className="max-w-xs">
                      <p className="text-sm font-medium text-gray-200 truncate">
                        {alert.title}
                      </p>
                      <p className="text-xs text-gray-500 truncate mt-0.5">
                        {alert.description}
                      </p>
                    </td>
                    <td className="text-sm text-gray-400 whitespace-nowrap">
                      {alert.rule_name.replace(/_/g, ' ')}
                    </td>
                    <td>
                      <SeverityBadge severity={alert.severity} showIcon={false} />
                    </td>
                    <td>
                      <StatusBadge status={alert.status} />
                    </td>
                    <td className="text-xs text-gray-400 font-mono whitespace-nowrap">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                    <td>
                      <select
                        value={alert.status}
                        onChange={(e) => handleStatusChange(alert.id, e.target.value)}
                        disabled={updatingId === alert.id}
                        className="input-field text-xs py-1.5 px-2 w-[130px]"
                      >
                        {STATUS_OPTIONS.map((s) => (
                          <option key={s} value={s}>
                            {s.charAt(0).toUpperCase() + s.slice(1)}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-800/50">
            <p className="text-xs text-gray-500">
              Page {data.page} of {data.total_pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-ghost py-1.5 px-2.5 text-xs disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page >= data.total_pages}
                className="btn-ghost py-1.5 px-2.5 text-xs disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
