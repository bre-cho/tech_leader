import type { FacialAestheticRequest, FacialDepthProfile } from "./types";

export function buildFacialDepthProfile(req: FacialAestheticRequest): FacialDepthProfile {
  return {
    depth_cues: [
      "soft contour",
      "soft shadow under cheekbone",
      "nose bridge highlight",
      "radiant cheek glow",
      "jawline separation",
      "catchlight in eyes"
    ],
    shadow_rules: [
      "shadows must be soft and beauty-commercial",
      "avoid harsh editorial shadow unless luxury/editorial campaign explicitly requests it",
      "shadow should sculpt, not age the face"
    ],
    glow_rules: [
      "glow on cheekbones and nose bridge",
      "skin must remain realistic with micro texture",
      "avoid oily shine and plastic highlighter"
    ],
    perception_goal: [
      "3D facial perception",
      "luxury skin",
      "soft feminine depth",
      "commercial attractiveness",
      "trustworthy clean beauty"
    ]
  };
}
