import { createContext, useContext, useState, type ReactNode } from 'react';

interface NotificationSettings {
  anomalyAlerts: boolean;
  weeklyReport: boolean;
  newRecommendations: boolean;
}

const defaults: NotificationSettings = {
  anomalyAlerts: true,
  weeklyReport: true,
  newRecommendations: true,
};

interface NotificationContextType {
  settings: NotificationSettings;
  toggle: (key: keyof NotificationSettings) => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);
const STORAGE_KEY = 'nebula-notification-settings';

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<NotificationSettings>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? { ...defaults, ...JSON.parse(stored) } : defaults;
    } catch {
      return defaults;
    }
  });

  function toggle(key: keyof NotificationSettings) {
    setSettings((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }

  return (
    <NotificationContext.Provider value={{ settings, toggle }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotificationSettings() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error('useNotificationSettings must be used within NotificationProvider');
  return ctx;
}
