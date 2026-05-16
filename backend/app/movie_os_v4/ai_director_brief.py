from .schemas import AIDirectorBrief


class AIDirectorBriefBuilder:
    def build(self, prompt: str) -> AIDirectorBrief:
        text = prompt.lower()

        if "queen" in text or "gothic" in text:
            genre = "dark fantasy cinematic trailer"
            emotion = "awe, power, seduction, mystery"
            promise = "a regal fantasy heroine revealed through ruby light, dramatic camera movement, and transformation rhythm"
        elif "vogue" in text or "fashion" in text or "couture" in text:
            genre = "haute couture fantasy fashion film"
            emotion = "desire, elegance, aspiration"
            promise = "a high-fashion cinematic world with editorial composition and couture motion"
        elif "spiritual" in text or "ethereal" in text or "golden" in text:
            genre = "ethereal magic realism film"
            emotion = "peace, wonder, transcendence"
            promise = "a poetic sunrise world with glowing particles, breath timing, and emotional stillness"
        else:
            genre = "cinematic fantasy short film"
            emotion = "curiosity, wonder, cinematic payoff"
            promise = "a visually memorable story with a clear emotional arc"

        return AIDirectorBrief(
            logline=f"A cinematic movie generated from: {prompt}",
            genre=genre,
            audience_emotion=emotion,
            visual_promise=promise,
            director_intent="Turn a simple prompt into an autonomous cinematic production plan with continuity, rhythm, and sequential runtime.",
            success_criteria=[
                "Strong first-frame hook",
                "Consistent character identity across scenes",
                "Clear emotional escalation",
                "Stable provider runtime with concurrency 1",
                "Final movie assembly ready for export",
            ],
        )


ai_director_brief_builder = AIDirectorBriefBuilder()
