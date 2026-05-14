import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

const recipes = {
  luxury_tropical_cafe: {
    title: "Luxury Tropical Cafe Girl",
    wardrobe: "soft mint green chiffon lace dress with delicate white lace trimming, elegant feminine silhouette",
    pose: "natural seated pose in rattan chair beside glass table, relaxed shoulders, elegant hand positioning",
    expression: "warm natural smile, direct soft eye contact, friendly luxury beauty commercial vibe",
    environment: "tropical outdoor cafe, lush monstera leaves, palms, rattan furniture, glass table",
    lighting: "golden hour cinematic lighting, warm backlight on hair, soft skin glow",
    camera: "85mm portrait lens, shallow depth of field, commercial beauty photography",
    providerHint: "banana"
  },
  korean_street_fashion: {
    title: "Korean Street Fashion Identity Lock",
    wardrobe: "oversized distressed blue denim shirt, white ribbed tube top with black graphic, chain belt, loose necktie, pearl necklace, silver glasses",
    pose: "confident editorial stance, cool-girl attitude, full-body fashion framing",
    expression: "confident direct gaze, lips softly relaxed",
    environment: "clean neutral fashion studio",
    lighting: "clean studio lighting, soft cinematic shadows, neutral gray background",
    camera: "35mm fashion photography",
    providerHint: "sdxl_comfy"
  },
  sporty_wildcats_campaign: {
    title: "Sporty WildCats Beauty Campaign",
    wardrobe: "white sporty bodysuit with black long sleeves, high-cut hip cutouts, black leather mini skirt, chunky black over-the-knee boots",
    pose: "confident kneeling studio pose, strong commercial sport-fashion energy",
    expression: "direct captivating gaze, confident feminine energy",
    environment: "minimalist white studio",
    lighting: "bright clean studio lighting with soft realistic shadows",
    camera: "35mm vertical full-body fashion campaign",
    providerHint: "sdxl_comfy"
  },
  luxury_lipstick_ad: {
    title: "Luxury Lipstick Beauty Ad",
    wardrobe: "bare-shoulder luxury beauty styling, minimal jewelry",
    pose: "tight close-up portrait with lipstick positioned near lips",
    expression: "direct beauty gaze, lips slightly parted, premium cosmetic appeal",
    environment: "high-end beauty campaign background with soft bokeh",
    lighting: "luxury beauty commercial lighting, golden highlights, perfect skin reflections",
    camera: "85mm macro beauty lens, ultra shallow depth of field",
    providerHint: "banana"
  },
  cinematic_car_wash: {
    title: "Cinematic Car Wash Model",
    wardrobe: "dark gray athletic crop top, matching fitted shorts, black gloves, wet realistic fabric physics",
    pose: "dynamic car detailing pose with natural body mechanics and brand-safe commercial framing",
    expression: "confident feminine energy, practical activity focus",
    environment: "luxury black sports car in dark premium detailing garage with soap foam and wet reflections",
    lighting: "dark cinematic garage lighting, wet reflective highlights, strong contrast",
    camera: "35mm automotive commercial photography",
    providerHint: "hidream"
  },
  custom: {
    title: "Custom Beauty Identity Campaign",
    wardrobe: "use user custom prompt and references",
    pose: "commercial beauty pose driven by references",
    expression: "identity-locked natural expression",
    environment: "user-defined commercial setting",
    lighting: "reference-driven lighting",
    camera: "commercial portrait camera",
    providerHint: "banana"
  }
};

export function buildVisualRecipe(req: BeautyIdentityRuntimeRequest): RuntimeReport {
  const recipe = recipes[req.visualIntent];
  return {
    name: "VisualRecipeLibrary",
    score: 94,
    data: {
      intent: req.visualIntent,
      recipe,
      userCustomPrompt: req.customPrompt,
      safety: [
        "tasteful commercial beauty/fashion framing",
        "adult model assumption",
        "avoid explicit sexual framing",
        "realistic anatomy and fabric physics"
      ]
    },
    warnings: []
  };
}
