import { analyzeFacialAesthetic } from "../lib/facial-aesthetic";

const result = analyzeFacialAesthetic({
  prompt: "K-beauty TikTok commerce poster, KOL holding serum product, lavender pastel layout with readable benefits",
  persona: {
    platform: "tiktok",
    luxuryLevel: 86,
    softnessLevel: 92,
    realismLevel: 90,
    sensualityLevel: 45
  },
  observation: {
    faceShape: "soft oval balanced face with natural asymmetry",
    noseBridge: "high elegant nose bridge with soft contour and refined natural tip",
    eyes: "large bright almond eyes with warm eye contact and catchlight",
    skin: "clean semi-matte skin, cheek glow, nose highlight, premium glow",
    productPlacement: "product in hand and product hero lower center",
    typography: "serif luxury headline, short benefit icons, clear CTA"
  }
});

if (!result.ok) throw new Error("Expected facial aesthetic analysis to pass");
if (result.scores.commercial_face_score < 85) throw new Error("commercial face score too low");
if (!result.providerPayload.prompt.includes("ultra realistic commercial beauty portrait")) throw new Error("provider payload prompt missing");
if (!result.dna.negative_controls.includes("plastic skin")) throw new Error("negative controls missing plastic skin");
if (result.winnerDNA.finalScore <= 80) throw new Error("winner DNA score too low");

const unsafeResult = analyzeFacialAesthetic({
  prompt: "beauty poster with doll face and plastic surgery nose",
  strictCommercialSafety: true
});

if (unsafeResult.ok) throw new Error("Unsafe prompt should be rejected");
if (!unsafeResult.issues.some((issue) => issue.severity === "reject")) {
  throw new Error("Expected a reject issue for unsafe prompt");
}

console.log("V29 Facial Aesthetic Reasoning Engine test passed");
