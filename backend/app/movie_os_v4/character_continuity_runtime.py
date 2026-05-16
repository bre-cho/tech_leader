from .schemas import CharacterBible, MoodColorLensProfile


class CharacterContinuityRuntime:
    def build(self, prompt: str, mood: MoodColorLensProfile) -> CharacterBible:
        if mood.mood == "gothic_luxury":
            return CharacterBible(
                identity_lock="gothic ruby queen identity locked across all scenes",
                face="same regal adult face, pale luminous skin, intense gaze",
                costume="deep ruby velvet gown with black lace and gold trim",
                jewelry="ruby crown, ruby earrings, ruby necklace, forehead jewel",
                hairstyle="deep red curled royal hair with consistent volume",
                age="adult queen character",
                body_silhouette="royal feminine silhouette, structured shoulders, couture waist",
                makeup="ruby lips, smoky eye makeup, cinematic blush",
                continuity_rules=[
                    "Keep crown shape consistent.",
                    "Keep ruby jewelry placement stable.",
                    "Keep hairstyle volume and red tone stable.",
                    "Keep costume material velvet and lace.",
                    "No face drift between scenes.",
                ],
            )

        if mood.mood == "vogue_fantasy":
            return CharacterBible(
                identity_lock="fantasy couture model identity locked across all scenes",
                face="same adult editorial model face and pose confidence",
                costume="butterfly wing couture gown with violet emerald translucent panels",
                jewelry="fantasy earrings and delicate headpiece",
                hairstyle="sculpted runway updo with fantasy accessory",
                age="adult fashion model",
                body_silhouette="tall couture silhouette with dramatic wing span",
                makeup="editorial metallic eye makeup, glossy skin, sculpted cheekbones",
                continuity_rules=[
                    "Keep wing geometry consistent.",
                    "Keep violet emerald material language.",
                    "Keep runway posture and headpiece stable.",
                    "No wing shape randomization across scenes.",
                ],
            )

        if mood.mood == "ethereal_spiritual":
            return CharacterBible(
                identity_lock="ethereal woman identity locked across all scenes",
                face="same serene adult face, peaceful closed-eye or soft gaze expression",
                costume="flowing translucent earth-tone robe with golden fiber detail",
                jewelry="minimal natural spiritual jewelry",
                hairstyle="long auburn hair interacting with golden particles",
                age="adult spiritual heroine",
                body_silhouette="soft flowing silhouette with transparent fabric layers",
                makeup="natural glowing skin, minimal spiritual beauty makeup",
                continuity_rules=[
                    "Keep golden particle hair aura consistent.",
                    "Keep sunrise backlight direction.",
                    "Keep soft spiritual expression.",
                    "Keep robe fabric transparent and flowing.",
                ],
            )

        return CharacterBible(
            identity_lock="cinematic hero identity locked across all scenes",
            face="same hero face identity",
            costume="consistent mood-based costume",
            jewelry="consistent accessories",
            hairstyle="consistent hairstyle silhouette",
            age="adult cinematic character",
            body_silhouette="consistent cinematic silhouette",
            makeup="consistent cinematic makeup",
            continuity_rules=[
                "Maintain face identity.",
                "Maintain costume color palette.",
                "Maintain hairstyle and makeup.",
                "No character drift across scenes.",
            ],
        )


character_continuity_runtime = CharacterContinuityRuntime()
