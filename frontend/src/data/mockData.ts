import type { CostTrend } from '../types/cost';
import type { Recommendation } from '../types/recommendation';
import type { CloudResource } from '../types/resource';

export type { CostTrend, Recommendation, CloudResource };

export const costTrends: CostTrend[] = [
  { month: 'Okt', compute: 8400, storage: 2200, database: 3600, network: 1800, total: 16000 },
  { month: 'Nov', compute: 9100, storage: 2400, database: 3800, network: 1900, total: 17200 },
  { month: 'Dez', compute: 10200, storage: 2600, database: 4100, network: 2100, total: 19000 },
  { month: 'Jan', compute: 11800, storage: 2900, database: 4500, network: 2300, total: 21500 },
  { month: 'Feb', compute: 12500, storage: 3100, database: 4800, network: 2400, total: 22800 },
  { month: 'Mär', compute: 13200, storage: 3300, database: 5100, network: 2600, total: 24200 },
];

export const cloudResources: CloudResource[] = [
  { id: 'r1', name: 'prod-web-server-01', provider: 'AWS', type: 'EC2 t3.xlarge', region: 'eu-central-1', monthlyCost: 1240, utilizationPercent: 23, tags: ['production', 'web'] },
  { id: 'r2', name: 'analytics-cluster', provider: 'AWS', type: 'RDS PostgreSQL', region: 'us-east-1', monthlyCost: 2850, utilizationPercent: 78, tags: ['analytics', 'database'] },
  { id: 'r3', name: 'storage-bucket-logs', provider: 'AWS', type: 'S3 Standard', region: 'eu-west-1', monthlyCost: 420, utilizationPercent: 45, tags: ['logs', 'storage'] },
  { id: 'r4', name: 'api-lambda-functions', provider: 'AWS', type: 'Lambda', region: 'eu-central-1', monthlyCost: 680, utilizationPercent: 62, tags: ['production', 'serverless'] },
  { id: 'r5', name: 'ml-training-ec2', provider: 'AWS', type: 'EC2 p3.2xlarge', region: 'us-west-2', monthlyCost: 3850, utilizationPercent: 12, tags: ['ml', 'training'] },
  { id: 'r6', name: 'backup-storage-glacier', provider: 'AWS', type: 'S3 Glacier', region: 'eu-west-1', monthlyCost: 180, utilizationPercent: 92, tags: ['backup', 'storage'] },
  { id: 'r7', name: 'api-gateway-prod', provider: 'AWS', type: 'API Gateway', region: 'eu-central-1', monthlyCost: 520, utilizationPercent: 88, tags: ['production', 'api'] },
  { id: 'r8', name: 'data-warehouse-redshift', provider: 'AWS', type: 'Redshift dc2.large', region: 'us-east-1', monthlyCost: 2400, utilizationPercent: 65, tags: ['data', 'analytics'] },
  { id: 'r9', name: 'cdn-cloudfront-dist', provider: 'AWS', type: 'CloudFront', region: 'global', monthlyCost: 890, utilizationPercent: 75, tags: ['production', 'cdn'] },
  { id: 'r10', name: 'dev-environment-ec2', provider: 'AWS', type: 'EC2 t3.medium', region: 'eu-central-1', monthlyCost: 420, utilizationPercent: 8, tags: ['development'] },
];

export const recommendations: Recommendation[] = [
  {
    id: 'rec1',
    title: 'Downsizen auf t3.medium',
    description: 'Der prod-web-server-01 läuft mit nur 23% Auslastung. KI-Analyse zeigt, dass t3.medium ausreichend wäre.',
    provider: 'AWS',
    resourceName: 'prod-web-server-01',
    currentCost: 1240,
    estimatedSavings: 620,
    savingsPercent: 50,
    priority: 'high',
    category: 'rightsizing',
    aiConfidence: 94,
  },
  {
    id: 'rec2',
    title: 'Ungenutzten ML-EC2 beenden',
    description: 'Die ML-Training-Instanz zeigt nur 12% durchschnittliche Auslastung über 30 Tage. Erwägen Sie Spot-Instanzen.',
    provider: 'AWS',
    resourceName: 'ml-training-ec2',
    currentCost: 3850,
    estimatedSavings: 3080,
    savingsPercent: 80,
    priority: 'high',
    category: 'unused',
    aiConfidence: 91,
  },
  {
    id: 'rec3',
    title: 'S3 Intelligent-Tiering aktivieren',
    description: 'Log-Daten älter als 90 Tage können automatisch in günstigere Storage-Klassen verschoben werden.',
    provider: 'AWS',
    resourceName: 'storage-bucket-logs',
    currentCost: 420,
    estimatedSavings: 315,
    savingsPercent: 75,
    priority: 'medium',
    category: 'storage',
    aiConfidence: 88,
  },
  {
    id: 'rec4',
    title: 'RDS Reserved Instance kaufen',
    description: 'RDS-Datenbank läuft stabil mit hoher Auslastung. 1-Jahr Reserved Instance spart 35%.',
    provider: 'AWS',
    resourceName: 'analytics-cluster',
    currentCost: 2850,
    estimatedSavings: 998,
    savingsPercent: 35,
    priority: 'high',
    category: 'reserved-instances',
    aiConfidence: 96,
  },
  {
    id: 'rec5',
    title: 'Dev-Umgebung auf Schedule setzen',
    description: 'Dev-EC2-Instanz läuft 24/7 mit 8% Auslastung. Automatisches Starten/Stoppen spart 60%.',
    provider: 'AWS',
    resourceName: 'dev-environment-ec2',
    currentCost: 420,
    estimatedSavings: 252,
    savingsPercent: 60,
    priority: 'medium',
    category: 'unused',
    aiConfidence: 92,
  },
  {
    id: 'rec6',
    title: 'Redshift Pause-Resume nutzen',
    description: 'Data Warehouse wird nur tagsüber genutzt. Automatisches Pausieren nachts spart 30%.',
    provider: 'AWS',
    resourceName: 'data-warehouse-redshift',
    currentCost: 2400,
    estimatedSavings: 720,
    savingsPercent: 30,
    priority: 'low',
    category: 'rightsizing',
    aiConfidence: 79,
  },
];

export const totalMonthlyCost = costTrends[costTrends.length - 1].total;
export const totalResources = cloudResources.length;
export const totalSavingsPotential = recommendations.reduce(
  (sum, rec) => sum + rec.estimatedSavings,
  0
);
