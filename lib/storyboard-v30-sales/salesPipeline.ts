import {
  ProductCategory,
  SalesDecision,
  SalesMechanism,
  SalesProviderPrompt,
  SalesScene,
  SalesStoryboardInput,
  SalesStoryboardInputSchema,
  SalesStoryboardOutput,
  SalesStoryboardScore
} from "./types";

const hasAny = (text: string, words: string[]) => words.some((w) => text.includes(w));

export function detectSalesCategory(input: SalesStoryboardInput): ProductCategory {
  const t = `${input.productName} ${input.category || ""} ${input.brief || ""} ${input.posterPrompt || ""} ${input.styleHint || ""}`.toLowerCase();
  if (hasAny(t, ["lipstick", "son môi", "lip"])) return "lipstick";
  if (hasAny(t, ["skincare", "serum", "kem dưỡng", "làm trắng", "body cream", "sunscreen", "chống nắng", "spf"])) return "skincare";
  if (hasAny(t, ["fashion", "váy", "dress", "corset", "lookbook", "runway"])) return "fashion";
  if (hasAny(t, ["nước mắm", "fish sauce", "soy sauce", "nước tương", "sauce"])) return "sauce";
  if (hasAny(t, ["juice", "drink", "beverage", "nước ép"])) return "drink";
  if (hasAny(t, ["muối", "seasoning", "gia vị", "chấm"])) return "seasoning";
  if (hasAny(t, ["gym", "fitness", "boxing"])) return "fitness";
  return "product";
}

export function detectSalesMechanism(input: SalesStoryboardInput, category: ProductCategory): SalesMechanism {
  const t = `${input.productName} ${input.brief || ""} ${input.posterPrompt || ""} ${input.styleHint || ""}`.toLowerCase();
  if (category === "lipstick" || hasAny(t, ["micro contrast on lips", "lipstick touching lips"])) return "lip_desire";
  if (hasAny(t, ["before after", "trước sau", "transformation", "làm trắng"])) return "skin_transformation";
  if (hasAny(t, ["shield", "khiên", "sunlight", "chống nắng"])) return "sun_shield";
  if (hasAny(t, ["liquid vortex", "vortex", "xoáy"])) return "liquid_vortex";
  if (hasAny(t, ["explosion", "splash", "ingredient", "nguyên liệu", "spice"])) return "ingredient_explosion";
  if (hasAny(t, ["texture", "macro", "lace", "chất liệu", "micro contrast"])) return "texture_proof";
  if (hasAny(t, ["miniature", "farmers", "fishermen", "ngư dân", "nông dân"])) return "mini_world_story";
  if (category === "fashion" || hasAny(t, ["dior", "ysl", "luxury", "premium"])) return "luxury_identity";
  return "product_dominance";
}

export function routeSalesStoryboard(input: SalesStoryboardInput): SalesDecision {
  const category = detectSalesCategory(input);
  const mechanism = detectSalesMechanism(input, category);
  const storyArc = mechanism === "skin_transformation" || mechanism === "sun_shield"
    ? "problem_solution_proof_cta"
    : mechanism === "luxury_identity" || mechanism === "lip_desire"
      ? "luxury_aura_reveal_cta"
      : "hook_desire_trust_cta";
  const pacing = input.platform === "tiktok" || input.platform === "shorts" ? "fast" : input.goal === "premium" ? "cinematic" : "balanced";
  const priority = mechanism === "lip_desire" ? ["lips", "lipstick", "eyes", "skin"]
    : mechanism === "liquid_vortex" ? ["bottle", "liquid", "ingredient", "heritage"]
      : mechanism === "ingredient_explosion" ? ["product", "ingredient", "texture", "cta"]
        : mechanism === "sun_shield" ? ["sunlight", "shield", "skin", "product"]
          : mechanism === "skin_transformation" ? ["skin result", "transition", "product", "trust"]
            : mechanism === "luxury_identity" ? ["identity", "outfit", "face", "brand aura", "cta"]
              : ["product", "visual hook", "trust", "cta"];

  const visualHook: Record<SalesMechanism, string> = {
    lip_desire: "lipstick touches lips in a high-desire apply moment",
    skin_transformation: "skin result changes visibly and believably",
    sun_shield: "sunlight hits invisible shield and bends away",
    ingredient_explosion: "ingredients burst around product in a flavor explosion",
    liquid_vortex: "glossy liquid vortex pulls attention around the bottle",
    texture_proof: "macro texture detail reveals product quality",
    luxury_identity: "premium aura creates desire through model, outfit and runway identity",
    human_emotion: "human reaction transfers emotion",
    mini_world_story: "miniature craft world proves origin",
    product_dominance: "large centered product appears instantly"
  };

  return {
    category,
    mechanism,
    visualHook: visualHook[mechanism],
    storyArc,
    pacing,
    priority,
    reason: [`Category=${category}`, `Mechanism=${mechanism}`, `StoryArc=${storyArc}`, `Pacing=${pacing}`]
  };
}

export function lightingForSalesMechanism(m: SalesMechanism) {
  if (m === "lip_desire") return "soft diffused beauty key light, controlled lip highlight, matte skin";
  if (m === "sun_shield") return "golden sunlight, rim light, transparent shield refraction";
  if (m === "liquid_vortex") return "golden hour backlight through liquid, glossy highlights, cinematic shadows";
  if (m === "ingredient_explosion") return "warm commercial food lighting, crisp texture highlights";
  if (m === "luxury_identity") return "Dior/YSL-style soft spotlight, rim light, premium dark gradient, runway prestige";
  if (m === "texture_proof") return "macro commercial lighting, crisp micro texture highlights";
  return "premium commercial lighting, balanced highlights, clean shadows";
}

function sceneBase(input: SalesStoryboardInput, decision: SalesDecision): Omit<SalesScene, "sceneId" | "order" | "startSec" | "endSec" | "durationSec">[] {
  const product = input.productName;
  const m = decision.mechanism;
  const hookVisual = decision.visualHook;
  const lang = input.language || "vi";

  const hookText = lang === "vi" ? "Nhìn là muốn thử" : "You want to try this";
  const ctaText = lang === "vi" ? "Chốt visual winner" : "Lock the winning visual";

  if (decision.storyArc === "problem_solution_proof_cta") {
    return [
      {
        scenePurpose: "hook",
        visual: hookVisual,
        action: `Open with a sharp problem/desire contrast around ${product}.`,
        camera: "fast push-in, 9:16 social hook framing",
        lighting: lightingForSalesMechanism(m),
        motion: "fast pattern interrupt",
        overlayText: hookText,
        voiceover: lang === "vi" ? "Vấn đề nằm ở cảm giác đầu tiên." : "The first feeling decides everything.",
        retentionNote: "Pattern interrupt before 1s."
      },
      {
        scenePurpose: "desire",
        visual: `The product mechanism activates: ${hookVisual}.`,
        action: "Show transformation or shield logic in a believable commercial way.",
        camera: "medium to macro transition",
        lighting: lightingForSalesMechanism(m),
        motion: "visible transformation motion",
        retentionNote: "Visual proof keeps attention."
      },
      {
        scenePurpose: "proof",
        visual: `Close-up proof of ${product} result and texture.`,
        action: "Show result, ingredient, label or skin/product evidence.",
        camera: "macro insert + face/product proof",
        lighting: "clean trust lighting, precise highlights",
        motion: "slow detail reveal",
        retentionNote: "Trust beat before CTA."
      },
      {
        scenePurpose: "cta",
        visual: `${product} hero frame with clear CTA.`,
        action: "End on clean product/logo-safe hero frame.",
        camera: "centered commercial product hero",
        lighting: "premium clean studio light",
        motion: "hero hold",
        overlayText: ctaText,
        retentionNote: "CTA with product clarity."
      }
    ];
  }

  if (decision.storyArc === "luxury_aura_reveal_cta") {
    return [
      {
        scenePurpose: "hook",
        visual: hookVisual,
        action: `Open with model/beauty/product aura around ${product}.`,
        camera: "beauty close-up or runway identity close-up",
        lighting: lightingForSalesMechanism(m),
        motion: "slow premium push",
        overlayText: hookText,
        retentionNote: "Face/beauty hook creates desire."
      },
      {
        scenePurpose: "luxury_aura",
        visual: `Luxury atmosphere forms around ${product}.`,
        action: "Use fashion/beauty details, spotlight, model confidence, outfit texture.",
        camera: "wide → medium → macro luxury rhythm",
        lighting: lightingForSalesMechanism(m),
        motion: "cinematic orbit and fabric/skin highlight",
        retentionNote: "Aura beat increases perceived value."
      },
      {
        scenePurpose: "desire",
        visual: `Close desire moment: ${decision.priority.join(" → ")}.`,
        action: "Route attention from eyes/face to product or outfit detail.",
        camera: "macro detail + eye contact return",
        lighting: "soft contrast, commercial beauty highlights",
        motion: "attention route movement",
        retentionNote: "Attention routing creates buying desire."
      },
      {
        scenePurpose: "cta",
        visual: `${product} final commercial hero.`,
        action: "Final frame must be clean, memorable and conversion-ready.",
        camera: "hero frame, label/shape readable",
        lighting: "premium final spotlight",
        motion: "slow hero hold",
        overlayText: ctaText,
        retentionNote: "Clear final product/brand recall."
      }
    ];
  }

  return [
    {
      scenePurpose: "hook",
      visual: hookVisual,
      action: `${product} appears instantly with commercial attention route.`,
      camera: "hard cut + fast push",
      lighting: lightingForSalesMechanism(m),
      motion: "instant product dominance",
      overlayText: hookText,
      retentionNote: "Immediate product clarity."
    },
    {
      scenePurpose: "desire",
      visual: `Desire mechanism: ${hookVisual}.`,
      action: "Show why the product feels attractive.",
      camera: "medium to macro",
      lighting: lightingForSalesMechanism(m),
      motion: "dynamic reveal",
      retentionNote: "Desire beat."
    },
    {
      scenePurpose: "trust",
      visual: "Clean proof shot with product, ingredient, result or social cue.",
      action: "Add trust without slowing pace.",
      camera: "detail + proof insert",
      lighting: "trust lighting",
      motion: "steady proof hold",
      retentionNote: "Trust beat."
    },
    {
      scenePurpose: "cta",
      visual: `${product} hero CTA.`,
      action: "Close with final offer/product hero.",
      camera: "center hero",
      lighting: "premium final",
      motion: "hero hold",
      overlayText: ctaText,
      retentionNote: "CTA."
    }
  ];
}

export function buildSalesScenes(input: SalesStoryboardInput, decision: SalesDecision): SalesScene[] {
  const duration = input.duration || 15;
  const base = sceneBase(input, decision);
  const unit = duration / base.length;
  return base.map((scene, index) => ({
    ...scene,
    sceneId: `sales_scene_${index + 1}`,
    order: index + 1,
    startSec: Number((index * unit).toFixed(2)),
    endSec: Number(((index + 1) * unit).toFixed(2)),
    durationSec: Number(unit.toFixed(2))
  }));
}

export function compileSalesProviderPrompts(input: SalesStoryboardInput, decision: SalesDecision, scenes: SalesScene[]): SalesProviderPrompt[] {
  return scenes.map((scene) => ({
    sceneId: scene.sceneId,
    provider: decision.category === "fashion" || decision.mechanism === "luxury_identity" ? "veo" : "runway",
    prompt: [
      `Product: ${input.productName}`,
      `Category: ${decision.category}`,
      `Sales mechanism: ${decision.mechanism}`,
      `Scene purpose: ${scene.scenePurpose}`,
      `Visual: ${scene.visual}`,
      `Action: ${scene.action}`,
      `Camera: ${scene.camera}`,
      `Lighting: ${scene.lighting}`,
      `Motion: ${scene.motion}`,
      `Retention: ${scene.retentionNote}`,
      input.preserveIdentity ? "Preserve model identity and face consistency." : "",
      input.preserveProductShape ? "Preserve product shape, label, color and packaging." : "",
      input.constraints.join("\n")
    ].filter(Boolean).join("\n"),
    negativePrompt: "wrong product shape, unreadable label, identity drift, bad hands, bad anatomy, low quality, watermark, random text, off-brand composition",
    settings: {
      aspectRatio: input.aspectRatio || "9:16",
      durationSec: scene.durationSec,
      commercialSafety: true,
      preserveIdentity: input.preserveIdentity,
      preserveProductShape: input.preserveProductShape
    }
  }));
}

export function scoreSalesStoryboard(input: SalesStoryboardInput, decision: SalesDecision, scenes: SalesScene[]): SalesStoryboardScore {
  const hasHook = scenes.some((s) => s.scenePurpose === "hook");
  const hasProof = scenes.some((s) => s.scenePurpose === "proof" || s.scenePurpose === "trust");
  const hasCta = scenes.some((s) => s.scenePurpose === "cta");
  const fastPlatform = input.platform === "tiktok" || input.platform === "shorts";
  const productClarity = input.preserveProductShape ? 94 : 82;
  const hookStrength = hasHook ? (fastPlatform ? 94 : 88) : 60;
  const desire = decision.mechanism === "luxury_identity" || decision.mechanism === "lip_desire" ? 94 : 88;
  const trust = hasProof ? 90 : 78;
  const conversion = hasCta ? 91 : 70;
  const retention = fastPlatform ? 92 : 86;
  const risk = input.constraints.some((c) => /text|label|logo/i.test(c)) ? 18 : 10;
  const finalScore = Math.round(hookStrength * 0.22 + productClarity * 0.18 + desire * 0.18 + trust * 0.14 + conversion * 0.18 + retention * 0.10 - risk * 0.15);
  return {
    hookStrength,
    productClarity,
    desire,
    trust,
    conversion,
    retention,
    risk,
    finalScore,
    verdict: finalScore >= 88 ? "READY" : finalScore >= 78 ? "TEST" : "REBUILD",
    reasons: decision.reason.concat([
      `Hook=${hookStrength}`,
      `ProductClarity=${productClarity}`,
      `FinalScore=${finalScore}`
    ])
  };
}

export function generateSalesStoryboardV3ForV30(raw: unknown): SalesStoryboardOutput {
  const input = SalesStoryboardInputSchema.parse(raw);
  const decision = routeSalesStoryboard(input);
  const scenes = buildSalesScenes(input, decision);
  const providerPrompts = compileSalesProviderPrompts(input, decision, scenes);
  const score = scoreSalesStoryboard(input, decision, scenes);
  return {
    engineVersion: "auto_storyboard_engine_v3_sales_for_v30",
    input,
    decision,
    scenes,
    providerPrompts,
    score,
    exportJson: {
      productName: input.productName,
      decision,
      scenes,
      providerPrompts,
      score
    }
  };
}
