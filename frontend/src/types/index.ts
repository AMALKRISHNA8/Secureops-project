/**
 * TypeScript type definitions for SecureOps.
 */

// --- Auth ---
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'analyst' | 'admin';
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

// --- Events ---
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';
export type EventStatus = 'new' | 'reviewed' | 'escalated' | 'closed';
export type AlertStatus = 'open' | 'investigating' | 'resolved';

export interface SecurityEvent {
  id: string;
  timestamp: string;
  source: string;
  source_ip: string | null;
  destination_ip: string | null;
  event_type: string;
  description: string | null;
  severity: SeverityLevel;
  status: EventStatus;
  raw_data: Record<string, unknown> | null;
  created_at: string;
  alerts: Alert[];
}

export interface EventCreatePayload {
  source: string;
  source_ip?: string;
  destination_ip?: string;
  event_type: string;
  description?: string;
  severity?: SeverityLevel;
  raw_data?: Record<string, unknown>;
}

export interface EventListResponse {
  events: SecurityEvent[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface EventCreateResponse {
  event: SecurityEvent;
  alerts_generated: number;
}

// --- Alerts ---
export interface Alert {
  id: string;
  event_id: string;
  rule_name: string;
  severity: SeverityLevel;
  title: string;
  description: string | null;
  status: AlertStatus;
  created_at: string;
  resolved_at: string | null;
  event?: {
    id: string;
    source: string;
    source_ip: string | null;
    event_type: string;
    severity: SeverityLevel;
    timestamp: string;
  };
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// --- Dashboard ---
export interface DashboardStats {
  total_events: number;
  total_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  open_alerts: number;
  investigating_alerts: number;
  resolved_alerts: number;
  events_today: number;
}

export interface TimelineEntry {
  date: string;
  count: number;
}

export interface SeverityCount {
  severity: string;
  count: number;
}

export interface TopSourceIP {
  source_ip: string;
  count: number;
}

export interface TopEventType {
  event_type: string;
  count: number;
}

export interface DashboardTimeline {
  timeline: TimelineEntry[];
  severity_distribution: SeverityCount[];
  top_source_ips: TopSourceIP[];
  top_event_types: TopEventType[];
}

// --- Health ---
export interface HealthStatus {
  status: string;
  api: string;
  database: string;
  version: string;
  uptime: string;
  uptime_seconds: number;
  timestamp: string;
}
