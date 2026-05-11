/** Minimum render resolution (px) below which a blur penalty is applied. */
const MIN_SHARP_RESOLUTION_PX = 720;

/**
 * Compute an estimated blur/sharpness quality score (0–100) from poster attributes.
 *
 * Higher scores indicate a visually sharper, less blurry composition based on
 * the provided attributes.  Falls back to a sensible mid-range default when no
 * attributes are supplied so the function remains backwards-compatible.
 */
export function blurScore(attrs?: {
  /** 0–1: how much of the poster is a single focused subject */
  focusRatio?: number;
  /** 0–1: fraction of image area occupied by high-contrast edges */
  edgeDensity?: number;
  /** render resolution width in px (higher → typically sharper) */
  resolutionWidth?: number;
}): number {
  const focus = Math.min(1, Math.max(0, attrs?.focusRatio ?? 0.6));
  const edges = Math.min(1, Math.max(0, attrs?.edgeDensity ?? 0.5));
  const resPenalty =
    attrs?.resolutionWidth != null && attrs.resolutionWidth < MIN_SHARP_RESOLUTION_PX ? -8 : 0;

  const raw = 55 + focus * 25 + edges * 15 + resPenalty;
  return Math.round(Math.min(100, Math.max(0, raw)));
}

/**
 * Compute an estimated thumbnail click-worthiness score (0–100) from poster
 * attributes such as headline length and visual element counts.
 *
 * Falls back to a sensible mid-range default when no attributes are supplied.
 */
export function thumbnailScore(attrs?: {
  /** short headlines (<= 6 words) score higher */
  headlineWordCount?: number;
  /** presence of a human face increases click-rate */
  hasFace?: boolean;
  /** 0–1: relative brightness/contrast of the dominant visual element */
  contrastScore?: number;
}): number {
  const headlineBoost =
    attrs?.headlineWordCount != null && attrs.headlineWordCount <= 6 ? 10 : 0;
  const faceBoost = attrs?.hasFace ? 8 : 0;
  const contrast = Math.min(1, Math.max(0, attrs?.contrastScore ?? 0.65));

  const raw = 55 + contrast * 20 + headlineBoost + faceBoost;
  return Math.round(Math.min(100, Math.max(0, raw)));
}
