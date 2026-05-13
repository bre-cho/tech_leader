import { GoogleGenAI } from "@google/genai";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";
import type { GoogleAccountCapability } from "@/services/accounts/accountTypes";

export function createGoogleAiForCapability(capability: GoogleAccountCapability, sceneIndex = 0) {
  const selected = new GoogleAccountStore().select(capability, sceneIndex);
  return {
    ai: new GoogleGenAI({ apiKey: selected.apiKey }),
    account: { id: selected.accountId, label: selected.label }
  };
}
