# V30 — Storyboard Agent: London Fashion Week Runtime

## Analysis of provided storyboard sheets

The reference sheets show a complete fashion-week film structure:

```text
I. SETUP      01-25
II. BACKSTAGE 26-60
III. RUNWAY   61-130
IV. AFTER PARTY 131-160
```

The Facebook reel URL could not be fetched by the browsing tool because Facebook throttled the request, so the implementation is grounded in the storyboard sheets you provided.

## Core upgrade

This patch upgrades Storyboard Agent from simple scene splitting into a real production storyboard runtime:

```text
Event Concept
→ Phase Blueprint
→ 160-Shot Catalog
→ Camera/Motion/Emotion Beat
→ Identity Continuity Contract
→ Retention Pacing Map
→ Provider Batch Compiler
→ Verification Gate
→ Artifact Contract
```

## New files

```text
lib/storyboard-v30/
  types.ts
  lfwShotCatalog.ts
  shotPromptCompiler.ts
  storyboardPlanner.ts
  continuityEngine.ts
  retentionEngine.ts
  providerBatchCompiler.ts
  storyboardAgentRuntime.ts

app/api/storyboard/v30/run/route.ts
app/api/storyboard/v30/provider-batches/route.ts
components/storyboard-v30/StoryboardV30Studio.tsx
app/storyboard-v30/page.tsx
tests/v30-storyboard-agent.test.ts
```

## API

```bash
POST /api/storyboard/v30/run
POST /api/storyboard/v30/provider-batches
```

## UI

```text
/storyboard-v30
```

## Provider handoff

```text
Still keyframes:
- HiDream
- Banana
- ComfyUI

Video shots:
- Veo
- Runway
- Kling
- LTX

Motion fallback:
- Runway
- Kling
```

## Run

```bash
npm install
npm run test:v30
npm run dev
```

## Production notes

- Shot prompts include identity, wardrobe, hair/makeup continuity.
- Runway shots use telephoto and tracking language.
- Backstage uses close-up/macro/detail progression.
- After party switches to neon, social proof and closure.
- Retention map alternates wide context, detail, beauty close-up, reaction and payoff.
