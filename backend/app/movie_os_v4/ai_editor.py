from .schemas import AIEditorPlan, MoodColorLensProfile


class AIEditorV4:
    def build(self, mood: MoodColorLensProfile) -> AIEditorPlan:
        if mood.mood == "gothic_luxury":
            return AIEditorPlan(
                edit_style="dark luxury cinematic trailer edit",
                transitions=["ruby glint match cut", "velvet fade", "shadow dissolve"],
                pacing_rules=["hold eyes longer", "cut on jewel glints", "escalate slowly toward peak"],
                sound_design=["deep pulse", "royal room tone", "jewelry shimmer", "low cinematic hit"],
                subtitle_strategy="minimal serif subtitles in lower safe zone",
                color_grade="ruby-black-gold contrast grade",
            )

        if mood.mood == "vogue_fantasy":
            return AIEditorPlan(
                edit_style="haute couture editorial fashion film edit",
                transitions=["runway flash cut", "fabric motion dissolve", "spotlight wipe"],
                pacing_rules=["cut on pose changes", "hold couture silhouettes", "use macro details between wide reveals"],
                sound_design=["runway pulse", "camera flash", "crystal shimmer"],
                subtitle_strategy="magazine-style typography, minimal words",
                color_grade="violet emerald glossy editorial grade",
            )

        if mood.mood == "ethereal_spiritual":
            return AIEditorPlan(
                edit_style="poetic magic realism edit",
                transitions=["gold particle dissolve", "sun flare wipe", "breathing fade"],
                pacing_rules=["longer holds", "slow breath rhythm", "gentle reveal timing"],
                sound_design=["ambient wind", "soft chimes", "warm drone", "breath pause"],
                subtitle_strategy="soft poetic subtitles with generous spacing",
                color_grade="golden hour luminous grade",
            )

        return AIEditorPlan(
            edit_style="cinematic fantasy montage",
            transitions=["magic dissolve", "soft glow wipe", "motion match cut"],
            pacing_rules=["balance spectacle and emotion", "increase energy toward final scene"],
            sound_design=["cinematic ambience", "sparkle accents", "rising pulse"],
            subtitle_strategy="clean cinematic subtitles",
            color_grade="fantasy cinematic grade",
        )


ai_editor_v4 = AIEditorV4()
