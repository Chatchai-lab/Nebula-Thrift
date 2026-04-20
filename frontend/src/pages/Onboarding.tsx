import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle, Cloud, Loader2, Zap, AlertCircle, XCircle, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../components/ThemeToggle';
import { useAccount } from '../hooks/useAccount';
import { api } from '../services/api';

type Step = 1 | 2 | 3;
type CredentialMethod = 'role' | 'keys';

interface ConnectedAccount {
  account_id: string;
  region: string;
}

const TRUST_POLICY = {
  Version: '2012-10-17',
  Statement: [
    {
      Effect: 'Allow',
      Principal: {
        AWS: 'arn:aws:iam::NEBULA_ACCOUNT_ID:root',
      },
      Action: 'sts:AssumeRole',
    },
  ],
};

export function Onboarding() {
  const navigate = useNavigate();
  const { connect } = useAccount();
  const [step, setStep] = useState<Step>(1);

  // Credential method selection
  const [credMethod, setCredMethod] = useState<CredentialMethod>('keys');

  // Option A: IAM Role
  const [roleArn, setRoleArn] = useState('');
  const [copied, setCopied] = useState(false);

  // Option B: Access Keys
  const [accountName, setAccountName] = useState('');
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretKey, setSecretKey] = useState('');

  // Validation states
  const [validating, setValidating] = useState(false);
  const [validated, setValidated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectedAccount, setConnectedAccount] = useState<ConnectedAccount | null>(null);

  function copyTrustPolicy() {
    navigator.clipboard.writeText(JSON.stringify(TRUST_POLICY, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleValidate() {
    // Validate input based on credential method
    if (credMethod === 'role') {
      if (!roleArn.trim()) {
        setError('Please enter a valid Role ARN');
        return;
      }
    } else {
      if (!accountName.trim() || !accessKeyId.trim() || !secretKey.trim()) {
        setError('Please fill in all fields');
        return;
      }
    }

    setStep(3);
    setValidating(true);
    setError(null);

    try {
      // Register the account with the backend
      const account = await api.registerAccount({
        name: credMethod === 'role' ? 'IAM Role Account' : accountName,
        region: 'eu-central-1',
        ...(credMethod === 'role'
          ? { role_arn: roleArn }
          : { access_key_id: accessKeyId, secret_access_key: secretKey }),
      });

      // Save the snapshot so data is available immediately
      await api.saveSnapshot(account.account_id);

      setConnectedAccount({
        account_id: account.account_id,
        region: account.region,
      });

      // Store in context
      connect(account.account_id, account.name, account.region);

      setValidating(false);
      setValidated(true);
      toast.success('AWS account connected successfully!');
    } catch (err) {
      setValidating(false);
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect AWS account';
      setError(errorMessage);
      toast.error(errorMessage);
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
              <span className="text-xs text-muted-foreground">{s.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={`h-0.5 w-12 mx-2 transition-all ${
                  step > s.n ? 'bg-primary' : 'bg-muted'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Card Container */}
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-border bg-card text-card-foreground shadow-sm p-8">
          {/* Step 1 — Choose Provider */}
          {step === 1 && (
            <>
              <h2 className="text-xl font-bold text-foreground mb-1">Choose your cloud provider</h2>
              <p className="text-sm text-muted-foreground mb-6">Select the provider you want to connect to Nebula Thrift</p>

              <div className="flex gap-3 mb-6">
                {/* AWS */}
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 relative overflow-hidden rounded-lg border-2 border-teal-500 bg-teal-500/10 p-6 text-center transition-all hover:bg-teal-500/20 hover:shadow-lg"
                >
                  <div className="flex flex-col items-center gap-3">
                    <Cloud className="w-8 h-8 text-teal-500" />
                    <span className="font-semibold text-foreground">AWS</span>
                  </div>
                </button>

                {/* Azure */}
                <div className="flex-1 relative overflow-hidden rounded-lg border-2 border-blue-500 bg-blue-500/10 p-6 text-center opacity-50">
                  <div className="absolute inset-0 flex items-center justify-center bg-background/50">
                    <span className="inline-block bg-blue-500/20 px-3 py-1 rounded-full text-xs font-medium text-blue-500">
                      Coming Soon
                    </span>
                  </div>
                  <div className="flex flex-col items-center gap-3">
                    <Cloud className="w-8 h-8 text-blue-500" />
                    <span className="font-semibold text-blue-500">Azure</span>
                  </div>
                </div>

                {/* GCP */}
                <div className="flex-1 relative overflow-hidden rounded-lg border-2 border-yellow-500 bg-yellow-500/10 p-6 text-center opacity-50">
                  <div className="absolute inset-0 flex items-center justify-center bg-background/50">
                    <span className="inline-block bg-yellow-500/20 px-3 py-1 rounded-full text-xs font-medium text-yellow-500">
                      Coming Soon
                    </span>
                  </div>
                  <div className="flex flex-col items-center gap-3">
                    <Cloud className="w-8 h-8 text-yellow-500" />
                    <span className="font-semibold text-yellow-500">GCP</span>
                  </div>
                </div>
              </div>

              <p className="mt-4 text-center text-sm text-muted-foreground">
                <Link to="/dashboard" className="text-primary hover:underline">
                  Skip for now
                </Link>
              </p>
            </>
          )}

          {/* Step 2 — Credentials */}
          {step === 2 && (
            <>
              <h2 className="text-xl font-bold text-foreground mb-1">Connect your AWS account</h2>
              <p className="text-sm text-muted-foreground mb-6">Choose your authentication method</p>

              {/* Credential Method Toggle */}
              <div className="flex rounded-lg border border-border overflow-hidden mb-6">
                <button
                  onClick={() => {
                    setCredMethod('role');
                    setError(null);
                  }}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    credMethod === 'role'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted'
                  }`}
                >
                  IAM Role (Recommended)
                </button>
                <button
                  onClick={() => {
                    setCredMethod('keys');
                    setError(null);
                  }}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    credMethod === 'keys'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted'
                  }`}
                >
                  Access Keys
                </button>
              </div>

              {/* Option A: IAM Role */}
              {credMethod === 'role' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Role ARN
                    </label>
                    <input
                      type="text"
                      value={roleArn}
                      onChange={(e) => setRoleArn(e.target.value)}
                      placeholder="arn:aws:iam::123456789012:role/NebulaCostReader"
                      className="w-full px-3 py-2.5 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Trust Policy
                    </label>
                    <div className="relative">
                      <pre className="bg-muted p-4 rounded-lg text-xs overflow-x-auto border border-border">
                        <code className="text-muted-foreground">
                          {JSON.stringify(TRUST_POLICY, null, 2)}
                        </code>
                      </pre>
                      <button
                        onClick={copyTrustPolicy}
                        className="absolute top-2 right-2 p-2 rounded-lg bg-background hover:bg-muted transition-colors"
                        title="Copy to clipboard"
                      >
                        {copied ? (
                          <Check className="w-4 h-4 text-primary" />
                        ) : (
                          <Copy className="w-4 h-4 text-muted-foreground" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Option B: Access Keys */}
              {credMethod === 'keys' && (
                <div className="space-y-4">
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
              )}

              {error && (
                <div className="mt-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 flex gap-2">
                  <AlertCircle className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}

              <div className="flex gap-3 mt-6">
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

              <p className="mt-4 text-center text-sm text-muted-foreground">
                <Link to="/dashboard" className="text-primary hover:underline">
                  Skip for now
                </Link>
              </p>
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
              ) : error ? (
                <>
                  <div className="w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center mb-4">
                    <XCircle className="w-8 h-8 text-destructive" />
                  </div>
                  <h2 className="text-xl font-bold text-foreground mb-2">Connection failed</h2>
                  <p className="text-sm text-muted-foreground mb-4">{error}</p>
                  <p className="text-xs text-muted-foreground mb-6">
                    Troubleshooting: Check that your credentials are correct and the IAM policy has Cost Explorer read permissions.
                  </p>
                  <button
                    onClick={() => {
                      setError(null);
                      setStep(2);
                    }}
                    className="w-full py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-all"
                  >
                    ← Try again
                  </button>
                </>
              ) : null}
            </div>
          )}
        </div>

        {/* Skip link outside for Step 3 */}
        {step === 3 && !validated && !error && (
          <p className="mt-6 text-center text-sm text-muted-foreground">
            <Link to="/dashboard" className="text-primary hover:underline">
              Skip for now — explore demo data
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
