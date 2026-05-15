import type { ShotSpec, StoryboardV31Request } from "./types";

const TEMPLATE: Array<Pick<ShotSpec, "phase" | "title" | "description" | "camera" | "lens" | "movement" | "subjectFocus" | "emotionBeat">> = [
  { phase: "atmosphere", title: "Pattern interrupt — LFW lights snap on", description: "Instant spotlight ignition over runway and crowd.", camera: "wide establishing", lens: "24mm", movement: "fast push-in", subjectFocus: "runway lights", emotionBeat: "curiosity" },
  { phase: "atmosphere", title: "Beauty hook close-up eyes", description: "Main model looks into camera for immediate attention lock.", camera: "close-up face eye", lens: "85mm", movement: "slow push", subjectFocus: "eyes", emotionBeat: "beauty hook" },
  { phase: "preparation", title: "Backstage deep breath", description: "Model breathes before stepping out.", camera: "portrait close-up", lens: "85mm", movement: "subtle handheld", subjectFocus: "face", emotionBeat: "anticipation" },
  { phase: "preparation", title: "Accessory macro flash", description: "Jewelry, fabric and bag detail.", camera: "macro close-up", lens: "100mm macro", movement: "micro pan", subjectFocus: "accessory", emotionBeat: "luxury detail" },
  { phase: "ascension", title: "First runway step", description: "Model steps from darkness into the light.", camera: "full body runway", lens: "70-200mm", movement: "tracking backward", subjectFocus: "model walk", emotionBeat: "ascension" },
  { phase: "ascension", title: "Crowd phone reaction", description: "Audience raises phones and turns heads.", camera: "audience reaction close", lens: "50mm", movement: "pan", subjectFocus: "crowd", emotionBeat: "social proof" },
  { phase: "climax", title: "Telephoto catwalk power", description: "Compressed runway view with model walking forward.", camera: "telephoto runway frontal", lens: "200mm", movement: "smooth backward track", subjectFocus: "model", emotionBeat: "escalation" },
  { phase: "climax", title: "Hair and dress slow motion", description: "Fabric and hair move under spotlight.", camera: "medium fashion detail", lens: "85mm", movement: "slow motion", subjectFocus: "hair fabric", emotionBeat: "beauty tension" },
  { phase: "climax", title: "Hero pose at runway end", description: "Model stops and holds iconic pose.", camera: "full body hero", lens: "70mm", movement: "static hero hold", subjectFocus: "pose", emotionBeat: "payoff" },
  { phase: "climax", title: "Photographer flash burst", description: "Cameras fire repeatedly.", camera: "press reaction", lens: "35mm", movement: "flash cut", subjectFocus: "photographers", emotionBeat: "event matters" },
  { phase: "release", title: "Micro smile close-up", description: "Model gives tiny smile after pose.", camera: "beauty close-up face", lens: "85mm", movement: "slow push", subjectFocus: "smile", emotionBeat: "emotional release" },
  { phase: "release", title: "Applause wide finale", description: "Runway, crowd, lights and applause close the arc.", camera: "wide finale", lens: "24mm", movement: "dolly out", subjectFocus: "runway crowd", emotionBeat: "final payoff" }
];

export function createDefaultShortsShots(req: StoryboardV31Request): ShotSpec[] {
  const unit = Math.max(1.6, Math.min(3.5, req.targetDurationSec / TEMPLATE.length));
  return TEMPLATE.map((s, idx) => ({
    id: idx + 1,
    ...s,
    durationSec: Number(unit.toFixed(2)),
    continuityTags: [
      `concept:${req.concept}`,
      `character:${req.mainCharacter}`,
      `location:${req.location}`,
      `fashion:${req.fashionDna}`
    ],
    prompt: "",
    negativePrompt: ""
  }));
}
