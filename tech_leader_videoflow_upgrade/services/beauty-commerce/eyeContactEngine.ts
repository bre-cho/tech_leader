import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildEyeContactPlan(req: BeautyCommerceRequest) {
  if (req.productName) {
    return {
      sequence: ["look at viewer", "glance to product", "smile", "return gaze to viewer"],
      purpose: "human trust first, then product attention, then conversion confidence",
      videoNote: "In video, gaze should follow product movement instead of presenter standing still."
    };
  }

  return {
    sequence: ["direct calm gaze", "micro smile", "slight head movement"],
    purpose: "emotional attention and brand recall",
    videoNote: "Use subtle eye movement to avoid static AI model feel."
  };
}
