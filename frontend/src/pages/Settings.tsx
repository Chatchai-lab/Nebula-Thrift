import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { RefreshCw, Unplug, Trash2, Bell, AlertTriangle, BarChart2, Sparkles } from 'lucide-react';
import { useAccount } from '../hooks/useAccount';
import { useAuth } from '../hooks/useAuth';
import { useNotificationSettings } from '../hooks/useNotificationSettings';
import { api } from '../services/api';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

export function Settings() {
  const navigate = useNavigate();
  const { user, isDemoMode } = useAuth();
  const { isConnected, accountId, accountName, region, lastSynced, disconnect, setLastSynced } = useAccount();
  const { settings, toggle } = useNotificationSettings();

  const [syncing, setSyncing] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showUpdateCredentials, setShowUpdateCredentials] = useState(false);
  const [credentialsDraft, setCredentialsDraft] = useState({ accessKeyId: '', secretKey: '' });
  const [updatingCredentials, setUpdatingCredentials] = useState(false);

  async function handleSync() {
    if (!accountId) return;
    setSyncing(true);
    try {
      await api.saveSnapshot(accountId);
      setLastSynced(new Date().toISOString());
      toast.success('Sync complete');
    } catch (err) {
      toast.error('Sync failed');
    } finally {
      setSyncing(false);
    }
  }

  function handleDisconnect() {
    setShowDisconnectConfirm(false);
    if (accountId) {
      api.deleteAccount(accountId).catch((err) => {
        console.warn('Failed to delete account from backend:', err);
      });
    }
    disconnect();
    toast.info('AWS account disconnected');
  }

  function handleDeleteAccount() {
    setShowDeleteConfirm(false);
    handleDisconnect();
    toast.success('Account deleted');
  }

  async function handleUpdateCredentials() {
    if (!credentialsDraft.accessKeyId.trim() || !credentialsDraft.secretKey.trim()) {
      toast.error('Please enter both Access Key ID and Secret Key');
      return;
    }

    if (!accountId) return;

    setUpdatingCredentials(true);
    try {
      await api.updateAccountCredentials(accountId, credentialsDraft.accessKeyId, credentialsDraft.secretKey);
      setShowUpdateCredentials(false);
      setCredentialsDraft({ accessKeyId: '', secretKey: '' });
      toast.success('Credentials updated successfully');
    } catch (err) {
      toast.error('Failed to update credentials');
    } finally {
      setUpdatingCredentials(false);
    }
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
              {isConnected ? 'Connected' : 'Not connected'}
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
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowUpdateCredentials(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-all"
              >
                Update Credentials
              </button>
              <button
                onClick={() => setShowDisconnectConfirm(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:text-destructive hover:border-destructive/50 transition-all"
              >
                <Unplug className="w-4 h-4" />
                Disconnect
              </button>
            </div>
          )}
        </div>

        {isConnected ? (
          <div className="text-sm text-muted-foreground space-y-1 mb-4">
            <p>Account ID: <span className="text-foreground font-mono">{accountId}</span></p>
            <p>Account Name: <span className="text-foreground">{accountName}</span></p>
            <p>Region: <span className="text-foreground font-mono">{region || 'Unknown'}</span></p>
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
              onClick={() => navigate(isDemoMode ? '/register' : '/onboarding')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-all"
            >
              {isDemoMode ? 'Sign Up to Connect AWS →' : 'Connect AWS Account →'}
            </button>
          )}
          {isConnected && (
            <span className="text-xs text-muted-foreground">
              Last sync: {lastSynced ? new Date(lastSynced).toLocaleString() : 'Never'}
            </span>
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
          {/* Anomaly Alerts */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                <AlertTriangle className="w-4 h-4 text-yellow-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Anomaly Alerts</p>
                <p className="text-xs text-muted-foreground mt-0.5">Get notified when costs spike more than 20% week-over-week</p>
              </div>
            </div>
            <Switch checked={settings.anomalyAlerts} onCheckedChange={() => toggle('anomalyAlerts')} />
          </div>

          <div className="h-px bg-border" />

          {/* Weekly Report */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                <BarChart2 className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Weekly Report</p>
                <p className="text-xs text-muted-foreground mt-0.5">Receive a weekly summary of your cloud spend</p>
              </div>
            </div>
            <Switch checked={settings.weeklyReport} onCheckedChange={() => toggle('weeklyReport')} />
          </div>

          <div className="h-px bg-border" />

          {/* New Recommendations */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">New Recommendations</p>
                <p className="text-xs text-muted-foreground mt-0.5">Be notified when new optimization opportunities are found</p>
              </div>
            </div>
            <Switch checked={settings.newRecommendations} onCheckedChange={() => toggle('newRecommendations')} />
          </div>

          {/* Email Field — displays Account email */}
          <div className="pt-2 border-t border-border">
            <label className="block text-xs text-muted-foreground mb-2">Notification Email</label>
            <p className="text-sm text-foreground font-medium">
              {user?.email || 'Not set'}
            </p>
          </div>
        </div>
      </section>

      {/* Account */}
      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Account</h2>
        <div className="space-y-3 mb-6">
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Name</label>
            <p className="text-sm text-foreground font-medium">{user?.name ?? 'Unknown'}</p>
          </div>
          <div>
            <label className="block text-xs text-muted-foreground mb-1">Email</label>
            <p className="text-sm text-foreground font-medium">{user?.email ?? 'Not set'}</p>
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

      {/* Disconnect Confirmation Dialog */}
      <Dialog open={showDisconnectConfirm} onOpenChange={setShowDisconnectConfirm}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Disconnect AWS Account</DialogTitle>
            <DialogDescription>This will remove your AWS connection. Your existing data will be preserved.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDisconnectConfirm(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDisconnect}>
              Disconnect
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Account Confirmation Dialog */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Delete account</DialogTitle>
            <DialogDescription>This action cannot be undone</DialogDescription>
          </DialogHeader>
          <div className="mb-6">
            <p className="text-sm text-muted-foreground">
              All your data, connections, and recommendations will be permanently deleted.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteAccount}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Update Credentials Dialog */}
      <Dialog open={showUpdateCredentials} onOpenChange={setShowUpdateCredentials}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Update AWS Credentials</DialogTitle>
            <DialogDescription>Enter your new AWS credentials to update the connection</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Access Key ID</label>
              <Input
                type="text"
                value={credentialsDraft.accessKeyId}
                onChange={(e) => setCredentialsDraft((prev) => ({ ...prev, accessKeyId: e.target.value }))}
                placeholder="AKIAIOSFODNN7EXAMPLE"
                className="font-mono text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Secret Access Key</label>
              <Input
                type="password"
                value={credentialsDraft.secretKey}
                onChange={(e) => setCredentialsDraft((prev) => ({ ...prev, secretKey: e.target.value }))}
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                className="font-mono text-sm"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUpdateCredentials(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateCredentials} disabled={updatingCredentials}>
              {updatingCredentials ? 'Updating…' : 'Update Credentials'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
