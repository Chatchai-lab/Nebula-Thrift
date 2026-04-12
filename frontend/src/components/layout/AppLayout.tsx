import { Outlet } from 'react-router-dom';
import { Navbar } from '../Navbar';

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="max-w-7xl mx-auto">
        {/* Hier werden die eigentlichen Seiteninhalte eingeblendet */}
        <Outlet />
      </main>
    </div>
  );
}