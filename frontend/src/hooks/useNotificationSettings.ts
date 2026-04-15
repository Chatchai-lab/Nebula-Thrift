import { useState } from 'react';

interface NotificationSettings {
  anomalyAlerts: boolean;
  weeklyReport: boolean;
  newRecommendations: boolean;
  email: string;
}

const STORAGE_KEY = 'nebula-notifications';

const defaults: NotificationSettings = {
  anomalyAlerts: true,
  weeklyReport: true,
  newRecommendations: false,
  email: '',
};

export function useNotificationSettings() {
  const [settings, setSettings] = useState<NotificationSettings>(() => {
    try {
      const stored =
        typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
      return stored ? JSON.parse(stored) : defaults;
    } catch {
      return defaults;
    }
  });

  function toggle(key: 'anomalyAlerts' | 'weeklyReport' | 'newRecommendations') {
    setSettings((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }

  function setEmail(newEmail: string) {
    setSettings((prev) => {
      const next = { ...prev, email: newEmail };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }

  return { settings, toggle, setEmail };
}
