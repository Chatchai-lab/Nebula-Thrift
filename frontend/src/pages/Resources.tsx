import { useState } from 'react';
import { Calculator, Download, CheckSquare, Square } from 'lucide-react';
import { useCloudData } from '../hooks/useCloudData';

export function Resources() {
  const { recommendations } = useCloudData();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const toggleSelection = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedIds(recommendations.map((r) => r.id));
  };

  const clearAll = () => {
    setSelectedIds([]);
  };

  const selectedRecommendations = recommendations.filter((r) => selectedIds.includes(r.id));
  const monthlySavings = selectedRecommendations.reduce((sum, r) => sum + r.estimatedSavings, 0);
  const yearlySavings = monthlySavings * 12;
  const totalCurrentCost = selectedRecommendations.reduce((sum, r) => sum + r.currentCost, 0);
  const optimizedCost = totalCurrentCost - monthlySavings;
  const percentageSaved = totalCurrentCost > 0 ? ((monthlySavings / totalCurrentCost) * 100).toFixed(1) : 0;

  const groupedByService = recommendations.reduce((acc, rec) => {
    const service = rec.category || 'Other';
    if (!acc[service]) acc[service] = [];
    acc[service].push(rec);
    return acc;
  }, {} as Record<string, typeof recommendations>);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2 text-foreground">
          <Calculator className="w-8 h-8 text-primary" />
          Savings Simulator
        </h1>
        <p className="mt-1 text-muted-foreground">
          Select recommendations to calculate your potential savings
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Recommendation Checklist */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-4 rounded-xl border flex items-center justify-between bg-card border-border">
            <span className="font-semibold text-foreground">
              {selectedIds.length} of {recommendations.length} selected
            </span>
            <div className="flex gap-2">
              <button
                onClick={selectAll}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-all bg-background text-primary border border-border"
              >
                Select All
              </button>
              <button
                onClick={clearAll}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-all bg-background text-muted-foreground border border-border"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {Object.entries(groupedByService).map(([service, recs]) => (
              <div key={service} className="p-6 rounded-xl border bg-card border-border">
                <h3 className="font-bold mb-4 text-foreground">{service}</h3>
                <div className="space-y-3">
                  {recs.map((rec) => {
                    const isSelected = selectedIds.includes(rec.id);
                    return (
                      <div
                        key={rec.id}
                        onClick={() => toggleSelection(rec.id)}
                        className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all border ${
                          isSelected
                            ? 'bg-primary/5 border-primary/30'
                            : 'bg-background border-border'
                        }`}
                      >
                        <div className="mt-0.5">
                          {isSelected ? (
                            <CheckSquare className="w-5 h-5 text-primary" />
                          ) : (
                            <Square className="w-5 h-5 text-muted-foreground" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold mb-1 text-foreground">
                            {rec.resourceName}
                          </div>
                          <div className="text-sm mb-2 text-muted-foreground">
                            {rec.title}
                          </div>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-semibold ${
                                rec.priority === 'high'
                                  ? 'bg-destructive/10 text-destructive'
                                  : rec.priority === 'medium'
                                  ? 'bg-warning/10 text-warning'
                                  : 'bg-primary/10 text-primary'
                              }`}
                            >
                              {rec.priority.toUpperCase()}
                            </span>
                            <span className="text-sm font-semibold text-primary">
                              €{rec.estimatedSavings.toLocaleString('de-DE')}/mo
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right column - Live Summary Panel (Sticky) */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 p-6 rounded-xl border bg-card border-border">
            <h2 className="text-lg font-bold mb-6 text-foreground">Live Summary</h2>

            <div className="mb-6">
              <div className="text-sm mb-2 text-muted-foreground">Monthly Savings</div>
              <div className="text-4xl font-bold text-primary">
                €{monthlySavings.toLocaleString('de-DE')}
              </div>
            </div>

            <div className="mb-6 pb-6 border-b border-border">
              <div className="text-sm mb-2 text-muted-foreground">Yearly Savings</div>
              <div className="text-2xl font-bold text-foreground">
                €{yearlySavings.toLocaleString('de-DE')}
              </div>
            </div>

            {totalCurrentCost > 0 && (
              <>
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-muted-foreground">Current Spend</span>
                    <span className="font-semibold text-foreground">
                      €{totalCurrentCost.toLocaleString('de-DE')}
                    </span>
                  </div>
                  <div className="w-full rounded-full h-3 mb-2 bg-background">
                    <div className="h-3 rounded-full bg-muted-foreground w-full" />
                  </div>

                  <div className="flex items-center justify-between mb-3 mt-4">
                    <span className="text-sm text-muted-foreground">Optimized Spend</span>
                    <span className="font-semibold text-primary">
                      €{optimizedCost.toLocaleString('de-DE')}
                    </span>
                  </div>
                  <div className="w-full rounded-full h-3 bg-background">
                    <div
                      className="h-3 rounded-full bg-primary"
                      style={{
                        width: `${((optimizedCost / totalCurrentCost) * 100).toFixed(0)}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="p-4 rounded-lg mb-6 bg-primary/10 border border-primary/30">
                  <div className="text-sm mb-1 text-muted-foreground">Total Savings</div>
                  <div className="text-3xl font-bold text-primary">{percentageSaved}%</div>
                </div>
              </>
            )}

            <button
              className="w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 bg-secondary text-foreground"
            >
              <Download className="w-4 h-4" />
              Download Report
            </button>

            {selectedIds.length === 0 && (
              <div className="mt-6 p-4 rounded-lg text-center bg-background border border-border">
                <p className="text-sm text-muted-foreground">
                  Select recommendations to see potential savings
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
