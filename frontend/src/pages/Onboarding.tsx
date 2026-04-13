import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle, Cloud, Loader2, Zap, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../components/ThemeToggle';
import { useAccount } from '../hooks/useAccount';
import { api } from '../services/api';

type Step = 1 | 2 | 3;

interface ConnectedAccount {
  account_id: string;
  region: string;
}

export function Onboarding() {
  const navigate = useNavigate();
  const { connect } = useAccount();
  const [step, setStep] = useState<Step>(1);
  const [accountName, setAccountName] = useState('');
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [validating, setValidating] = useState(false);
  const [validated, setValidated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectedAccount, setConnectedAccount] = useState<ConnectedAccount | null>(null);

  async function handleValidate() {
    if (!accountName.trim() || !accessKeyId.trim() || !secretKey.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setStep(3);
    setValidating(true);
    setError(null);

    try {
      // Register the account with the backend
      const account = await api.registerAccount({
        name: accountName,
        access_key_id: accessKeyId,
        secret_access_key: secretKey,
        region: 'eu-central-1',
      });

      // Save the snapshot so data is available immediately
      await api.saveSnapshot(account.account_id);

      setConnectedAccount({
        account_id: account.account_id,
        region: account.region,
      });

      // Store in context
      connect(account.account_id, account.name);

      setValidating(false);
      setValidated(true);
      toast.success('AWS account connected successfully!');
    } catch (err) {
      setValidating(false);
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect AWS account';
      setError(errorMessage);
      toast.error(errorMessage);
      setStep(2);
    }
  }

  const steps = [
    { n: 1, label: 'Choose Provider' },
    { n: 2, label: 'Credentials' },
    { n: 3, label: 'Validate' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4 relative">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      {/* Logo */}
      <div className="flex items-center gap-3 mb-10">
        <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center">
          <Zap className="w-4 h-4 text-primary" />
        </div>
        <span className="font-bold text-lg text-foreground">Nebula Thrift</span>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-0 mb-10">
        {steps.map((s, i) => (
          <div key={s.n} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                  step > s.n
                    ? 'bg-primary text-primary-foreground'
                    : step === s.n
                    ? 'bg-primary/20 text-primary ring-2 ring-primary'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {step > s.n ? <CheckCircle className="w-4 h-4" /> : s.n}
              </div>
              <span className={`text-xs ${step === s.n ? 'text-foreground font-medium' : 'text-muted-foreground'}`}>
                {s.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={`w-16 h-px mx-2 mb-5 ${step > s.n ? 'bg-primary' : 'bg-border'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Card */}
      <div className="w-full max-w-lg rounded-xl border border-border bg-card p-8">
        {/* Step 1 — Provider */}
        {step === 1 && (
          <>
            <h2 className="text-xl font-bold text-foreground mb-1">Choose your cloud provider</h2>
            <p className="text-sm text-muted-foreground mb-6">Select the provider you want to connect to Nebula Thrift</p>
            <div className="grid grid-cols-3 gap-4 mb-8">
              {/* AWS */}
              <button
                className="flex flex-col items-center gap-3 p-5 rounded-xl border-2 border-primary bg-primary/5 transition-all"
              >
                <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                  <Cloud className="w-5 h-5 text-orange-400" />
                </div>
                <span className="text-sm font-semibold text-foreground">AWS</span>
              </button>
              {/* Azure */}
              <div className="flex flex-col items-center gap-3 p-5 rounded-xl border border-border bg-muted/30 opacity-50 cursor-not-allowed relative">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Cloud className="w-5 h-5 text-blue-400" />
                </div>
                <span className="text-sm font-semibold text-muted-foreground">Azure</span>
                <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-[10px] px-2 py-0.5 rounded-full bg-secondary/30 text-muted-foreground border border-border whitespace-nowrap">
                  Coming Soon
                </span>
              </div>
              {/* GCP */}
              <div className="flex flex-col items-center gap-3 p-5 rounded-xl border border-border bg-muted/30 opacity-50 cursor-not-allowed relative">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <Cloud className="w-5 h-5 text-green-400" />
                </div>
                <span className="text-sm font-semibold text-muted-foreground">GCP</span>
                <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-[10px] px-2 py-0.5 rounded-full bg-secondary/30 text-muted-foreground border border-border whitespace-nowrap">
                  Coming Soon
                </span>
              </div>
            </div>
            <button
              onClick={() => setStep(2)}
              className="w-full py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-all"
            >
              Next →
            </button>
          </>
        )}

        {/* Step 2 — Credentials */}
        {step === 2 && (
          <>
            <h2 className="text-xl font-bold text-foreground mb-1">Connect your AWS account</h2>
            <p className="text-sm text-muted-foreground mb-6">Enter your AWS credentials</p>

            {error && (
              <div className="mb-6 p-4 rounded-lg border border-destructive/30 bg-destructive/10 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Account Name
                </label>
                <input
                  type="text"
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  placeholder="e.g. Production, Development, Testing"
                  className="w-full px-3 py-2.5 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Access Key ID
                </label>
                <input
                  type="text"
                  value={accessKeyId}
                  onChange={(e) => setAccessKeyId(e.target.value)}
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                  className="w-full px-3 py-2.5 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm font-mono"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Secret Access Key
                </label>
                <input
                  type="password"
                  value={secretKey}
                  onChange={(e) => setSecretKey(e.target.value)}
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                  className="w-full px-3 py-2.5 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm font-mono"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-2.5 px-4 rounded-lg border border-border text-foreground font-medium text-sm hover:bg-muted transition-all"
              >
                ← Back
              </button>
              <button
                onClick={handleValidate}
                disabled={validating}
                className="flex-1 py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 disabled:opacity-60 transition-all"
              >
                Validate Connection →
              </button>
            </div>
          </>
        )}

        {/* Step 3 — Validation */}
        {step === 3 && (
          <div className="flex flex-col items-center text-center py-4">
            {validating ? (
              <>
                <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
                <h2 className="text-xl font-bold text-foreground mb-2">Validating connection…</h2>
                <p className="text-sm text-muted-foreground">Registering your AWS account and fetching initial data</p>
              </>
            ) : validated && connectedAccount ? (
              <>
                <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                  <CheckCircle className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-xl font-bold text-foreground mb-2">Connection successful!</h2>
                <p className="text-sm text-muted-foreground mb-1">AWS Account connected</p>
                <p className="text-xs text-muted-foreground font-mono mb-8">
                  Account ID: {connectedAccount.account_id} · Region: {connectedAccount.region}
                </p>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="w-full py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-all"
                >
                  Go to Dashboard →
                </button>
              </>
            ) : null}
          </div>
        )}
      </div>

      {/* Skip link */}
      <p className="mt-6 text-sm text-muted-foreground">
        <Link to="/dashboard" className="text-primary hover:underline">
          Skip for now — explore demo data
        </Link>
      </p>
    </div>
  );
}
