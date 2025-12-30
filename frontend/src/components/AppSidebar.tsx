import { cn } from '@/lib/utils';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart3,
  History,
  Settings,
  Home,
  ChevronLeft,
  ChevronRight,
  Activity,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useHealth } from '@/hooks/useApi';

interface NavItem {
  icon: React.ElementType;
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { icon: Home, label: 'Dashboard', href: '/' },
  { icon: BarChart3, label: 'Analysis', href: '/analysis' },
  { icon: History, label: 'History', href: '/history' },
  { icon: Settings, label: 'Settings', href: '/settings' },
];

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const { data: health } = useHealth();

  return (
    <aside
      className={cn(
        'h-screen bg-sidebar border-r border-sidebar-border flex flex-col transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="p-4 flex items-center gap-3 border-b border-sidebar-border">
        <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <Activity className="w-6 h-6 text-primary-foreground" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="font-bold text-lg tracking-tight truncate">GeminiTrader</h1>
            <p className="text-xs text-muted-foreground">Pro Analysis</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                'hover:bg-sidebar-accent',
                isActive && 'bg-sidebar-accent text-sidebar-primary',
                !isActive && 'text-sidebar-foreground/70'
              )}
            >
              <item.icon className={cn('w-5 h-5 flex-shrink-0', isActive && 'text-sidebar-primary')} />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Status indicator */}
      <div className={cn('p-4 border-t border-sidebar-border', collapsed && 'px-2')}>
        <div className={cn('flex items-center gap-2', collapsed && 'justify-center')}>
          <div
            className={cn(
              'w-2 h-2 rounded-full flex-shrink-0',
              health?.status === 'healthy' ? 'bg-bullish animate-pulse' : 'bg-bearish'
            )}
          />
          {!collapsed && (
            <span className="text-xs text-muted-foreground truncate">
              {health?.status === 'healthy' ? 'API Connected' : 'API Disconnected'}
            </span>
          )}
        </div>
        {!collapsed && health?.active_sessions !== undefined && (
          <p className="text-xs text-muted-foreground mt-1">
            {health.active_sessions} active session{health.active_sessions !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* Collapse toggle */}
      <div className="p-3 border-t border-sidebar-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className={cn('w-full', collapsed && 'px-0')}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4 mr-2" />
              Collapse
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
