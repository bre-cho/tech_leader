import type { CreativeStudioBrief, PerceptionNode } from "@/lib/creative-os/types";

const PERCEPTION_DICTIONARY: Record<string, Omit<PerceptionNode, "id" | "score">> = {
  luxury: {
    label: "Luxury perception",
    signals: ["editorial whitespace", "black/ivory/gold restraint", "serif authority", "slow premium pacing"],
    recommendedVisualMoves: ["increase negative space", "reduce CTA noise", "use cinematic side lighting", "isolate product hero"]
  },
  trust: {
    label: "Trust perception",
    signals: ["proof block", "clean hierarchy", "clinical clarity", "expert cue"],
    recommendedVisualMoves: ["add small proof line", "make benefit stack readable", "avoid over-glow", "show product clearly"]
  },
  innovation: {
    label: "Innovation perception",
    signals: ["blue glow", "futuristic depth", "interface geometry", "high-tech contrast"],
    recommendedVisualMoves: ["add subtle blue rim light", "add clean UI grid", "use dark futuristic background"]
  },
  speed: {
    label: "Speed perception",
    signals: ["diagonal motion", "energy streak", "sharp contrast", "urgent hierarchy"],
    recommendedVisualMoves: ["tilt supporting elements", "increase motion lines", "compress text into short hook"]
  },
  editorial: {
    label: "Editorial perception",
    signals: ["magazine spacing", "refined typography", "quiet composition", "tasteful asymmetry"],
    recommendedVisualMoves: ["use large headline breathing room", "align text to visual axis", "reduce icon clutter"]
  },
  authority: {
    label: "Authority perception",
    signals: ["serif font", "structured proof", "stable center axis", "premium contrast"],
    recommendedVisualMoves: ["use strong headline hierarchy", "add expert/proof badge", "avoid playful fonts"]
  },
  femininity: {
    label: "Femininity perception",
    signals: ["soft highlight", "warm skin-safe palette", "elegant curves", "delicate texture"],
    recommendedVisualMoves: ["use soft beauty light", "add blush/ivory accent", "keep pose and copy refined"]
  },
  virality: {
    label: "Viral attention perception",
    signals: ["high contrast", "scroll-stopping object scale", "before/after tension", "curiosity hook"],
    recommendedVisualMoves: ["enlarge hero object", "create visual contradiction", "use fewer but stronger words"]
  },
  desire: {
    label: "Desire perception",
    signals: ["aspirational result", "sensory close-up", "status cue", "transformation promise"],
    recommendedVisualMoves: ["show outcome not features", "make product tactile", "add premium highlight on benefit"]
  },
  premium: {
    label: "Premium feeling",
    signals: ["controlled contrast", "material detail", "less copy", "high-status composition"],
    recommendedVisualMoves: ["remove low-value badges", "increase product material realism", "use one dominant visual idea"]
  }
};

function normalizeToken(value: string) {
  const lower = value.toLowerCase();
  if (lower.includes("lux") || lower.includes("cao cấp") || lower.includes("premium")) return "luxury";
  if (lower.includes("trust") || lower.includes("tin") || lower.includes("uy tín")) return "trust";
  if (lower.includes("tech") || lower.includes("innovation") || lower.includes("ai")) return "innovation";
  if (lower.includes("viral") || lower.includes("attention") || lower.includes("scroll")) return "virality";
  if (lower.includes("authority") || lower.includes("chuyên gia")) return "authority";
  if (lower.includes("female") || lower.includes("feminine") || lower.includes("nữ")) return "femininity";
  if (lower.includes("editorial") || lower.includes("magazine")) return "editorial";
  if (lower.includes("desire") || lower.includes("ham muốn") || lower.includes("aspiration")) return "desire";
  if (lower.includes("speed") || lower.includes("nhanh")) return "speed";
  return lower.replace(/\s+/g, "_");
}

export function inferDesiredPerception(brief: CreativeStudioBrief): string[] {
  const explicit = brief.desiredPerception?.filter(Boolean) || [];
  const goal = String(brief.goal || "conversion");
  const industry = String(brief.industry || brief.productType || "").toLowerCase();

  const inferred: string[] = [];
  if (goal.includes("luxury") || industry.includes("beauty") || industry.includes("fashion")) inferred.push("luxury", "desire");
  if (goal.includes("trust") || goal.includes("authority")) inferred.push("trust", "authority");
  if (goal.includes("viral")) inferred.push("virality", "speed");
  if (industry.includes("tech") || industry.includes("ai") || industry.includes("saas")) inferred.push("innovation", "trust");
  if (industry.includes("spa") || industry.includes("skincare") || industry.includes("mỹ phẩm")) inferred.push("femininity", "trust", "premium");

  const merged = [...explicit.map(normalizeToken), ...inferred.map(normalizeToken), "conversion"].filter(
    (token, index, arr) => token && arr.indexOf(token) === index
  );

  return merged.slice(0, 6);
}

export function buildPerceptionNodes(brief: CreativeStudioBrief): PerceptionNode[] {
  const desired = inferDesiredPerception(brief);
  return desired.map((token, index) => {
    const preset = PERCEPTION_DICTIONARY[token] || {
      label: token.replace(/_/g, " "),
      signals: ["clear meaning", "brand fit", "visual consistency"],
      recommendedVisualMoves: ["make the visual decision support the chosen perception"]
    };

    const productBonus = brief.productName ? 8 : 0;
    const audienceBonus = brief.audience ? 8 : 0;
    const offerBonus = brief.offer ? 6 : 0;
    const base = 62 + productBonus + audienceBonus + offerBonus - index * 3;

    return {
      id: `perception_${token}`,
      label: preset.label,
      score: Math.max(45, Math.min(96, base)),
      signals: preset.signals,
      recommendedVisualMoves: preset.recommendedVisualMoves
    };
  });
}

export function summarizePerception(nodes: PerceptionNode[]) {
  const totalScore = Math.round(nodes.reduce((sum, node) => sum + node.score, 0) / Math.max(nodes.length, 1));
  return { totalScore, desired: nodes.map((node) => node.id.replace("perception_", "")), nodes };
}
