/**
 * API service — centralized Axios client for all backend calls.
 */

import axios from 'axios';
import type {
  AuthToken,
  LoginCredentials,
  EventListResponse,
  EventCreatePayload,
  EventCreateResponse,
  SecurityEvent,
  AlertListResponse,
  Alert,
  DashboardStats,
  DashboardTimeline,
  HealthStatus,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('secureops_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('secureops_token');
      localStorage.removeItem('secureops_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// --- Auth ---
export const authAPI = {
  login: (credentials: LoginCredentials) =>
    api.post<AuthToken>('/api/auth/login', credentials).then((r) => r.data),

  register: (data: { username: string; email: string; password: string; role?: string }) =>
    api.post<AuthToken>('/api/auth/register', data).then((r) => r.data),
};

// --- Events ---
export const eventsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    severity?: string;
    event_type?: string;
    status?: string;
    source_ip?: string;
  }) => api.get<EventListResponse>('/api/events', { params }).then((r) => r.data),

  get: (id: string) =>
    api.get<SecurityEvent>(`/api/events/${id}`).then((r) => r.data),

  create: (data: EventCreatePayload) =>
    api.post<EventCreateResponse>('/api/events', data).then((r) => r.data),
};

// --- Alerts ---
export const alertsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    severity?: string;
    status?: string;
  }) => api.get<AlertListResponse>('/api/alerts', { params }).then((r) => r.data),

  get: (id: string) =>
    api.get<Alert>(`/api/alerts/${id}`).then((r) => r.data),

  updateStatus: (id: string, status: string) =>
    api.patch<Alert>(`/api/alerts/${id}`, { status }).then((r) => r.data),
};

// --- Dashboard ---
export const dashboardAPI = {
  stats: () =>
    api.get<DashboardStats>('/api/dashboard/stats').then((r) => r.data),

  timeline: () =>
    api.get<DashboardTimeline>('/api/dashboard/timeline').then((r) => r.data),
};

// --- Health ---
export const healthAPI = {
  check: () => api.get<HealthStatus>('/health').then((r) => r.data),
};

export default api;
