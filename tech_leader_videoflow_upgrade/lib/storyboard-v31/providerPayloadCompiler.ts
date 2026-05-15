import type { ShotSpec, StoryboardV31Request } from "./types";

function compilePrompt(req: StoryboardV31Request, shot: ShotSpec, rhythm: any) {
  return `
${req.title}
Concept: ${req.concept}
Platform: ${req.platform}
Location: ${req.location}
Main character: ${req.mainCharacter}
Fashion DNA: ${req.fashionDna}

Shot ${shot.id}: ${shot.title}
Phase: ${shot.phase}
Description: ${shot.description}
Camera: ${shot.camera}
Lens: ${shot.lens}
Movement: ${shot.movement}
Emotion beat: ${shot.emotionBeat}
Subject focus: ${shot.subjectFocus}

Rhythm node:
energy=${rhythm.energy}, intimacy=${rhythm.intimacy}, motion=${rhythm.motion}, tension=${rhythm.tension}, payoff=${rhythm.payoff}, facePriority=${rhythm.facePriority}, socialProof=${rhythm.socialProof}

Cinematic instructions:
Create a fashion-show cinematic Shorts/Reels/TikTok-ready shot with motion continuity, micro-emotion, camera energy, visual tension escalation, and payoff cycling.
Preserve identity continuity, wardrobe continuity, hair/makeup continuity, luxury runway atmosphere, realistic skin and correct anatomy.
`.trim();
}

export function compileProviderPayloads(req: StoryboardV31Request, shots: ShotSpec[], rhythmGraph: any[]) {
  const videoItems = shots.map((shot, idx) => ({
    shotId: shot.id,
    provider: req.provider.video,
    endpoint:
      req.provider.video === "veo" ? "/api/providers/google-managed/veo/generate" :
      req.provider.video === "runway" ? "/api/providers/runway/generate" :
      req.provider.video === "kling" ? "/api/providers/kling/generate" :
      "/api/providers/video/generate",
    prompt: compilePrompt(req, shot, rhythmGraph[idx]),
    negativePrompt: [
      "identity drift",
      "bad anatomy",
      "deformed hands",
      "random camera",
      "static boring frame",
      "plastic skin",
      "wrong outfit continuity",
      "crowd deformation",
      "warped runway",
      "low quality",
      "watermark"
    ].join(", "),
    durationSec: shot.durationSec,
    aspectRatio: req.aspectRatio,
    camera: { shotType: shot.camera, lens: shot.lens, movement: shot.movement },
    rhythm: rhythmGraph[idx]
  }));

  return {
    imageKeyframes: {
      provider: req.provider.image,
      endpoint:
        req.provider.image === "hidream" ? "/api/v1/hidream/commercial-visual/generate" :
        req.provider.image === "banana" ? "/api/providers/google-managed/nano-banana/generate" :
        req.provider.image === "comfyui" ? "/api/providers/comfyui/run" :
        "/api/providers/image/generate",
      items: videoItems.map(item => ({
        shotId: item.shotId,
        prompt: item.prompt,
        negativePrompt: item.negativePrompt,
        aspectRatio: req.aspectRatio
      }))
    },
    videoShots: {
      provider: req.provider.video,
      items: videoItems
    },
    motionFallback: {
      provider: req.provider.motionFallback,
      endpoint:
        req.provider.motionFallback === "runway" ? "/api/providers/runway/generate" :
        req.provider.motionFallback === "kling" ? "/api/providers/kling/generate" :
        "/api/providers/video/generate",
      items: videoItems.filter(item => item.rhythm.motion >= 8 || item.rhythm.energy >= 8)
    },
    renderQueue: videoItems.map(item => ({
      jobType: "video_shot_render",
      shotId: item.shotId,
      provider: item.provider,
      endpoint: item.endpoint,
      payload: item,
      retryPolicy: { maxAttempts: 3, backoffMs: [1000, 3000, 8000] }
    }))
  };
}
