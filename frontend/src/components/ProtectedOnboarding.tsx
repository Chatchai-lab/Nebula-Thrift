import { RequireAuth } from './RequireAuth';
import { Outlet } from 'react-router-dom';

export function ProtectedOnboarding() {
  return (
    <RequireAuth>
      <Outlet />
    </RequireAuth>
  );
}
