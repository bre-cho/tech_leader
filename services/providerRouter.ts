import { STORYBOARD_PROVIDERS, type StoryboardProvider } from "@/lib/contracts/providerContract";

export type ProviderName =
  | "google-banana"
  | "flux"
  | "sdxl"
  | StoryboardProvider;

const storyboardProviders = new Set<string>(STORYBOARD_PROVIDERS);

export function normalizeProviderName(provider: string): ProviderName {
  if (provider === "banana") return "google-banana";
  if (storyboardProviders.has(provider)) return provider as StoryboardProvider;
  if (provider === "google-banana" || provider === "flux" || provider === "sdxl") return provider;
  throw new Error(`Unsupported provider: ${provider}`);
}

export function routeProvider(task: {
  category?: string;
  needsText?: boolean;
  hasReferences?: boolean;
  needsGraphExecution?: boolean;
  needsCinematic?: boolean;
  preferredProvider?: string;
}): ProviderName {
  if (task.preferredProvider) return normalizeProviderName(task.preferredProvider);
  if (task.needsGraphExecution) return "comfyui";
  if (task.needsCinematic) return "hidream";
  if (task.needsText || task.hasReferences || task.category === "commercial") return "google-banana";
  return "google-banana";
}
