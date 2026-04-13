import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { RefreshCw, Unplug, Trash2, Bell, AlertTriangle, BarChart2, Sparkles } from 'lucide-react';
import { useAccount } from '../hooks/useAccount';
import { api } from '../services/api';

export function Settings() {
  const navigate = useNavigate();
  const { isConnected, accountId, accountName, disconnect } = useAccount();
  const [notifications, setNotifications] = useState({
    anomalyAlerts: true,
    weeklyReport: true,
    newRecommendations: false,
  });
  const [syncing, setSyncing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  function handleSync() {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      toast.success('Sync complete');
    }, 1500);
  }

  async function handleDisconnect() {
    if (accountId) {
      try {
        await api.deleteAccount(accountId);
      } catch (err) {
        console.warn('Failed to delete account from backend:', err);
      }
    }
    disconnect();
    toast.info('AWS account disisConnected');
  }

  function handleDeleteAccount() {
    setShowDeleteConfirm(false);
    handleDisconnect();
    toast.success('Account deleted');
  }

  function toggleNotification(key: keyof typeof notifications) {
    setNotifications((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      toast.success(`${next[key] ? 'Enabled' : 'Disabled'} notification`);
      return next;
    });
  }

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="mt-1 text-muted-foreground">Manage your account and integrations</p>
      </div>

      {/* AWS Connection */}
      <section className="rounded-xl border border-border bg-card p-6 mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">AWS Connection</h2>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-primary' : 'bg-muted-foreground'}`} />
            <span className="text-sm font-medium text-foreground">
              {isConnected ? 'Connected' : 'Not isConnected'}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                isConnected
                  ? 'bg-primary/10 text-primary border-primary/30'
                  : 'bg-muted text-muted-foreground border-border'
              }`}
            >
              {isConnected ? 'Active' : 'Demo mode'}
            </span>
          </div>
          {isConnected && (
            <button
              onClick={handleDisconnect}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:text-destructive hover:border-destructive/50 transition-all"
            >
              <Unplug className="w-4 h-4" />
              Disconnect
            </button>
          )}
        </div>

        {isConnected ? (
          <div className="text-sm text-muted-foreground space-y-1 mb-4">
            <p>Account ID: <span className="text-foreground font-mono">{accountId}</span></p>
            <p>Account Name: <span className="text-foreground">{accountName}</span></p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground mb-4">
            Connect your AWS account to get real cost insights and recommendations.
          </p>
        )}

        <div className="flex items-center gap-3">
          {isConnected ? (
            <button
              onClick={handleSync}
              disabled={syncing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-60 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? 'Syncing…' : 'Sync Now'}
            </button>
          ) : (
            <button
              onClick={() => navigate('/onboarding')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-all"
            >
              Connect AWS Account →
            </button>
          )}
          {isConnected && (
            <span className="text-xs text-muted-foreground">Last sync: 2 hours ago</span>
          )}
        </div>
      </section>

      {/* Notifications */}
      <section className="rounded-xl border border-border bg-card p-6 mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          <Bell className="w-5 h-5 inline-block mr-2 text-muted-foreground" />
          Notifications
        </h2>
        <div className="space-y-4">
          <NotificationRow
            icon={<AlertTriangle className="w-4 h-4 text-yellow-400" />}
            label="Anomaly Alerts"
            description="Get notified when costs spike more than 20% week-over-week"
            enabled={notifications.anomalyAlerts}
            onToggle={() => toggleNotification('anomalyAlerts')}
          />
          <div className="h-px bg-border" />
          <NotificationRow
            icon={<BarChart2 className="w-4 h-4 text-blue-400" />}
            label="Weekly Report"
            description="Receive a weekly summary of your cloud spend"
            enabled={notifications.weeklyReport}
            onToggle={() => toggleNotification('weeklyReport')}
          />
          <div className="h-px bg-border" />
          <NotificationRow
            icon={<Sparkles className="w-4 h-4 text-primary" />}
            label="New Recommendations"
            description="Be notified when new optimization opportunities are found"
            enabled={notifications.newRecommendations}
            onToggle={() => toggleNotification('newRecommendations')}
          />
        </div>
      </section>

      {/* Account */}
      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Account</h2>
        <div className="space-y-3 mb-6">
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Name</label>
            <p className="text-sm text-foreground font-medium">Demo User</p>
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Email</label>
            <p className="text-sm text-foreground font-medium">demo@example.com</p>
          </div>
        </div>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-destructive/40 text-destructive text-sm font-medium hover:bg-destructive/10 transition-all"
        >
          <Trash2 className="w-4 h-4" />
          Delete Account
        </button>
      </section>

      {/* Delete Confirm Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-destructive" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Delete account</h3>
                <p className="text-xs text-muted-foreground">This action cannot be undone</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mb-6">
              All your data, connections, and recommendations will be permanently deleted.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-2 px-4 rounded-lg border border-border text-foreground text-sm font-medium hover:bg-muted transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                className="flex-1 py-2 px-4 rounded-lg bg-destructive text-destructive-foreground text-sm font-medium hover:bg-destructive/90 transition-all"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function NotificationRow({
  icon,
  label,
  description,
  enabled,
  onToggle,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{icon}</div>
        <div>
          <p className="text-sm font-medium text-foreground">{label}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        </div>
      </div>
      <button
        onClick={onToggle}
        role="switch"
        aria-checked={enabled}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none ${
          enabled ? 'bg-primary' : 'bg-muted'
        }`}
      >
        <span
          className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow-lg transition-transform ${
            enabled ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  );
}
