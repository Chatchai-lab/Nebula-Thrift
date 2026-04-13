import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { ThemeProvider } from './hooks/useTheme';
import { AccountProvider } from './hooks/useAccount';

export default function App() {
  return (
    <ThemeProvider>
      <AccountProvider>
        <RouterProvider router={router} />
      </AccountProvider>
    </ThemeProvider>
  );
}
