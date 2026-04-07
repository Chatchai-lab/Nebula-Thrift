import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Lightbulb, Calculator, Settings } from 'lucide-react';

export function Sidebar() {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/recommendations', label: 'Recommendations', icon: Lightbulb },
    { path: '/simulator', label: 'Savings Simulator', icon: Calculator },
  ];

  return (
    <div className="w-64 h-screen flex flex-col bg-background border-r border-border">
      <div className="p-6 border-b border-border">
        <Link to="/" className="block">
          <h1 className="font-bold text-xl text-foreground">
            Nebula Thrift
          </h1>
          <p className="text-sm mt-1 text-muted-foreground">AWS Cost Optimization</p>
        </Link>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
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
      </div>
    </div>
  );
}
