export const STORYBOARD_PROVIDERS = [
  "veo",
  "runway",
  "kling",
  "ltx",
  "banana",
  "hidream",
  "comfyui",
] as const;

export type StoryboardProvider = (typeof STORYBOARD_PROVIDERS)[number];
