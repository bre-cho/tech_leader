import path from "node:path";
import { JsonStore } from "@/lib/runtime/jsonStore";
import { decryptSecret, encryptSecret, maskSecret } from "@/lib/runtime/secretCrypto";
import type { OpenRouterSettings } from "./openRouterTypes";

const DEFAULT: OpenRouterSettings = {
  enabled: false,
  selectedModel: "openai/gpt-4o-mini",
  appTitle: "AI Creative OS"
};

const STORE = new JsonStore<OpenRouterSettings>(
  path.join(process.cwd(), "storage", "settings", "openrouter.json"),
  DEFAULT
);

export class OpenRouterStore {
  getPublic() {
    const { encryptedApiKey, ...pub } = STORE.read();
    return pub;
  }

  update(input: { apiKey?: string; selectedModel?: string; siteUrl?: string; appTitle?: string; enabled?: boolean }) {
    const current = STORE.read();
    const next: OpenRouterSettings = {
      ...current,
      ...(input.selectedModel !== undefined ? { selectedModel: input.selectedModel } : {}),
      ...(input.siteUrl !== undefined ? { siteUrl: input.siteUrl } : {}),
      ...(input.appTitle !== undefined ? { appTitle: input.appTitle } : {}),
      ...(input.enabled !== undefined ? { enabled: input.enabled } : {}),
      ...(input.apiKey !== undefined ? { encryptedApiKey: encryptSecret(input.apiKey), maskedApiKey: maskSecret(input.apiKey) } : {}),
      updatedAt: new Date().toISOString()
    };
    STORE.write(next);
    const { encryptedApiKey, ...pub } = next;
    return pub;
  }

  getAuth() {
    const s = STORE.read();
    if (!s.enabled) throw new Error("OpenRouter is disabled.");
    const apiKey = s.encryptedApiKey ? decryptSecret(s.encryptedApiKey) : process.env.OPENROUTER_API_KEY;
    if (!apiKey) throw new Error("Missing OpenRouter API key.");
    return {
      apiKey,
      model: s.selectedModel,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        ...(s.siteUrl ? { "HTTP-Referer": s.siteUrl } : {}),
        ...(s.appTitle ? { "X-Title": s.appTitle } : {})
      }
    };
  }
}
