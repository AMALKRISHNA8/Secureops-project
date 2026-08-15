/**
 * Status badge component for alert and event statuses.
 */

interface Props {
  status: string;
}

const statusClasses: Record<string, string> = {
  open: 'status-open',
  investigating: 'status-investigating',
  resolved: 'status-resolved',
  new: 'status-new',
  reviewed: 'status-reviewed',
  escalated: 'status-escalated',
  closed: 'status-closed',
};

export default function StatusBadge({ status }: Props) {
  const cls = statusClasses[status] || 'bg-gray-500/15 text-gray-400 border-gray-500/30';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 text-xs font-semibold uppercase tracking-wide rounded-md border ${cls}`}
    >
      {status}
    </span>
  );
}
