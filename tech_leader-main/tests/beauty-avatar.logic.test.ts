import { createBeautyAvatar } from "../lib/beauty-avatar/beautyAvatarGenerator";

const result = createBeautyAvatar({
  brandName: "Demo Beauty",
  personaType: "kol_beauty",
  industry: "cosmetic_brand",
  faceDescription: "oval face, warm light Asian skin tone, almond eyes, soft full lips",
  targetAudience: "Vietnamese women 22-35",
  renderUsage: ["poster", "short video"],
  quality: "8K",
  saveMemory: false
});

if (!result.identity_lock) throw new Error("identity lock failed");
if (!result.consistency.passed) throw new Error("consistency QA failed");
if (!result.render_profile.prompt.includes("Identity lock")) throw new Error("prompt missing identity lock");
if (!result.avatar_id.startsWith("beauty_avatar_")) throw new Error("avatar id failed");

console.log("V26.1 Beauty Avatar logic test passed:", result.avatar_id);
