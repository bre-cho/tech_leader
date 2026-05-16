from .schemas import MoodColorLensProfile


class MoodColorLensEngine:
    def detect(self, prompt: str) -> MoodColorLensProfile:
        text = prompt.lower()

        if "gothic" in text or "ruby" in text or "queen" in text:
            return MoodColorLensProfile(
                mood="gothic_luxury",
                secondary_moods=["dark_feminine", "fantasy", "royal"],
                lighting="ruby velvet low-key cinematic lighting with gold rim highlights",
                lens="85mm portrait lens, shallow depth of field",
                color_script=["deep ruby", "black velvet", "antique gold", "soft skin highlight"],
                texture_language=["velvet", "ruby gemstone", "black lace", "polished gold"],
                transition_language=["ruby glint match cut", "velvet fade", "shadow dissolve"],
                soundtrack_direction="deep cinematic pulse, royal ambience, jewelry shimmer",
            )

        if "vogue" in text or "couture" in text or "fashion" in text:
            return MoodColorLensProfile(
                mood="vogue_fantasy",
                secondary_moods=["luxury", "editorial", "runway"],
                lighting="high-fashion editorial spotlight with glossy runway reflections",
                lens="50mm editorial fashion lens",
                color_script=["violet blue", "emerald green", "silver highlight", "moonlit black"],
                texture_language=["translucent wings", "crystal fabric", "reflective runway", "editorial haze"],
                transition_language=["runway flash cut", "fabric motion dissolve", "spotlight wipe"],
                soundtrack_direction="runway pulse, crystal shimmer, cinematic fashion impact",
            )

        if "spiritual" in text or "ethereal" in text or "golden" in text:
            return MoodColorLensProfile(
                mood="ethereal_spiritual",
                secondary_moods=["emotional", "magic_realism", "sunrise"],
                lighting="golden hour backlight with glowing particle atmosphere",
                lens="35mm natural cinematic lens",
                color_script=["warm gold", "soft amber", "misty green", "skin glow"],
                texture_language=["transparent fabric", "hair particles", "sun flare", "dust glow"],
                transition_language=["gold particle dissolve", "sun flare wipe", "breathing fade"],
                soundtrack_direction="ambient wind, soft chimes, breath-like musical pulse",
            )

        return MoodColorLensProfile(
            mood="cinematic_fantasy",
            secondary_moods=["luxury", "emotional"],
            lighting="magical volumetric cinematic light",
            lens="35mm fantasy cinema lens",
            color_script=["violet", "emerald", "moonlit blue", "soft gold"],
            texture_language=["sparkles", "mist", "cinematic costume", "glowing atmosphere"],
            transition_language=["magic dissolve", "soft glow wipe", "motion match cut"],
            soundtrack_direction="cinematic fantasy ambience with rising emotional pulse",
        )


mood_color_lens_engine = MoodColorLensEngine()
