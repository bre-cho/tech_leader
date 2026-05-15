export function verifyBeautyCommerceV28(output: {
  bananaMultiReference: any;
  femininityEngine: Record<string, any>;
  videoEngine: Record<string, any>;
  prompt: string;
  negativePrompt: string;
  videoPlan: any;
}) {
  const femScores = Object.values(output.femininityEngine).map((x: any) => Number(x.score ?? 0));
  const vidScores = Object.values(output.videoEngine).map((x: any) => Number(x.score ?? 0));
  const avgFem = Math.round(femScores.reduce((a, b) => a + b, 0) / femScores.length);
  const avgVid = Math.round(vidScores.reduce((a, b) => a + b, 0) / vidScores.length);

  const checks = {
    banana_multi_reference_ready: Number(output.bananaMultiReference.score) >= 80,
    femininity_engine_ready: avgFem >= 88,
    video_engine_ready: avgVid >= 88,
    prompt_has_commercial_psychology: output.prompt.includes("Commercial Beauty Psychology"),
    negative_prompt_blocks_explicit: output.negativePrompt.includes("explicit nudity"),
    video_plan_has_scenes: Array.isArray(output.videoPlan.scenes) && output.videoPlan.scenes.length >= 3,
    handoff_has_lipdub: Boolean(output.videoPlan.handoff?.lipdub),
    handoff_has_subtitle_runtime: Boolean(output.videoPlan.handoff?.subtitles)
  };

  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);

  return {
    passed: score >= 90,
    score,
    checks,
    engineAverages: { femininity: avgFem, video: avgVid },
    issues: Object.entries(checks).filter(([, v]) => !v).map(([k]) => k)
  };
}

export function scoreCommercialV28(verification: any, input: any) {
  const productBoost = input.productName ? 4 : 0;
  const refsBoost = Math.min(5, input.references.length);
  const channelBoost = input.channel === "tiktok" || input.channel === "livestream" ? 4 : 0;
  const finalScore = Math.min(100, Math.round(Number(verification.score) * 0.75 + 12 + productBoost + refsBoost + channelBoost));
  return {
    final_score: finalScore,
    pass: finalScore >= 90,
    predicted_ctr_range: finalScore >= 95 ? "4.0% - 6.5%" : finalScore >= 90 ? "3.0% - 4.8%" : "1.8% - 3.0%",
    winner_dna_ready: finalScore >= 92,
    reasoning: "score combines engine verification, product presence, references and TikTok/livestream fit"
  };
}
