import type { StoryboardRequest, PhasePlan, ShotSpec, PhaseName } from "./types";
import { PHASE_BLUEPRINTS } from "./lfwShotCatalog";
import { compileShotPrompt, providerPayload } from "./shotPromptCompiler";

const PHASE_RANGES: Record<PhaseName, { start: number; end: number; sourceStart: number; sourceEnd: number }> = {
  setup: { start: 1, end: 25, sourceStart: 1, sourceEnd: 25 },
  backstage: { start: 26, end: 60, sourceStart: 26, sourceEnd: 60 },
  runway: { start: 61, end: 130, sourceStart: 61, sourceEnd: 130 },
  after_party: { start: 131, end: 160, sourceStart: 131, sourceEnd: 160 }
};

export function planStoryboard(req: StoryboardRequest): PhasePlan[] {
  const phases: PhasePlan[] = [];
  const requested = req.requestedPhases;
  const totalCatalogShots = requested.reduce((sum, p) => sum + PHASE_BLUEPRINTS[p].shots.length, 0);
  const durationUnit = req.targetDurationSec / Math.min(req.totalShots, totalCatalogShots);
  let globalId = 1;

  for (const phase of requested) {
    const blueprint = PHASE_BLUEPRINTS[phase];
    const range = PHASE_RANGES[phase];
    const phaseShots: ShotSpec[] = [];

    blueprint.shots.forEach((base, idx) => {
      if (globalId > req.totalShots) return;
      const id = globalId++;
      const durationSec = Number(Math.max(1.5, Math.min(6, durationUnit)).toFixed(2));
      const lens = inferLens(base.camera, phase);
      const continuityTags = [
        `phase:${phase}`,
        `location:${req.location}`,
        `character:${req.mainCharacter}`,
        `emotion:${base.emotionBeat}`,
        `focus:${base.subjectFocus}`
      ];

      const partial = {
        id,
        phase,
        title: base.title,
        description: base.description,
        camera: base.camera,
        lens,
        movement: base.movement,
        durationSec,
        subjectFocus: base.subjectFocus,
        emotionBeat: base.emotionBeat,
        continuityTags
      };

      const compiled = compileShotPrompt(req, partial);
      const shot: ShotSpec = {
        ...partial,
        prompt: compiled.prompt,
        negativePrompt: compiled.negativePrompt,
        providerPayload: {}
      };
      shot.providerPayload = providerPayload(req, shot);
      phaseShots.push(shot);
    });

    if (phaseShots.length) {
      phases.push({
        phase,
        title: blueprint.title,
        startShot: phaseShots[0].id,
        endShot: phaseShots[phaseShots.length - 1].id,
        purpose: blueprint.purpose,
        retentionRole: blueprint.retentionRole,
        shots: phaseShots
      });
    }
  }

  return phases;
}

function inferLens(camera: string, phase: PhaseName) {
  if (/macro|insert|close|cận/i.test(camera)) return "85mm macro / 100mm detail lens";
  if (/wide|toàn|flycam|establishing/i.test(camera)) return "24mm wide cinematic lens";
  if (/tele|runway|frontal/i.test(camera) || phase === "runway") return "70-200mm runway telephoto";
  return "35mm editorial documentary lens";
}
