import type { BeautyPerceptionRequest, EngineResult } from "./types";

export function routeBeautyProvider(req: BeautyPerceptionRequest, lighting: EngineResult): EngineResult {
  let imageProvider = "Nano Banana";
  let videoProvider = "Veo 3.1";

  if (req.lightingStyle === "DARK_EDITORIAL" || req.lightingStyle === "CINEMATIC_SPOTLIGHT" || req.lightingStyle === "SUNSET_GLOW") {
    imageProvider = "HiDream";
  }
  if (req.references.some(r => r.kind === "pose_ref" || r.kind === "gesture_ref")) {
    imageProvider = "SDXL/Comfy optional precision pass, then Nano Banana commercial pass";
  }
  if (req.platform === "tiktok" || req.platform === "livestream_thumbnail") {
    imageProvider = "Nano Banana";
    videoProvider = "Veo 3.1 + LTX LipDub";
  }

  return {
    name: "ProviderRouter",
    score: 94,
    data: {
      imageProvider,
      videoProvider,
      reasons: {
        "Nano Banana": "beauty consistency, TikTok beauty, KOL realism, feminine softness",
        "HiDream": "editorial luxury, cinematic darkness, fashion campaign",
        "Flux": "texture recovery, realism enhancement",
        "SDXL/Comfy": "precise controllability, LoRA stacking, regional prompting"
      },
      endpoints: {
        nano_banana: "/api/providers/google-managed/nano-banana/generate",
        veo: "/api/providers/google-managed/veo/generate",
        ltx: "/api/v1/creative-execution/lipdub-workflow",
        comfy: "/api/providers/comfyui/run"
      }
    },
    warnings: []
  };
}
