export type ImageVariant = {
  variant_index: number;
  concept_name: string;
  headline: string;
  cta: string;
  layout_direction: string;
  visual_prompt: string;
  scores?: Record<string, number | boolean>;
};

export type FormState = {
  industry: string;
  product: string;
  goal: string;
  channel: string;
};
