import { RequireAuth } from './RequireAuth';
import { Layout } from './Layout';

export function ProtectedLayout() {
  return (
    <RequireAuth>
      <Layout />
    </RequireAuth>
  );
}
