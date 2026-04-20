import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { api } from '../services/api';

interface AuthUser {
  user_id: string;
  name: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isDemoMode: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  enterDemoMode: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() =>
    sessionStorage.getItem('nebula-demo-mode') === 'true'
  );

  // Restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const currentUser = await api.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        // Not logged in, that's ok
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  function enterDemoMode() {
    sessionStorage.setItem('nebula-demo-mode', 'true');
    setIsDemoMode(true);
  }

  async function register(name: string, email: string, password: string) {
    const user = await api.register({ name, email, password });
    setUser(user);
    // Clear demo mode when user registers
    sessionStorage.removeItem('nebula-demo-mode');
    setIsDemoMode(false);
  }

  async function login(email: string, password: string) {
    const user = await api.login({ email, password });
    setUser(user);
    // Clear demo mode when user logs in
    sessionStorage.removeItem('nebula-demo-mode');
    setIsDemoMode(false);
  }

  async function logout() {
    await api.logout();
    setUser(null);
    // Clear demo mode on logout
    sessionStorage.removeItem('nebula-demo-mode');
    setIsDemoMode(false);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        isDemoMode,
        login,
        register,
        logout,
        enterDemoMode,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
