import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Lightbulb, Calculator, Settings, X } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ mobileOpen = false, onMobileClose }: SidebarProps) {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/recommendations', label: 'Recommendations', icon: Lightbulb },
    { path: '/simulator', label: 'Savings Simulator', icon: Calculator },
  ];

  const handleNavClick = () => {
    if (onMobileClose) onMobileClose();
  };

  const sidebarContent = (
    <>
      <div className="p-6 border-b border-border flex items-center justify-between">
        <Link to="/" className="block" onClick={handleNavClick}>
          <h1 className="font-bold text-xl text-foreground">
            Nebula Thrift
          </h1>
          <p className="text-sm mt-1 text-muted-foreground">AWS Cost Optimization</p>
        </Link>
        <button
          type="button"
          aria-label="Close menu"
          onClick={onMobileClose}
          className="md:hidden p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  onClick={handleNavClick}
                  className={`flex items-center gap-3 px-4 py-3 rounded-md transition-all relative ${
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r bg-primary" />
                  )}
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-border">
        <Link
          to="/settings"
          onClick={handleNavClick}
          className={`flex items-center gap-3 px-4 py-3 rounded-md w-full transition-all relative ${
            location.pathname === '/settings'
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          }`}
        >
          {location.pathname === '/settings' && (
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r bg-primary" />
          )}
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </Link>
        <div className="mt-2 px-4">
          <ThemeToggle />
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 h-screen flex-col bg-background border-r border-border">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onMobileClose}
            aria-hidden="true"
          />
          <aside className="relative w-64 h-screen flex flex-col bg-background border-r border-border animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  );
}
