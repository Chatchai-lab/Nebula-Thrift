import { Outlet } from 'react-router-dom';
import { ThemeToggle } from '../ThemeToggle';

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative">
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>
      <main className="w-full flex justify-center">
        {/* Hier werden Login, Register oder Onboarding eingeblendet */}
        <Outlet />
      </main>
    </div>
  );
}