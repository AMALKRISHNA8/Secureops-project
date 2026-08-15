/**
 * Event detail page — full event info + associated alerts.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, Server, Globe, FileText } from 'lucide-react';
import { eventsAPI } from '../services/api';
import type { SecurityEvent } from '../types';
import SeverityBadge from '../components/SeverityBadge';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [event, setEvent] = useState<SecurityEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    loadEvent(id);
  }, [id]);

  const loadEvent = async (eventId: string) => {
    try {
      const data = await eventsAPI.get(eventId);
      setEvent(data);
    } catch {
      setError('Event not found');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading event details..." />;

  if (error || !event) {
    return (
      <div className="text-center py-16 animate-fade-in">
        <p className="text-gray-400 text-lg">{error || 'Event not found'}</p>
        <button onClick={() => navigate('/events')} className="btn-primary mt-4">
          Back to Events
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button + header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/events')}
          className="p-2 hover:bg-surface-50 rounded-lg transition-colors text-gray-400 hover:text-white"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-white">Event Details</h1>
          <p className="text-xs text-gray-500 font-mono mt-0.5">ID: {event.id}</p>
        </div>
        <SeverityBadge severity={event.severity} />
        <StatusBadge status={event.status} />
      </div>

      {/* Event info cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyber-400" />
            Event Information
          </h3>
          <div className="space-y-3">
            <InfoRow label="Event Type" value={event.event_type.replace(/_/g, ' ')} />
            <InfoRow label="Source" value={event.source} />
            <InfoRow label="Description" value={event.description || 'N/A'} />
            <InfoRow
              label="Timestamp"
              value={new Date(event.timestamp).toLocaleString()}
            />
            <InfoRow
              label="Created"
              value={new Date(event.created_at).toLocaleString()}
            />
          </div>
        </div>

        <div className="glass-card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <Globe className="w-4 h-4 text-cyber-400" />
            Network Information
          </h3>
          <div className="space-y-3">
            <InfoRow label="Source IP" value={event.source_ip || 'N/A'} mono />
            <InfoRow label="Destination IP" value={event.destination_ip || 'N/A'} mono />
          </div>

          {event.raw_data && Object.keys(event.raw_data).length > 0 && (
            <>
              <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2 pt-2">
                <Server className="w-4 h-4 text-cyber-400" />
                Raw Data
              </h3>
              <pre className="bg-surface-300 rounded-lg p-3 text-xs text-gray-300 font-mono overflow-x-auto max-h-48">
                {JSON.stringify(event.raw_data, null, 2)}
              </pre>
            </>
          )}
        </div>
      </div>

      {/* Associated Alerts */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-amber-400" />
          Associated Alerts ({event.alerts.length})
        </h3>
        {event.alerts.length === 0 ? (
          <p className="text-sm text-gray-500 py-6 text-center">
            No alerts generated for this event
          </p>
        ) : (
          <div className="space-y-3">
            {event.alerts.map((alert) => (
              <div
                key={alert.id}
                className="p-4 rounded-lg bg-surface-200/50 border border-gray-800/50"
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-200">{alert.title}</h4>
                  <div className="flex items-center gap-2 shrink-0 ml-3">
                    <SeverityBadge severity={alert.severity} showIcon={false} />
                    <StatusBadge status={alert.status} />
                  </div>
                </div>
                <p className="text-xs text-gray-400">{alert.description}</p>
                <p className="text-xs text-gray-500 mt-2">
                  Rule: {alert.rule_name.replace(/_/g, ' ')} •{' '}
                  {new Date(alert.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoRow({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex justify-between items-start gap-4">
      <span className="text-xs text-gray-500 shrink-0 w-28">{label}</span>
      <span
        className={`text-sm text-gray-300 text-right ${mono ? 'font-mono text-cyan-400' : ''}`}
      >
        {value}
      </span>
    </div>
  );
}
