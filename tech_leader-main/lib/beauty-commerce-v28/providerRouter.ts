import type { BeautyCommerceInput, ProviderName } from "./types";

export function routeBeautyCommerceProvider(input: BeautyCommerceInput): { imageProvider: ProviderName; videoProvider: ProviderName; reason: string } {
  if (input.preferredProvider) {
    return {
      imageProvider: input.preferredProvider,
      videoProvider: input.preferredProvider === "banana" ? "veo" : input.preferredProvider,
      reason: "preferredProvider override"
    };
  }

  if (input.references.length >= 2 || input.productName || input.channel === "tiktok" || input.channel === "livestream") {
    return {
      imageProvider: "banana",
      videoProvider: "veo",
      reason: "Banana for commercial beauty consistency; Veo for social beauty motion."
    };
  }

  if (input.industry === "luxury_beauty" || input.industry === "wedding_studio") {
    return {
      imageProvider: "hidream",
      videoProvider: "veo",
      reason: "HiDream for cinematic luxury stills; Veo for cinematic video."
    };
  }

  if (input.industry === "fashion_tryon") {
    return {
      imageProvider: "sdxl",
      videoProvider: "ltx",
      reason: "SDXL/Comfy for controlled fashion details; LTX for avatar motion/lipdub."
    };
  }

  return {
    imageProvider: "banana",
    videoProvider: "veo",
    reason: "default beauty commerce provider route"
  };
}
