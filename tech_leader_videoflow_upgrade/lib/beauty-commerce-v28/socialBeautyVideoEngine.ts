import type { BeautyCommerceInput } from "./types";
import { runMicroExpressionEngine } from "./microExpressionEngine";
import { runBodyLanguageEngine } from "./bodyLanguageEngine";
import { runProductAttentionRouting } from "./productAttentionRouting";
import { runGestureEngine } from "./gestureEngine";
import { runTikTokTimingEngine } from "./tiktokTimingEngine";

export function runSocialBeautyCommerceVideoEngine(input: BeautyCommerceInput) {
  return {
    microExpression: runMicroExpressionEngine(input),
    bodyLanguage: runBodyLanguageEngine(input),
    productAttention: runProductAttentionRouting(input),
    gesture: runGestureEngine(input),
    tiktokTiming: runTikTokTimingEngine(input)
  };
}

export function buildVideoPlan(input: BeautyCommerceInput, engines: ReturnType<typeof runSocialBeautyCommerceVideoEngine>) {
  const sceneCount = input.sceneCount;
  const durationPerScene = Number((input.durationSec / sceneCount).toFixed(2));
  const scenes = Array.from({ length: sceneCount }).map((_, i) => {
    const n = i + 1;
    const start = Number((i * durationPerScene).toFixed(2));
    const end = Number(((i + 1) * durationPerScene).toFixed(2));
    const purpose =
      n === 1 ? "Hook: eye contact + first-frame beauty trust" :
      n === 2 ? "Attention routing: gesture/pose/product enters focus" :
      n === sceneCount ? "CTA: brand/product recall and conversion" :
      n === 3 ? "Benefit proof: product/fashion/beauty outcome" :
      "Retention beat: micro-expression + movement";

    return {
      scene: n,
      start,
      end,
      purpose,
      bodyLanguage: (engines.bodyLanguage.data.motionPattern as string[])[Math.min(i, 4)],
      eyeFocus: input.productName ? (n % 2 === 0 ? "product" : "camera") : "camera",
      gesture: (engines.gesture.data.gestures as string[])[i % (engines.gesture.data.gestures as string[]).length],
      microExpression: n === 1 ? "slight smile drift + blink" : "subtle smile/breathing motion",
      providerHint: n === 1 ? "Banana keyframe + Veo/LTX motion" : "Veo/Runway/Kling motion provider"
    };
  });

  return {
    pipeline: [
      "Beauty Avatar DNA",
      "Facial Consistency Engine",
      "Body Motion Engine",
      "Eye Tracking Engine",
      "Product Attention Routing",
      "Gesture Engine",
      "LipDub Runtime",
      "Subtitle Karaoke Runtime",
      "TikTok Commercial Timing",
      "Export Vertical Video"
    ],
    aspectRatio: "9:16",
    scenes,
    handoff: {
      lipdub: "/api/v1/creative-execution/lipdub-workflow",
      subtitles: "/api/v1/video/postprocess/render",
      voice: "/api/v1/voice/jobs",
      googleManagedBanana: "/api/providers/google-managed/nano-banana/generate"
    }
  };
}
