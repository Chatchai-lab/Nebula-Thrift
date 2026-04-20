import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, TrendingDown, Zap, BarChart3, ArrowRight, Lightbulb, Bell, Menu, X } from 'lucide-react';
import { ThemeToggle } from '../components/ThemeToggle';
import { useAuth } from '../hooks/useAuth';

export function Landing() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { enterDemoMode } = useAuth();
  const navigate = useNavigate();

  function handleTryDemo() {
    enterDemoMode();
    navigate('/dashboard');
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg sm:text-xl font-bold text-foreground">Nebula Thrift</span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6 lg:gap-8">
            <Link to="/dashboard" className="font-medium text-muted-foreground hover:text-foreground transition-colors">Dashboard</Link>
            <Link to="/recommendations" className="font-medium text-muted-foreground hover:text-foreground transition-colors">Cost Analysis</Link>
            <Link to="/simulator" className="font-medium text-muted-foreground hover:text-foreground transition-colors">Savings</Link>
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-3">
            <ThemeToggle />
            <Link
              to="/login"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 rounded-md text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile Actions */}
          <div className="md:hidden flex items-center gap-1">
            <ThemeToggle />
            <button
              type="button"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
              className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              onClick={() => setMobileMenuOpen((open) => !open)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border bg-background">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex flex-col gap-2">
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/recommendations"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                Cost Analysis
              </Link>
              <Link
                to="/simulator"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                Savings
              </Link>
              <div className="h-px bg-border my-2" />
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all text-center"
              >
                Get Started
              </Link>
            </nav>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-12 sm:pt-16 lg:pt-20 pb-16 sm:pb-24 lg:pb-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full text-xs sm:text-sm border border-primary/20 bg-primary/10 text-primary mb-5 sm:mb-6">
              <Sparkles className="w-4 h-4" />
              <span>Introducing Nebula Thrift v1.0</span>
              <ArrowRight className="w-4 h-4" />
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-h1 font-bold mb-5 sm:mb-6 text-foreground leading-tight">
              Control the Cloud.{' '}
              <span className="text-primary">Keep the Cash.</span>
            </h1>

            <p className="text-base sm:text-lg lg:text-xl mb-7 sm:mb-8 text-muted-foreground leading-relaxed">
              Stop the bleed of inefficient cloud spending. Our autonomous intelligence engine scans,
              analyzes, and optimizes your infrastructure in real-time.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <button
                onClick={handleTryDemo}
                className="px-6 sm:px-8 py-3 sm:py-4 rounded-md font-semibold text-center transition-all bg-primary text-primary-foreground hover:bg-primary/90"
              >
                Try Demo
              </button>
              <button className="px-6 sm:px-8 py-3 sm:py-4 font-semibold underline text-muted-foreground hover:text-foreground transition-colors">
                View Pricing
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-lg border border-border bg-card overflow-hidden transform lg:rotate-2 lg:hover:rotate-0 transition-transform shadow-[0_20px_60px_rgba(52,211,153,0.1)]">
              <div className="p-3 sm:p-4">
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-3 sm:mb-4">
                  <div className="p-3 sm:p-4 rounded-md bg-background border border-border">
                    <div className="text-xs sm:text-sm mb-1 sm:mb-2 text-muted-foreground">Total Spend</div>
                    <div className="text-xl sm:text-2xl font-bold text-foreground">€24,200</div>
                  </div>
                  <div className="p-3 sm:p-4 rounded-md bg-primary/5 border border-primary/20">
                    <div className="text-xs sm:text-sm mb-1 sm:mb-2 text-muted-foreground">Savings</div>
                    <div className="text-xl sm:text-2xl font-bold text-primary">€5,985</div>
                  </div>
                </div>
                <div className="h-28 sm:h-32 rounded-md flex items-end gap-2 bg-background p-2">
                  {[40, 65, 45, 80, 55, 90, 70].map((height, i) => (
                    <div key={i} className="flex-1 rounded bg-primary/80" style={{ height: `${height}%` }} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="border-y border-border py-10 sm:py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-6 sm:mb-8 text-xs tracking-wider text-muted-foreground">
            TRUSTED BY MODERN ENGINEERING TEAMS
          </div>
          <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 lg:gap-12">
            {['ACME', 'TECHCORP', 'CLOUDIFY', 'DATASTREAM', 'NEXUS'].map((company) => (
              <div key={company} className="text-lg sm:text-xl lg:text-2xl font-bold text-border">
                {company}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-20 lg:py-24">
        <div className="text-center mb-10 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-h2 font-bold mb-4 text-foreground">How It Works</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          <div className="p-6 sm:p-8 rounded-lg border border-border bg-card relative">
            <div className="text-7xl sm:text-8xl font-bold absolute top-4 right-4 opacity-5 text-foreground">01</div>
            <div className="w-12 h-12 rounded-md flex items-center justify-center mb-5 sm:mb-6 relative z-10 bg-primary/10">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 text-foreground">Connect &amp; Scan</h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Connect your AWS account in seconds with read-only permissions. We map your entire footprint instantly.
            </p>
          </div>

          <div className="p-6 sm:p-8 rounded-lg border border-border bg-card relative">
            <div className="text-7xl sm:text-8xl font-bold absolute top-4 right-4 opacity-5 text-foreground">02</div>
            <div className="w-12 h-12 rounded-md flex items-center justify-center mb-5 sm:mb-6 relative z-10 bg-secondary/10">
              <Lightbulb className="w-6 h-6 text-secondary" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 text-foreground">Intelligent Analysis</h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Our AI engine identifies idle instances, over-provisioned databases, and orphaned snapshots.
            </p>
          </div>

          <div className="p-6 sm:p-8 rounded-lg border border-border bg-card relative">
            <div className="text-7xl sm:text-8xl font-bold absolute top-4 right-4 opacity-5 text-foreground">03</div>
            <div className="w-12 h-12 rounded-md flex items-center justify-center mb-5 sm:mb-6 relative z-10 bg-primary/10">
              <TrendingDown className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 text-foreground">Optimize &amp; Save</h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Implement changes with a single click or automate the entire process. Watch your cloud bill shrink.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Detail Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-20 lg:py-24">
        <div className="text-center mb-10 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-h2 font-bold text-foreground">Engineered for Precision.</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="lg:row-span-2 p-6 sm:p-8 rounded-lg border border-border bg-card">
            <div className="text-xs tracking-wider mb-4 text-primary">REAL-TIME ANALYTICS</div>
            <h3 className="text-xl sm:text-2xl font-bold mb-4 text-foreground">
              Granular Visibility Across Every Cluster
            </h3>
            <p className="mb-6 sm:mb-8 text-sm sm:text-base text-muted-foreground">
              Monitor every resource in real-time with comprehensive cost attribution and usage metrics.
            </p>
            <div className="h-40 sm:h-48 rounded-md flex items-end gap-2 p-3 sm:p-4 bg-background">
              {[30, 45, 65, 55, 75, 60, 85, 70, 90, 80].map((height, i) => (
                <div
                  key={i}
                  className="flex-1 rounded"
                  style={{
                    background: 'linear-gradient(to top, var(--primary), color-mix(in srgb, var(--primary) 30%, transparent))',
                    height: `${height}%`,
                  }}
                />
              ))}
            </div>
          </div>

          <div className="p-6 sm:p-8 rounded-lg border border-border bg-card">
            <div className="w-12 h-12 rounded-md flex items-center justify-center mb-5 sm:mb-6 bg-secondary/10">
              <BarChart3 className="w-6 h-6 text-secondary" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 text-foreground">Smart Insights</h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Predictive modeling that warns you about future cost spikes before they happen.
            </p>
          </div>

          <div className="p-6 sm:p-8 rounded-lg border border-border bg-card">
            <div className="w-12 h-12 rounded-md flex items-center justify-center mb-5 sm:mb-6 bg-secondary/10">
              <Bell className="w-6 h-6 text-secondary" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 text-foreground">Anomaly Detection</h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Automated alerts for irregular traffic patterns or runaway serverless functions.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-20 lg:py-24">
        <div
          className="rounded-2xl p-8 sm:p-12 lg:p-16 text-center border border-border"
          style={{ background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.1), rgba(139, 92, 246, 0.1))' }}
        >
          <h2 className="text-3xl sm:text-4xl lg:text-h2 font-bold mb-4 text-foreground">
            Ready to trim the fat?
          </h2>
          <p className="text-base sm:text-lg lg:text-xl mb-6 sm:mb-8 max-w-2xl mx-auto text-muted-foreground">
            Join infrastructure teams who have reclaimed millions in cloud waste using Nebula Thrift's autonomous engine.
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-6 sm:px-8 py-3 sm:py-4 rounded-md font-semibold transition-all bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Schedule an Audit
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-12 sm:mt-16 lg:mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="text-center md:text-left">
              <span className="font-bold text-foreground">Nebula Thrift</span>
              <div className="text-sm mt-1 text-muted-foreground">&copy; 2026 Nebula Thrift. All rights reserved.</div>
            </div>
            <div className="flex flex-wrap justify-center gap-4 sm:gap-6 text-sm text-muted-foreground">
              <button className="hover:text-foreground transition-colors">Privacy Policy</button>
              <button className="hover:text-foreground transition-colors">Terms of Service</button>
              <button className="hover:text-foreground transition-colors">API Documentation</button>
              <button className="hover:text-foreground transition-colors">Support</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
