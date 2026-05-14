type CampaignWrite = {
  brand_id: string;
  campaign: Record<string, unknown>;
};

const campaigns: CampaignWrite[] = [];

export const brandMemoryService = {
  async writeCampaign(entry: CampaignWrite) {
    campaigns.push(entry);
    return entry;
  },
  listCampaigns() {
    return [...campaigns];
  },
};

export function inferDecision(ctr: number, conversionRate: number, cpa: number): "clone" | "improve" | "kill" {
  if (ctr >= 0.05 && conversionRate >= 0.03 && cpa <= 20) return "clone";
  if (ctr >= 0.03 && conversionRate >= 0.02 && cpa <= 35) return "improve";
  return "kill";
}
