import type { FacialAestheticRequest, ContourHighlightPlan } from "./types";

export function buildContourHighlightReasoning(req: FacialAestheticRequest): ContourHighlightPlan {
  const clinic = req.industry === "beauty_clinic";
  const wedding = req.industry === "wedding_studio";

  return {
    highlight_zones: [
      "center forehead",
      "high points of cheekbones",
      "nose bridge",
      "inner eye light catch",
      "soft chin highlight"
    ],
    contour_zones: [
      "soft jawline shadow",
      "nose side contour",
      "temple depth",
      "cheek depth under cheekbone"
    ],
    blush_zones: wedding
      ? ["soft pink blush on upper cheeks for romantic bridal warmth"]
      : clinic
        ? ["minimal healthy blush for trust and natural result"]
        : ["soft pink feminine warmth on cheeks"],
    reasoning: [
      "light brings facial features forward",
      "soft shadow creates dimension without harsh surgery look",
      "nose highlight increases elegance perception",
      "cheek glow increases luxury skin perception",
      "jaw separation improves face structure while keeping approachable softness"
    ]
  };
}
