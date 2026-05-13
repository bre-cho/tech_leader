from __future__ import annotations

import uuid
from app.workforce.contracts import (
    WorkforceRunRequest, WorkforceRunResponse, WorkforceContext
)
from app.workforce.agents.creative_director import CreativeDirectorAgent
from app.workforce.agents.visual_strategist import VisualStrategistAgent
from app.workforce.agents.composition import CompositionAgent
from app.workforce.agents.typography import TypographyAgent
from app.workforce.agents.brand_consistency import BrandConsistencyAgent
from app.workforce.agents.conversion import ConversionOptimizationAgent
from app.workforce.agents.motion import MotionThinkingAgent
from app.workforce.agents.industry import IndustryIntelligenceAgent
from app.workforce.agents.design_qa import DesignQAAgent


class MultiAgentWorkforceOrchestrator:
    def __init__(self):
        # Order matters: upstream agents create context used by downstream agents.
        self.agents = [
            IndustryIntelligenceAgent(),
            CreativeDirectorAgent(),
            VisualStrategistAgent(),
            BrandConsistencyAgent(),
            CompositionAgent(),
            TypographyAgent(),
            ConversionOptimizationAgent(),
            MotionThinkingAgent(),
            DesignQAAgent(),
        ]

    def run(self, request: WorkforceRunRequest) -> WorkforceRunResponse:
        context = WorkforceContext(brief=request.brief)
        results = []

        for agent in self.agents:
            result = agent.run(context)
            results.append(result)

        final_prompt, negative_prompt = self._compile_prompt(context)
        storyboard = context.decisions.get("motion", {}).get("storyboard", [])
        qa = results[-1].output
        verification_score = qa.get("score", 0)
        promotion_status = "PROMOTED_TO_WORKFLOW_RUNTIME" if verification_score >= 90 else "BLOCKED_BY_QA"

        winner_dna = {
            "industry": request.brief.industry,
            "brand_name": request.brief.brand_name,
            "attention_route": context.decisions.get("visual_strategy", {}).get("attention_route", []),
            "colors": context.design_system.get("colors", []),
            "typography": context.decisions.get("typography", {}),
            "conversion": context.decisions.get("conversion", {}),
            "storyboard_pattern": storyboard,
            "verification_score": verification_score,
        }

        return WorkforceRunResponse(
            run_id="workforce_" + uuid.uuid4().hex[:12],
            status="completed",
            context=context,
            agent_results=results,
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            storyboard=storyboard,
            verification_score=verification_score,
            promotion_status=promotion_status,
            winner_dna=winner_dna,
        )

    def _compile_prompt(self, context: WorkforceContext):
        b = context.brief
        d = context.decisions
        prompt = f'''
AI COMMERCIAL DESIGN WORKFORCE OUTPUT

Brand: {b.brand_name}
Industry: {b.industry}
Product: {b.product_name} ({b.product_type})
Audience: {b.target_audience}
Goal: {b.campaign_goal}
Channel: {b.channel}

Creative Direction:
{d.get("creative_direction", {})}

Visual Strategy:
{d.get("visual_strategy", {})}

Brand System:
{context.design_system}

Composition Canvas:
{context.canvas_regions}

Typography:
{d.get("typography", {})}

Conversion Logic:
{d.get("conversion", {})}

Motion / Poster-to-Video Logic:
{d.get("motion", {})}

Render a premium, commercial, conversion-focused creative asset.
It must route attention intentionally, preserve brand consistency, keep product readable,
use typography-safe regions, and prepare for poster-to-video expansion.
'''
        negative = "generic AI output, distorted logo, unreadable text, broken anatomy, fake product, clutter, low contrast, off-brand colors"
        return prompt.strip(), negative
