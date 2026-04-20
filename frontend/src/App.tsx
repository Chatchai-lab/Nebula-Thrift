import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { ThemeProvider } from './hooks/useTheme';
import { AccountProvider } from './hooks/useAccount';
import { AuthProvider } from './hooks/useAuth';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AccountProvider>
          <RouterProvider router={router} />
        </AccountProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
