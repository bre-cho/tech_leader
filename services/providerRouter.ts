export type ProviderName = "google-banana" | "flux" | "sdxl" | "hidream" | "comfyui";

export function routeProvider(task: {
  category?: string;
  needsText?: boolean;
  hasReferences?: boolean;
  needsGraphExecution?: boolean;
  needsCinematic?: boolean;
}): ProviderName {
  if (task.needsGraphExecution) return "comfyui";
  if (task.needsCinematic) return "hidream";
  if (task.needsText || task.hasReferences || task.category === "commercial") return "google-banana";
  return "google-banana";
}
