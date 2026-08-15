/**
 * Events page — searchable, filterable security events table.
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { eventsAPI } from '../services/api';
import type { SecurityEvent, EventListResponse } from '../types';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EventsPage() {
  const [data, setData] = useState<EventListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const navigate = useNavigate();

  const loadEvents = useCallback(async () => {
    setLoading(true);
    try {
      const result = await eventsAPI.list({
        page,
        page_size: 15,
        search: search || undefined,
        severity: severityFilter || undefined,
        event_type: typeFilter || undefined,
      });
      setData(result);
    } catch (err) {
      console.error('Failed to load events:', err);
    } finally {
      setLoading(false);
    }
  }, [page, search, severityFilter, typeFilter]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  // Debounced search
  useEffect(() => {
    setPage(1);
  }, [search, severityFilter, typeFilter]);

  const clearFilters = () => {
    setSearch('');
    setSeverityFilter('');
    setTypeFilter('');
    setPage(1);
  };

  const hasFilters = search || severityFilter || typeFilter;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Security Events</h1>
        <p className="text-sm text-gray-400 mt-1">
          {data ? `${data.total.toLocaleString()} total events` : 'Loading...'}
        </p>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search events..."
              className="input-field pl-10 text-sm"
            />
          </div>

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
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input-field w-auto min-w-[160px] text-sm"
          >
            <option value="">All Types</option>
            <option value="failed_login">Failed Login</option>
            <option value="successful_login">Successful Login</option>
            <option value="suspicious_login">Suspicious Login</option>
            <option value="port_scan">Port Scan</option>
            <option value="port_activity">Port Activity</option>
            <option value="privilege_escalation">Privilege Escalation</option>
            <option value="privilege_change">Privilege Change</option>
            <option value="malware_detected">Malware Detected</option>
            <option value="network_anomaly">Network Anomaly</option>
            <option value="policy_violation">Policy Violation</option>
            <option value="unauthorized_access">Unauthorized Access</option>
          </select>

          {hasFilters && (
            <button onClick={clearFilters} className="btn-ghost text-sm py-2 px-3 flex items-center gap-1.5">
              <X className="w-3.5 h-3.5" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <LoadingSpinner text="Loading events..." />
        ) : (data?.events.length ?? 0) === 0 ? (
          <div className="py-16 text-center">
            <Filter className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No events found</p>
            {hasFilters && (
              <p className="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Source</th>
                  <th>Source IP</th>
                  <th>Event Type</th>
                  <th>Severity</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data?.events.map((event) => (
                  <tr
                    key={event.id}
                    onClick={() => navigate(`/events/${event.id}`)}
                    className="cursor-pointer"
                  >
                    <td className="text-gray-400 font-mono text-xs whitespace-nowrap">
                      {new Date(event.timestamp).toLocaleString()}
                    </td>
                    <td className="text-gray-300 text-sm">{event.source}</td>
                    <td className="text-cyan-400 font-mono text-xs">
                      {event.source_ip || '—'}
                    </td>
                    <td className="text-gray-300 text-sm">
                      {event.event_type.replace(/_/g, ' ')}
                    </td>
                    <td>
                      <SeverityBadge severity={event.severity} showIcon={false} />
                    </td>
                    <td>
                      <StatusBadge status={event.status} />
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
