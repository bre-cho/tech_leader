import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

export function compileIdentityLockedPromptPack(params: {
  req: BeautyIdentityRuntimeRequest;
  identityDna: RuntimeReport;
  faceLockContract: RuntimeReport;
  visualRecipe: RuntimeReport;
  providerRoute: RuntimeReport;
}): RuntimeReport {
  const { req, identityDna, faceLockContract, visualRecipe, providerRoute } = params;
  const recipe = (visualRecipe.data as any).recipe;

  const globalNegative = [
    "bad anatomy",
    "identity drift",
    "face morphing",
    "asymmetrical eyes",
    "extra fingers",
    "deformed hands",
    "plastic skin",
    "CGI skin",
    "anime face",
    "cartoon style",
    "low resolution",
    "AI artifacts",
    "oversaturated skin",
    "fake reflections",
    "unrealistic body proportions",
    "blurry eyes",
    "deformed mouth",
    "double pupils",
    "over sharpen",
    "mutated limbs",
    "duplicate body parts",
    "fake hair",
    "over smoothing",
    "doll face",
    "uncanny valley",
    "incorrect shadows",
    "poor lighting",
    "warped perspective",
    "text",
    "watermark",
    "logo",
    "signature"
  ].join(", ");

  const prompt = `
${recipe.title}

ULTRA IMPORTANT — FACE LOCK PRIORITY:
The woman's face must remain IDENTICAL to the attached reference images.
Preserve exact eye shape, nose structure, lip shape, cheek proportions, jawline, facial spacing, eyebrow structure, skin tone, facial identity, beauty proportions and facial realism.
NO face morphing. NO identity drift. NO changing ethnicity. NO changing facial geometry. NO over-editing. NO AI plastic skin.

Brand: ${req.brandName}
Campaign: ${req.campaignName}
Platform: ${req.platform}
Product: ${req.product.name ?? "not specified"} ${req.product.category ? `(${req.product.category})` : ""}

Identity DNA:
${JSON.stringify(identityDna.data, null, 2)}

Face Lock Contract:
${JSON.stringify(faceLockContract.data, null, 2)}

Scene:
${recipe.environment}

Wardrobe:
${recipe.wardrobe}

Pose:
${recipe.pose}

Expression:
${recipe.expression}

Lighting:
${recipe.lighting}

Camera:
${recipe.camera}

Quality:
Photorealistic, commercial photography, ${req.output.quality}, high quality, sharp lighting and shadows, natural skin texture, visible pores, realistic hair strands, natural anatomy, professional campaign quality.

Custom instruction:
${req.customPrompt ?? "none"}

User constraints:
${req.constraints.join("\n") || "none"}

No visible text, watermark, logo or signature unless product label is explicitly required.
`.trim();

  const providerPayload = {
    provider: (providerRoute.data as any).selected,
    endpoint: (providerRoute.data as any).endpoints?.[(providerRoute.data as any).selected],
    prompt,
    negativePrompt: globalNegative,
    references: req.references,
    config: {
      aspectRatio: req.output.aspectRatio,
      quality: req.output.quality,
      faceLockStrictness: req.faceLock.strictness,
      outputDir: req.output.outputDir
    }
  };

  return {
    name: "IdentityLockedPromptCompiler",
    score: 96,
    data: {
      prompt,
      negativePrompt: globalNegative,
      providerPayload,
      settings: {
        flux_sdxl: {
          cfg: "5-7",
          steps: "30-40",
          sampler: "DPM++ 2M Karras",
          hiresFix: true,
          faceDetailer: true,
          adetailer: ["eyes", "lips", "hands"]
        },
        nano_banana: {
          identityLock: "HIGH",
          beautyRealism: "HIGH",
          skinRealism: "HIGH",
          commercialPhotographyMode: true,
          faceConsistencyPriority: true
        },
        hidream: {
          editorialBeautyMode: true,
          luxuryCinematicLighting: true,
          skinTexturePreservation: true
        }
      }
    },
    warnings: []
  };
}
