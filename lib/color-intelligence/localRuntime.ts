type ColorRunPayload = {
  brand_name: string;
  industry: string;
  use_case: string;
  audience: string;
  desired_perception: string[];
  cultural_context?: string;
};

type ColorGraphItem = {
  source: string;
  relation: string;
  target: string;
  weight: number;
  brand_name: string;
  use_case: string;
  created_at: string;
};

const colorGraphStore: ColorGraphItem[] = [];

function nowIso(): string {
  return new Date().toISOString();
}

function clamp(value: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, value));
}

function buildPalette(industry: string, useCase: string) {
  const industryLower = industry.toLowerCase();
  const useCaseLower = useCase.toLowerCase();

  if (useCaseLower === "restore_photo") {
    return [
      { name: "Memory Sepia", hex: "#B88A5C", role: "base", perception: ["nostalgia", "warmth"] },
      { name: "Paper Beige", hex: "#E8D8C5", role: "balance", perception: ["comfort", "realism"] },
      { name: "Natural Skin", hex: "#D2A07B", role: "skin", perception: ["identity", "safety"] },
      { name: "Ink Brown", hex: "#5A4233", role: "detail", perception: ["clarity", "heritage"] },
    ];
  }

  if (industryLower.includes("fashion") || useCaseLower.includes("editorial")) {
    return [
      { name: "Editorial Black", hex: "#161616", role: "base", perception: ["authority", "luxury"] },
      { name: "Runway Ivory", hex: "#F2EFE8", role: "balance", perception: ["premium", "clarity"] },
      { name: "Champagne Gold", hex: "#CFAE72", role: "highlight", perception: ["status", "attention"] },
      { name: "Signal Coral", hex: "#DF6A5E", role: "cta", perception: ["energy", "conversion"] },
    ];
  }

  return [
    { name: "Spa Green", hex: "#9CBFA8", role: "base", perception: ["calm", "trust"] },
    { name: "Warm Ivory", hex: "#F5F1E8", role: "balance", perception: ["clean", "premium"] },
    { name: "Soft Gold", hex: "#C7A86A", role: "highlight", perception: ["luxury", "attention"] },
    { name: "Coral CTA", hex: "#E6766A", role: "cta", perception: ["conversion", "energy"] },
  ];
}

function buildPerceptionScores(payload: ColorRunPayload) {
  const base: Record<string, number> = {
    trust: 78,
    luxury: 75,
    comfort: 72,
    warmth: 74,
    attention: 77,
    conversion: 73,
  };

  for (const perception of payload.desired_perception || []) {
    const key = perception.toLowerCase().trim();
    if (key in base) {
      base[key] = clamp(base[key] + 11);
    }
  }

  return base;
}

export function runColorIntelligenceLocal(payload: ColorRunPayload) {
  const palette = buildPalette(payload.industry || "", payload.use_case || "");
  const perceptionScores = buildPerceptionScores(payload);
  const runId = `color_${Math.random().toString(16).slice(2, 14)}`;

  const materialPlan = {
    primary_material: payload.use_case === "landing_brand" ? "glossy accent" : "matte texture",
    secondary_material: payload.industry.toLowerCase().includes("fashion") ? "soft fabric" : "glass + metal",
    notes: "Match product surface to trust and premium perception before CTA emphasis.",
  };

  const lightingPlan = {
    key_light: "soft diffused key",
    rim_light: "warm rim for premium edges",
    cta_focus: "increase local contrast near CTA and product hero",
  };

  const runtimePrompt =
    `Brand ${payload.brand_name}. Use case ${payload.use_case}. ` +
    `Prioritize ${(payload.desired_perception || []).join(", ")} with audience ${payload.audience}. ` +
    "Keep product readability and avoid muddy shadows.";

  const response = {
    run_id: runId,
    brand_name: payload.brand_name,
    industry: payload.industry,
    use_case: payload.use_case,
    palette,
    perception_scores: perceptionScores,
    material_plan: materialPlan,
    lighting_plan: lightingPlan,
    runtime_prompt: runtimePrompt,
    created_at: nowIso(),
    source: "nextjs_local_fallback",
  };

  for (const item of palette) {
    colorGraphStore.push({
      source: item.name,
      relation: "supports",
      target: item.perception.join(" / "),
      weight: Number(((perceptionScores.conversion + perceptionScores.trust) / 200).toFixed(3)),
      brand_name: payload.brand_name,
      use_case: payload.use_case,
      created_at: nowIso(),
    });
  }

  return response;
}

export function getColorGraphLocal(limit = 200) {
  return { items: colorGraphStore.slice(-Math.max(1, limit)) };
}
