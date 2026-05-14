import type { BeautyPerceptionRequest, EngineResult } from "./types";

export function runEyeContactEngine(req: BeautyPerceptionRequest): EngineResult {
  const direct = req.desiredSignals.some(s => /eye|camera|gaze|direct/i.test(s));
  const product = Boolean(req.productName);
  const score = direct ? 96 : 88;

  return {
    name: "EyeContactEngine",
    score,
    data: {
      gaze_alignment: direct ? "direct_soft_camera_lock" : "soft_near_camera_gaze",
      iris_visibility: "clear visible iris with catchlight",
      eyelid_softness: "relaxed eyelids, no harsh stare",
      emotional_warmth: "micro smile + gentle eyes",
      viewer_lock_duration: req.platform === "tiktok" ? "first 0.7s critical" : "first glance and hero frame",
      sequence: product
        ? ["camera trust", "product glance", "camera confirmation"]
        : ["camera trust", "micro smile", "soft side glance", "return to camera"],
      perception_mapping: {
        "direct camera eye contact": "attention lock",
        "soft eyelids": "friendliness",
        "catchlight": "trust and vitality"
      }
    },
    warnings: direct ? [] : ["Direct eye contact not explicitly requested; CTR may be lower for TikTok/livestream."]
  };
}
