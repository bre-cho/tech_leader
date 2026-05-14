export type PosterProductionInput = {
  product?: string;
  product_type?: string;
  text?: string;
  goal?: string;
  brand?: string;
  audience?: string;
  platform?: string;
  ratio?: string;
  headline?: string;
  cta?: string;
  value_icons?: string[];
  hasPackaging?: boolean;
  hasCollection?: boolean;
  useReferenceImage?: boolean;
  perception_targets?: string[];
  industry?: string;
};

export type PosterCodeIntelligenceGraph = {
  purpose: string;
  nodes: Array<{ id: string; label: string }>;
  edges: Array<{ from: string; to: string; relation: string }>;
};
