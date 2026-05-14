export const FACE_WIDTH_LOCK_POSITIVE_TERMS = [
  "soft rounded compact face",
  "soft U-shape face structure",
  "rounded lower face silhouette",
  "softly widened jaw width",
  "natural chin base width retention",
  "soft lower-face width continuity",
  "gentle jaw width preservation",
  "balanced lower-face width distribution",
  "soft facial width transition",
  "subtle youthful face roundness",
  "soft facial mass retention",
  "natural cheek width continuity",
  "short compact lower face",
  "short feminine chin",
  "rounded blunt chin",
  "softly flattened chin tip",
  "smooth curved chin contour",
  "natural soft jaw transition",
  "non-pointed chin structure",
  "balanced cheek-to-chin ratio",
  "soft cheek fullness",
  "subtle cheek volume",
  "youthful Korean facial proportions",
  "shorter nose-to-chin distance",
  "compact soft face geometry",
  "softly rounded jawline"
];

export const FACE_WIDTH_LOCK_REQUIRED_TERMS = [
  "natural chin base width retention",
  "soft lower-face width continuity",
  "gentle jaw width preservation",
  "balanced lower-face width distribution",
  "rounded blunt chin",
  "non-pointed chin structure"
];

export const FACE_WIDTH_LOCK_NEGATIVE_TERMS = [
  "sharp chin tip",
  "pointed chin",
  "aggressive V-line",
  "extreme facial taper",
  "triangular chin",
  "needle chin",
  "narrow chin tip",
  "pinched chin base",
  "collapsed lower face",
  "over-tapered jaw",
  "extreme lower-face narrowing",
  "narrow jaw base",
  "compressed chin width",
  "excessive jaw narrowing",
  "harsh jaw contour",
  "angular chin structure",
  "sharp lower-face convergence",
  "anime V-face",
  "elongated lower face",
  "stretched lower face",
  "long chin",
  "horse face proportions",
  "hollow cheeks",
  "gaunt face",
  "overly sculpted jaw",
  "sunken cheeks",
  "unrealistic facial proportions",
  "exaggerated jaw contour",
  "uncanny valley"
];

export const FACE_BALANCE_PROVIDER_BOOSTERS: Record<string, string[]> = {
  sdxl: ["real camera face proportions", "soft compact DSLR portrait face"],
  flux: ["natural lower-face width", "non-surgical Korean beauty proportions"],
  hidream: ["soft face geometry realism", "rounded chin contour realism"],
  veo: ["temporal face shape consistency", "stable non-pointed chin across frames"],
  runway: ["cinematic face consistency", "soft jawline continuity"],
  kling: ["temporal lower-face width retention", "stable rounded chin structure"],
  generic: ["realistic compact lower-face geometry"]
};
