import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

export function routeProvider(req: BeautyIdentityRuntimeRequest, visualRecipe: RuntimeReport): RuntimeReport {
  const hinted = (visualRecipe.data as any).recipe?.providerHint ?? "banana";
  const provider = req.provider === "auto" ? hinted : req.provider;

  const route = {
    selected: provider,
    fallbackOrder:
      provider === "banana" ? ["banana", "flux", "sdxl_comfy", "hidream"] :
      provider === "hidream" ? ["hidream", "banana", "flux", "sdxl_comfy"] :
      provider === "sdxl_comfy" ? ["sdxl_comfy", "flux", "banana", "hidream"] :
      ["flux", "banana", "sdxl_comfy", "hidream"],
    endpoints: {
      banana: "/api/providers/google-managed/nano-banana/generate",
      hidream: "/api/v1/hidream/commercial-visual/generate",
      flux: "/api/providers/flux/generate",
      sdxl_comfy: "/api/providers/comfyui/run"
    },
    reason:
      provider === "banana" ? "best for beauty consistency, KOL realism, commercial composition and multi-reference editing" :
      provider === "hidream" ? "best for cinematic luxury/editorial atmosphere and dramatic lighting" :
      provider === "sdxl_comfy" ? "best for precision control, outfit details, regional prompting and LoRA stacks" :
      "best for realism recovery and texture enhancement"
  };

  return {
    name: "ProviderRouter",
    score: 94,
    data: route,
    warnings: []
  };
}
