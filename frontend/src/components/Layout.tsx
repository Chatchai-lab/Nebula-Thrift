import { useState } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Sidebar } from './Sidebar';

export function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar mobileOpen={mobileMenuOpen} onMobileClose={() => setMobileMenuOpen(false)} />
      <main className="flex-1 overflow-auto flex flex-col">
        {/* Mobile TopBar */}
        <div className="md:hidden w-full py-3 px-4 flex items-center justify-between border-b border-border bg-background sticky top-0 z-30">
          <button
            type="button"
            aria-label="Open navigation menu"
            aria-expanded={mobileMenuOpen}
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          <Link to="/" className="font-bold text-foreground">
            Nebula Thrift
          </Link>
          <div className="w-10" aria-hidden="true" />
        </div>

        {/* Demo Banner */}
        <div className="w-full py-3 px-4 sm:px-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-secondary/30 bg-secondary/10">
          <span className="text-sm sm:text-base text-foreground">
            You're viewing demo data — Connect your AWS account for real insights
          </span>
          <Link
            to="/register"
            className="self-start sm:self-auto px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium text-sm transition-all hover:bg-primary/90"
          >
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
