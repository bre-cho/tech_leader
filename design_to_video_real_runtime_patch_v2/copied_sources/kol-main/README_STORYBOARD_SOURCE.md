# AUTO STORYBOARD ENGINE V2 FULL BACKEND

Production-oriented MVP patch pack for poster → storyboard → provider prompt export.

## Quick Start
```bash
pip install -r requirements.txt
./scripts/smoke_test.sh
./scripts/run_local.sh
```

## Endpoint
```txt
POST /api/storyboard/generate-v2
POST /api/storyboard/render-ready
```

## What it builds
- 3 storyboard variants: trust, viral, conversion
- 15s/30s scene structure
- Camera/motion/lighting planning
- Provider prompts for Veo/Runway/Kling/Seedance
- Scorecard for CTR/Attention/Trust/Conversion

Read `docs/` for integration steps.
