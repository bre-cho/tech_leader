import type { BeautyProvider } from "./types";

export function getProviderHairBooster(provider: BeautyProvider = "generic"): string[] {
  switch (provider) {
    case "sdxl":
      return ["RAW beauty photography", "DSLR realism", "high detail hair texture"];
    case "flux":
      return ["micro strand detail", "realistic strand separation", "natural hairline realism"];
    case "hidream":
      return ["cinematic hair micro texture realism", "luxury beauty face detail"];
    case "veo":
      return ["natural hair motion physics", "realistic strand simulation", "soft moving flyaway hairs"];
    case "runway":
      return ["cinematic hair motion", "runway spotlight catching individual hair strands"];
    case "kling":
      return ["temporal hair consistency", "realistic hair movement continuity"];
    default:
      return ["photorealistic hair detail", "natural strand separation"];
  }
}
