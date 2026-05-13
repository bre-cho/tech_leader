import type { StoryboardRequest, ShotSpec, PhaseName } from "./types";

export function compileShotPrompt(req: StoryboardRequest, shot: Omit<ShotSpec, "prompt" | "negativePrompt" | "providerPayload">) {
  const prompt = `
${req.title}
Main character: ${req.mainCharacter}
Location: ${req.location}
Phase: ${shot.phase}
Shot ${shot.id}: ${shot.title}

Scene description:
${shot.description}

Camera:
${shot.camera}
Lens:
${shot.lens}
Movement:
${shot.movement}
Duration:
${shot.durationSec}s

Subject focus:
${shot.subjectFocus}

Emotion beat:
${shot.emotionBeat}

Continuity:
- ${req.identityDna.faceLock ? "same female model face identity across all shots" : "character continuity relaxed"}
- ${req.identityDna.wardrobeContinuity ? "wardrobe continuity must match phase and outfit sequence" : "wardrobe can vary"}
- ${req.identityDna.hairMakeupContinuity ? "hair and makeup continuity preserved per phase" : "hair/makeup variation allowed"}
- Character notes: ${req.identityDna.characterNotes}

Style:
${req.style.mood}
Lighting: ${req.style.lighting}
Camera language: ${req.style.cameraLanguage}
Color grade: ${req.style.colorGrade}

Generate cinematic fashion week storyboard frame / video shot, high-end editorial realism, realistic skin, correct anatomy, luxury event atmosphere, precise fashion details, no random identity drift.
`.trim();

  const negativePrompt = [
    "identity drift",
    "different face",
    "bad anatomy",
    "deformed hands",
    "extra fingers",
    "warped runway",
    "wrong location",
    "low quality",
    "plastic skin",
    "unreadable random text",
    "watermark",
    "logo hallucination",
    "crowd deformation",
    "broken camera perspective",
    "static boring frame"
  ].join(", ");

  return { prompt, negativePrompt };
}

export function providerPayload(req: StoryboardRequest, shot: ShotSpec) {
  const videoProvider = req.providers.video;
  return {
    shotId: shot.id,
    phase: shot.phase,
    provider: videoProvider,
    endpoint:
      videoProvider === "veo" ? "/api/providers/google-managed/veo/generate" :
      videoProvider === "runway" ? "/api/providers/runway/generate" :
      videoProvider === "kling" ? "/api/providers/kling/generate" :
      videoProvider === "ltx" ? "/api/v1/creative-execution/lipdub-workflow" :
      "/api/providers/video/generate",
    prompt: shot.prompt,
    negativePrompt: shot.negativePrompt,
    durationSec: shot.durationSec,
    aspectRatio: req.aspectRatio,
    continuityTags: shot.continuityTags,
    camera: {
      shotType: shot.camera,
      lens: shot.lens,
      movement: shot.movement
    }
  };
}
