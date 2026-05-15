import type { StoryboardRequest, PhasePlan } from "./types";

export function compileProviderBatches(req: StoryboardRequest, phases: PhasePlan[]) {
  const shots = phases.flatMap(p => p.shots);
  return {
    stillKeyframes: {
      provider: req.providers.still,
      endpoint:
        req.providers.still === "hidream" ? "/api/v1/hidream/commercial-visual/generate" :
        req.providers.still === "banana" ? "/api/providers/google-managed/nano-banana/generate" :
        req.providers.still === "comfyui" ? "/api/providers/comfyui/run" :
        "/api/providers/image/generate",
      items: shots.map(s => ({
        shotId: s.id,
        prompt: s.prompt,
        negativePrompt: s.negativePrompt,
        aspectRatio: req.aspectRatio,
        phase: s.phase
      }))
    },
    videoShots: {
      provider: req.providers.video,
      items: shots.map(s => s.providerPayload)
    },
    altMotion: {
      provider: req.providers.motionAlt,
      endpoint:
        req.providers.motionAlt === "runway" ? "/api/providers/runway/generate" :
        req.providers.motionAlt === "kling" ? "/api/providers/kling/generate" :
        "/api/providers/video/generate",
      items: shots.filter(s => s.phase === "runway" || /slow|quay|bước|walk|catwalk/i.test(s.title)).map(s => ({
        shotId: s.id,
        prompt: s.prompt,
        durationSec: s.durationSec,
        aspectRatio: req.aspectRatio
      }))
    }
  };
}
