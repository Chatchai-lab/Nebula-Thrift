import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Zap, Server, AlertCircle } from 'lucide-react';
import { useCloudData } from '../hooks/useCloudData';

export function Dashboard() {
  const { costTrends, totalResources, totalSavingsPotential, recommendations } = useCloudData();
  const currentMonth = costTrends[costTrends.length - 1];
  const previousMonth = costTrends[costTrends.length - 2];
  const costIncrease = currentMonth.total - previousMonth.total;
  const costIncreasePercent = ((costIncrease / previousMonth.total) * 100).toFixed(1);
  const isIncreasing = costIncrease > 0;

  const serviceData = [
    { name: 'Compute', value: currentMonth.compute, color: 'var(--chart-compute)' },
    { name: 'Database', value: currentMonth.database, color: 'var(--chart-database)' },
    { name: 'Storage', value: currentMonth.storage, color: 'var(--chart-storage)' },
    { name: 'Network', value: currentMonth.network, color: 'var(--chart-network)' },
  ];

  const topRecommendations = recommendations.slice(0, 3);

  const chartTooltipStyle = {
    backgroundColor: 'var(--card)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    color: 'var(--foreground)',
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">Overview of your AWS costs and optimization opportunities</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="p-6 rounded-xl border bg-card border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Total Spend</span>
            <DollarSign className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold text-foreground">
            €{currentMonth.total.toLocaleString('de-DE')}
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm">
            {isIncreasing ? (
              <>
                <TrendingUp className="w-4 h-4 text-destructive" />
                <span className="text-destructive">+{costIncreasePercent}% vs last month</span>
              </>
            ) : (
              <>
                <TrendingDown className="w-4 h-4 text-primary" />
                <span className="text-primary">{costIncreasePercent}% vs last month</span>
              </>
            )}
          </div>
        </div>

        <div className="p-6 rounded-xl border bg-primary/5 border-primary/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Identified Savings</span>
            <Zap className="w-5 h-5 text-primary" />
          </div>
          <div className="text-2xl font-bold text-primary">
            €{totalSavingsPotential.toLocaleString('de-DE')}
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm">
            <TrendingDown className="w-4 h-4 text-primary" />
            <span className="text-primary">
              {((totalSavingsPotential / currentMonth.total) * 100).toFixed(0)}% potential reduction
            </span>
          </div>
        </div>

        <div className="p-6 rounded-xl border bg-secondary/5 border-secondary/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Active Recommendations</span>
            <AlertCircle className="w-5 h-5 text-secondary" />
          </div>
          <div className="text-2xl font-bold text-foreground">
            {recommendations.length}
          </div>
          <div className="text-sm mt-2 text-muted-foreground">
            {recommendations.filter(r => r.priority === 'high').length} high priority
          </div>
        </div>

        <div className="p-6 rounded-xl border bg-card border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Trend vs Last Month</span>
            <Server className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className={`text-2xl font-bold ${isIncreasing ? 'text-destructive' : 'text-primary'}`}>
            {isIncreasing ? '+' : ''}{costIncreasePercent}%
          </div>
          <div className="text-sm mt-2 text-muted-foreground">
            {totalResources} active resources
          </div>
        </div>
      </div>

      {/* Cost Trend Chart */}
      <div className="mb-8">
        <div className="p-6 rounded-xl border bg-card border-border">
          <h2 className="text-lg font-bold mb-4 text-foreground">Cost Overview — Last 30 Days</h2>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={costTrends}>
              <defs>
                <linearGradient id="computeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--chart-compute)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="var(--chart-compute)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="totalGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="month" stroke="var(--muted-foreground)" />
              <YAxis stroke="var(--muted-foreground)" />
              <Tooltip
                formatter={(value: number) => `€${value.toLocaleString('de-DE')}`}
                contentStyle={chartTooltipStyle}
              />
              <Legend />
              <Line type="monotone" dataKey="compute" stroke="var(--chart-compute)" strokeWidth={2} name="Compute" fill="url(#computeGradient)" />
              <Line type="monotone" dataKey="database" stroke="var(--chart-database)" strokeWidth={2} name="Database" />
              <Line type="monotone" dataKey="storage" stroke="var(--chart-storage)" strokeWidth={2} name="Storage" />
              <Line type="monotone" dataKey="network" stroke="var(--chart-network)" strokeWidth={2} name="Network" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Service Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="p-6 rounded-xl border bg-card border-border">
          <h2 className="text-lg font-bold mb-4 text-foreground">Service Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={serviceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {serviceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => `€${value.toLocaleString('de-DE')}`}
                contentStyle={chartTooltipStyle}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 rounded-xl border bg-card border-border">
          <h2 className="text-lg font-bold mb-4 text-foreground">Cost by Service</h2>
          <div className="space-y-4">
            {serviceData.map((service) => {
              const percentage = ((service.value / currentMonth.total) * 100).toFixed(1);
              return (
                <div key={service.name}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: service.color }} />
                      <span className="font-medium text-foreground">{service.name}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">{percentage}%</span>
                      <span className="font-semibold text-foreground">€{service.value.toLocaleString('de-DE')}</span>
                    </div>
                  </div>
                  <div className="w-full rounded-full h-2 bg-background">
                    <div 
                      className="h-2 rounded-full" 
                      style={{ backgroundColor: service.color, width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Recommendations Preview */}
      <div className="p-6 rounded-xl border bg-card border-border">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-foreground">Top Recommendations</h2>
          <a href="/recommendations" className="text-sm font-medium text-primary">View All →</a>
        </div>
        <div className="space-y-4">
          {topRecommendations.map((rec) => {
            const priorityClasses = {
              high: { indicator: 'bg-destructive', badge: 'bg-destructive/10 text-destructive border border-destructive/30' },
              medium: { indicator: 'bg-warning', badge: 'bg-warning/10 text-warning border border-warning/30' },
              low: { indicator: 'bg-primary', badge: 'bg-primary/10 text-primary border border-primary/30' },
            };
            const classes = priorityClasses[rec.priority];

            return (
              <div key={rec.id} className="p-4 rounded-lg border bg-background border-border">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-1 h-8 rounded ${classes.indicator}`} />
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${classes.badge}`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <span className="text-xs font-mono text-muted-foreground">{rec.resourceName}</span>
                    </div>
                    <h3 className="font-semibold mb-1 text-foreground">{rec.title}</h3>
                    <p className="text-sm text-muted-foreground">{rec.description}</p>
                  </div>
                  <div className="text-right ml-6">
                    <div className="text-2xl font-bold text-primary">
                      €{rec.estimatedSavings.toLocaleString('de-DE')}
                    </div>
                    <div className="text-xs text-muted-foreground">per month</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
