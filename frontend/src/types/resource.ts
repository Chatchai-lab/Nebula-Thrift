export interface CloudResource {
  id: string;
  name: string;
  provider: 'AWS';
  type: string;
  region: string;
  monthlyCost: number;
  utilizationPercent: number;
  tags: string[];
}
