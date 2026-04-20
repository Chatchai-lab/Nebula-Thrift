import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { ThemeProvider } from './hooks/useTheme';
import { AccountProvider } from './hooks/useAccount';
import { AuthProvider } from './hooks/useAuth';
import { NotificationProvider } from './hooks/useNotificationSettings';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AccountProvider>
          <NotificationProvider>
            <RouterProvider router={router} />
          </NotificationProvider>
        </AccountProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
