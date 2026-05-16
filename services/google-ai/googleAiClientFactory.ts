import { GoogleGenAI } from "@google/genai";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";
import type { GoogleAccountCapability } from "@/services/accounts/accountTypes";

export function resolveGoogleAiForCapability(capability: GoogleAccountCapability, sceneIndex = 0) {
  return new GoogleAccountStore().select(capability, sceneIndex);
}

export function createGoogleAiForCapability(capability: GoogleAccountCapability, sceneIndex = 0) {
  const selected = resolveGoogleAiForCapability(capability, sceneIndex);
  return {
    ai: new GoogleGenAI({ apiKey: selected.apiKey }),
    account: { id: selected.accountId, label: selected.label }
  };
}
