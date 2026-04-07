import { Link, Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function Layout() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto flex flex-col">
        {/* Demo Banner */}
        <div
          className="w-full py-3 px-6 flex items-center justify-between border-b border-secondary/30 bg-secondary/10"
        >
          <span className="text-foreground">
            You're viewing demo data — Connect your AWS account for real insights
          </span>
          <Link to="/register" className="px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium text-sm transition-all hover:bg-primary/90">
            Get Started
          </Link>
        </div>
        <div className="flex-1 bg-background">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
