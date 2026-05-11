export type ImageVariant = {
  variant_index: number;
  concept_name: string;
  headline: string;
  cta: string;
  layout_direction: string;
  visual_prompt: string;
  asset_url?: string;
  provider?: string;
  provider_job_id?: string | null;
  scores?: Record<string, number | boolean>;
};

export type FormState = {
  industry: string;
  product: string;
  goal: string;
  channel: string;
};
