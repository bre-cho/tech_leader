const LAYOUT_MAP: Record<string, string> = {
  ingredient: "product_dominance + ingredient_orbit_or_fusion",
  offer: "promotion_offer_cluster + price_focus",
  emotion: "story_world + brand_memory_scene",
  energy: "splash_explosion + oversized_hero",
  feature: "feature_infographic + proof_icons",
  lifestyle: "usage_scene + lifestyle_panels",
  luxury: "macro_luxury_hero + premium_negative_space",
  lookbook: "fashion_lookbook_collage + editorial_grid"
};

export function selectLayout(primary: string, secondary?: string | null): string {
  let layout = LAYOUT_MAP[primary] || "generic_premium_poster";
  if (secondary) {
    layout += ` + secondary_${secondary}`;
  }
  return layout;
}
