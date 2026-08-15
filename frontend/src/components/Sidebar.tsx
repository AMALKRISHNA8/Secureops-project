/**
 * Sidebar navigation component with cybersecurity styling.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Shield,
  AlertTriangle,
  Activity,
  LogOut,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/events', icon: Shield, label: 'Events' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/health', icon: Activity, label: 'System Health' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-surface-100 border-r border-gray-800/60 flex flex-col z-50">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-800/60">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyber-600/20 rounded-lg">
            <ShieldCheck className="w-6 h-6 text-cyber-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">SecureOps</h1>
            <p className="text-[10px] uppercase tracking-widest text-cyber-500 font-medium">
              Security Platform
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-4 py-2 text-[10px] uppercase tracking-widest text-gray-500 font-semibold">
          Monitoring
        </p>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="text-sm font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User info + logout */}
      <div className="px-3 py-4 border-t border-gray-800/60">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-200 truncate">
              {user?.username}
            </p>
            <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
