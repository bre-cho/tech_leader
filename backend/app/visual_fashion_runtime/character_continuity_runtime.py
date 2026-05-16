from .schemas import CharacterContinuityLock, VisualDNA


class CharacterContinuityRuntime:
    def build(self, dna: VisualDNA) -> CharacterContinuityLock:
        return CharacterContinuityLock(
            face_identity="keep same K-beauty face geometry, almond eyes, soft oval face, glossy natural lips, soft cheek volume",
            hair_identity=dna.hair_signature,
            outfit_rules=[
                "preserve palette from selected visual DNA",
                "keep accessory hierarchy consistent",
                "avoid random costume redesign",
                "keep luxury material language stable",
            ],
            makeup_rules=[
                "soft K-beauty glow",
                "clean eyeliner",
                "natural glossy lips unless red perfume scene",
                "skin texture realistic, not plastic",
            ],
            pose_rules=[
                "maintain feminine S-curve posing",
                "use hands elegantly around product or glasses",
                "avoid stiff static standing when motion brief is active",
            ],
            drift_guards=[
                "no face drift",
                "no hairstyle drift",
                "no outfit palette drift",
                "no jewelry mismatch",
                "no change in character age or proportions",
            ],
        )


character_continuity_runtime = CharacterContinuityRuntime()
