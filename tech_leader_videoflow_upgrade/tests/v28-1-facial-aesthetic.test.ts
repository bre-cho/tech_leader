import { runFacialAestheticEngine } from "../lib/facial-aesthetic-v28-1/facialAestheticEngine";

const result = runFacialAestheticEngine({
  brandName: "Demo Beauty",
  industry: "cosmetic_brand",
  faceDescription: "soft oval balanced face, high elegant nose bridge, large bright almond eyes, soft natural full lips",
  makeupDirection: "clean semi-matte skin, soft luxury contour, premium glow highlight",
  saveWinnerDna: false
});

if (!result.luxury_face_scoring.passed) throw new Error("luxury face scoring failed");
if ((result.verification as any).score < 90) throw new Error("verification failed");
if (!result.prompt_enhancer.includes("FACIAL AESTHETIC PERCEPTION ENGINE")) throw new Error("prompt enhancer missing");
if (!result.negative_prompt.includes("AI doll face")) throw new Error("negative prompt missing AI doll block");

console.log("V28.1 Facial Aesthetic Engine test passed:", result.luxury_face_scoring.final_score);
