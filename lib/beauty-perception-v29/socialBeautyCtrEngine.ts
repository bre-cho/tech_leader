import type { BeautyPerceptionRequest, EngineResult } from "./types";

export function runSocialBeautyCtrEngine(req: BeautyPerceptionRequest, engines: Record<string, EngineResult>): EngineResult {
  const platformProfiles = {
    tiktok: ["eye contact mạnh", "softness cao", "center framing", "bright skin", "emotional warmth"],
    instagram: ["editorial composition", "luxury lighting", "stronger contrast"],
    livestream_thumbnail: ["exaggerated gaze clarity", "stronger smile", "brighter eyes"],
    poster: ["clear face hierarchy", "headline safe space", "product recall"],
    lookbook: ["fashion silhouette", "editorial pose", "brand mood"],
    landing_page: ["trust", "clean composition", "premium negative space"]
  };

  const base = 78;
  const eye = engines.eyeContact?.score ?? 80;
  const femininity = engines.femininitySignalGraph?.score ?? 80;
  const lighting = engines.lightingGraph?.score ?? 80;
  const attention = engines.attentionRouting?.score ?? 80;
  const final = Math.min(98, Math.round(base * 0.2 + eye * 0.25 + femininity * 0.2 + lighting * 0.15 + attention * 0.2));

  return {
    name: "SocialBeautyCtrEngine",
    score: final,
    data: {
      platform: req.platform,
      platform_rules: platformProfiles[req.platform],
      ctr_prediction: final >= 94 ? "very_high" : final >= 88 ? "high" : "medium",
      estimated_ctr_range:
        final >= 94 ? "4.5% - 7.0%" :
        final >= 88 ? "3.0% - 5.0%" :
        "1.8% - 3.2%",
      optimization: [
        "increase eye catchlight",
        "keep micro smile natural",
        "use softness and warmth before product push",
        "avoid over-smoothing skin",
        "keep attention route under 3 seconds"
      ]
    },
    warnings: final < 88 ? ["CTR prediction below winner threshold."] : []
  };
}
