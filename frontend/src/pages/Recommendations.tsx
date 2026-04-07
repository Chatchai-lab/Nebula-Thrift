import { useState } from 'react';
import { Sparkles, AlertCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { useCloudData } from '../hooks/useCloudData';

export function Recommendations() {
  const { recommendations, totalSavingsPotential } = useCloudData();
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filteredRecommendations =
    filter === 'all'
      ? recommendations
      : recommendations.filter((rec) => rec.priority === filter);

  const priorityClasses = {
    high: { indicator: 'bg-destructive', badge: 'bg-destructive/10 text-destructive border-destructive/30', color: 'text-destructive' },
    medium: { indicator: 'bg-warning', badge: 'bg-warning/10 text-warning border-warning/30', color: 'text-warning' },
    low: { indicator: 'bg-primary', badge: 'bg-primary/10 text-primary border-primary/30', color: 'text-primary' },
  };

  const categoryLabel: Record<string, string> = {
    rightsizing: 'Rightsizing',
    unused: 'Unused Resource',
    'reserved-instances': 'Reserved Instance',
    storage: 'Storage Optimization',
    network: 'Network',
  };


  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2 text-foreground">
              Recommendations
            </h1>
            <p className="mt-1 text-muted-foreground">
              {recommendations.length} recommendations found — Potential savings: €{totalSavingsPotential.toLocaleString('de-DE')}/month
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Total Savings Potential</div>
            <div className="text-3xl font-bold text-primary">
              €{totalSavingsPotential.toLocaleString('de-DE')}
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="mb-6 p-4 rounded-xl border flex items-center gap-4 bg-card border-border">
        <span className="text-sm font-medium text-muted-foreground">Priority:</span>
        <div className="flex gap-2">
          {['all', 'high', 'medium', 'low'].map((priority) => (
            <button
              key={priority}
              onClick={() => setFilter(priority as 'all' | 'high' | 'medium' | 'low')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all border ${
                filter === priority
                  ? 'bg-primary text-foreground border-primary'
                  : 'bg-background text-muted-foreground border-border'
              }`}
            >
              {priority === 'all' ? 'All' : priority.charAt(0).toUpperCase() + priority.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {filteredRecommendations.map((rec) => {
          const classes = priorityClasses[rec.priority];
          const isExpanded = expandedId === rec.id;

          return (
            <div
              key={rec.id}
              className={`rounded-xl border transition-all bg-card ${
                isExpanded ? 'border-primary' : 'border-border'
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-1 h-10 rounded ${classes.indicator}`} />
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold border ${classes.badge}`}
                      >
                        {rec.priority.toUpperCase()} PRIORITY
                      </span>
                      <span className="px-3 py-1 rounded text-xs font-semibold bg-provider-aws/10 text-provider-aws border border-provider-aws/30">
                        AWS
                      </span>
                      <span className="px-3 py-1 rounded text-xs font-semibold bg-background text-muted-foreground border border-border">
                        {categoryLabel[rec.category]}
                      </span>
                      <span className="px-3 py-1 rounded text-xs font-semibold bg-background text-secondary border border-secondary/30">
                        {rec.priority === 'high' ? 'Low Effort' : rec.priority === 'medium' ? 'Medium Effort' : 'High Effort'}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-foreground">{rec.title}</h3>
                    <p className="mb-3 text-muted-foreground">{rec.description}</p>
                    <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground">
                      <AlertCircle className="w-4 h-4" />
                      <span>Resource: {rec.resourceName}</span>
                    </div>
                  </div>

                  <div className="text-right ml-6">
                    <div className="text-sm mb-1 text-muted-foreground">Estimated Savings</div>
                    <div className="text-3xl font-bold text-primary">
                      €{rec.estimatedSavings.toLocaleString('de-DE')}
                    </div>
                    <div className="text-sm mt-1 text-muted-foreground">
                      {rec.savingsPercent}% cost reduction
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-32 rounded-full h-2 bg-background">
                        <div
                          className="h-2 rounded-full bg-secondary"
                          style={{ width: `${rec.aiConfidence}%` }}
                        />
                      </div>
                      <span className="text-muted-foreground">{rec.aiConfidence}% AI Confidence</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button 
                      onClick={() => setExpandedId(isExpanded ? null : rec.id)}
                      className="px-4 py-2 rounded-lg transition-all flex items-center gap-2 border border-border text-muted-foreground bg-background" 
                    >
                      Details
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                    <button className="px-4 py-2 rounded-lg transition-all flex items-center gap-2 bg-primary text-foreground">
                      <CheckCircle className="w-4 h-4" />
                      Implement
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-4 p-4 rounded-lg bg-secondary/5 border border-secondary/20">
                    <div className="flex items-start gap-2 mb-4">
                      <Sparkles className="w-4 h-4 flex-shrink-0 mt-0.5 text-secondary" />
                      <div>
                        <p className="text-sm mb-3 text-foreground">
                          <span className="font-semibold">AI Implementation Guide:</span> Follow these steps to implement this optimization safely.
                        </p>
                        <ol className="space-y-2 text-sm text-muted-foreground">
                          <li className="flex gap-2">
                            <span className="font-semibold text-secondary">1.</span>
                            <span>Create a snapshot/backup of <code className="px-2 py-0.5 rounded font-mono text-xs bg-background text-foreground">{rec.resourceName}</code></span>
                          </li>
                          <li className="flex gap-2">
                            <span className="font-semibold text-secondary">2.</span>
                            <span>Review current configuration and dependencies</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="font-semibold text-secondary">3.</span>
                            <span>Schedule maintenance window during low-traffic period</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="font-semibold text-secondary">4.</span>
                            <span>Apply changes using AWS CLI or Terraform</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="font-semibold text-secondary">5.</span>
                            <span>Monitor performance metrics for 24-48 hours</span>
                          </li>
                        </ol>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
