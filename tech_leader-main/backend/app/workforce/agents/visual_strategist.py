from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class VisualStrategistAgent(WorkforceAgent):
    name = "VisualStrategistAgent"

    def run(self, context: WorkforceContext):
        brief = context.brief
        industry = brief.industry.lower()
        if "beauty" in industry or "cosmetic" in industry or "spa" in industry:
            hook = "skin glow, eye contact, product close to face"
            trust = ["natural skin texture", "clean premium background", "soft luxury light"]
            attention = ["face/eyes", "product hero", "glow detail", "CTA"]
        elif "fmcg" in industry or "grooming" in industry:
            hook = "oversized benefit headline plus product hero motion"
            trust = ["readable label", "benefit proof", "clean packshot"]
            attention = ["headline", "cooling/energy effect", "product", "CTA"]
        elif "fashion" in industry:
            hook = "editorial silhouette and fabric realism"
            trust = ["natural body proportions", "fabric texture", "brand styling"]
            attention = ["pose", "silhouette", "product/style detail", "CTA"]
        else:
            hook = "problem-solution product reveal"
            trust = ["clarity", "proof cue", "readable CTA"]
            attention = ["headline", "product", "proof", "CTA"]

        output = {
            "hook": hook,
            "attention_route": attention,
            "trust_strategy": trust,
            "dopamine_triggers": ["contrast", "texture detail", "motion cue", "human emotion"],
            "conversion_strategy": ["outcome-first headline", "benefit proof near product", "low-friction CTA"],
        }
        context.decisions["visual_strategy"] = output
        return self.ok(output, 0.9)
