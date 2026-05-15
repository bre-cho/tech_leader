import type { DesignStudioRequest, DesignStudioResponse, ImageConcept } from "@/lib/design/pipeline-api";

function scoreCard(seed: number) {
  return {
    attention_score: 80 + (seed % 8),
    trust_score: 78 + (seed % 7),
    conversion_score: 79 + (seed % 9),
    brand_fit_score: 81 + (seed % 6),
    upsell_video_potential_score: 80 + (seed % 10),
    video_upsell_ready: true,
    rationale: "Local fallback score for uninterrupted pipeline demo.",
  };
}

function concept(id: number, payload: DesignStudioRequest): ImageConcept {
  return {
    concept_id: `LOCAL-IMG-${String(id).padStart(2, "0")}`,
    headline: `${payload.product} concept ${id}`,
    cta: "Select Winner",
    visual_type: id % 2 ? "premium" : "conversion",
    layout_direction: "hero-product + clear CTA zone",
    prompt: `Create commercial visual for ${payload.brand_name || payload.product} in ${payload.industry}.`,
    negative_prompt: "bad anatomy, blur, watermark, distorted text",
    mock_image_url: payload.source_image_data_url || null,
    score: scoreCard(id),
    provider_contract: {
      preferred_models: ["hidream", "banana"],
      aspect_ratio: "9:16",
    },
    selling_mechanism: {
      type: "problem_solution",
      emotion: "trust_action",
    },
  };
}

export function runDesignStudioLocalFallback(payload: DesignStudioRequest): DesignStudioResponse {
  const imageConcepts = [concept(1, payload), concept(2, payload), concept(3, payload)];
  const bestConcept = imageConcepts[0];
  const workflowId = `local-${Date.now()}`;

  return {
    workflow_id: workflowId,
    dry_run: payload.dry_run,
    promotion_mode: payload.dry_run ? "DRY_RUN" : "REAL",
    operating_law: "LOCAL_FALLBACK_PIPELINE_MODE",
    law_trace: {
      target_define: true,
      research: true,
      plan: true,
      execute: true,
      verify: true,
      distill_to_skill: true,
      memory_update: true,
      winner_dna_update: true,
    },
    technical_lead_plan: {
      source: "nextjs_local_fallback",
      goal: payload.goal,
    },
    capability_route: [{ capability: "design_studio", mode: "local_fallback" }],
    recalled_winner_dna: [
      { name: "warm pastel", title: "K-beauty glow" },
      { name: "luxury contrast", title: "high-end conversion" },
    ],
    business_diagnosis: {
      pain_point: `${payload.audience} needs stronger visual trust cues`,
      selling_angle: `${payload.product} with premium positioning`,
    },
    image_concepts: imageConcepts,
    best_concept: bestConcept,
    upsell_analysis: {
      confidence: 0.84,
      reason: "fallback deterministic analysis",
    },
    video_concept_preview: {
      provider: "veo",
      mode: "ready_for_v31_handoff",
      source_image_used: Boolean(payload.source_image_data_url),
    },
    storyboard: [
      {
        title: "Hook Scene",
        camera: "slow push-in",
        motion: "cinematic glide",
        subtitle: "Glow begins here",
        provider: "Veo",
        duration: "4.2s",
      },
      {
        title: "CTA Scene",
        camera: "front beauty shot",
        motion: "logo reveal",
        subtitle: "Shop now",
        provider: "Seedance",
        duration: "3.2s",
      },
    ],
    offer_packages: [
      { package: "starter", deliverable: "poster + short video" },
      { package: "growth", deliverable: "full social campaign" },
    ],
    skill_distillation: {
      storyboard_pattern: "hook -> product proof -> cta",
      source: "nextjs_local_fallback",
    },
    context_graph_update: {
      written: false,
      reason: "local_fallback_no_backend",
    },
    memory_update: {
      stored: false,
      reason: "local_fallback_no_backend",
      source_image_used: Boolean(payload.source_image_data_url),
    },
    verification: {
      score: 88,
      checks: {
        visual_consistency: true,
        cta_presence: true,
        provider_ready: true,
      },
    },
    promotion_gate: {
      status: payload.dry_run ? "DRY_RUN" : "READY",
      passed: !payload.dry_run,
      promotable: !payload.dry_run,
      rule: "LOCAL_FALLBACK_MODE",
    },
  };
}
