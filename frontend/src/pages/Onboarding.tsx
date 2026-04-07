import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle, Cloud, Loader2, Zap } from 'lucide-react';

type Step = 1 | 2 | 3;
type CredentialMode = 'arn' | 'keys';

export function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>(1);
  const [credentialMode, setCredentialMode] = useState<CredentialMode>('arn');
  const [arn, setArn] = useState('');
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [validating, setValidating] = useState(false);
  const [validated, setValidated] = useState(false);

  function handleValidate() {
    setStep(3);
    setValidating(true);
    setTimeout(() => {
      setValidating(false);
      setValidated(true);
    }, 1500);
  }

  const steps = [
    { n: 1, label: 'Choose Provider' },
    { n: 2, label: 'Credentials' },
    { n: 3, label: 'Validate' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
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
            <p className="text-sm text-muted-foreground mb-6">Choose your preferred authentication method</p>

            {/* Tab Toggle */}
            <div className="flex rounded-lg border border-border bg-muted/30 p-1 mb-6">
              <button
                onClick={() => setCredentialMode('arn')}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${
                  credentialMode === 'arn'
                    ? 'bg-card text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                IAM Role ARN
              </button>
              <button
                onClick={() => setCredentialMode('keys')}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${
                  credentialMode === 'keys'
                    ? 'bg-card text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Access Keys
              </button>
            </div>

            {credentialMode === 'arn' ? (
              <div className="mb-6">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  IAM Role ARN
                </label>
                <input
                  type="text"
                  value={arn}
                  onChange={(e) => setArn(e.target.value)}
                  placeholder="arn:aws:iam::123456789012:role/NebulaCostReader"
                  className="w-full px-3 py-2.5 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm font-mono"
                />
                <p className="mt-2 text-xs text-muted-foreground">
                  Create a read-only IAM role and paste its ARN here. Nebula Thrift will assume this role to read cost data.
                </p>
              </div>
            ) : (
              <div className="space-y-4 mb-6">
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

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-2.5 px-4 rounded-lg border border-border text-foreground font-medium text-sm hover:bg-muted transition-all"
              >
                ← Back
              </button>
              <button
                onClick={handleValidate}
                className="flex-1 py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-all"
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
                <p className="text-sm text-muted-foreground">Calling AWS STS to verify your credentials</p>
              </>
            ) : validated ? (
              <>
                <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                  <CheckCircle className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-xl font-bold text-foreground mb-2">Connection successful!</h2>
                <p className="text-sm text-muted-foreground mb-1">AWS Account connected</p>
                <p className="text-xs text-muted-foreground font-mono mb-8">Account ID: 123456789012 · Region: eu-central-1</p>
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
