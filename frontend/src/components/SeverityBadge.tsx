/**
 * Severity badge component with color coding.
 */

import type { SeverityLevel } from '../types';

const severityConfig: Record<SeverityLevel, { class: string; icon: string }> = {
  critical: { class: 'severity-critical', icon: '🔴' },
  high: { class: 'severity-high', icon: '🟠' },
  medium: { class: 'severity-medium', icon: '🟡' },
  low: { class: 'severity-low', icon: '🟢' },
};

interface Props {
  severity: SeverityLevel;
  showIcon?: boolean;
}

export default function SeverityBadge({ severity, showIcon = true }: Props) {
  const config = severityConfig[severity] || severityConfig.low;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide rounded-md border ${config.class}`}
    >
      {showIcon && <span className="text-[10px]">{config.icon}</span>}
      {severity}
    </span>
  );
}
