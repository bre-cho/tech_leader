import crypto from "node:crypto";
import path from "node:path";
import { JsonStore } from "@/lib/runtime/jsonStore";
import { decryptSecret, encryptSecret, maskSecret } from "@/lib/runtime/secretCrypto";
import type {
  AccountRotationSettings,
  GoogleAccountCapability,
  GoogleAccountPublic,
  GoogleAccountRecord,
  GoogleAccountsState
} from "./accountTypes";

const DEFAULT_STATE: GoogleAccountsState = {
  accounts: [],
  rotation: { enabled: false, strategy: "round_robin", perScene: true },
  cursor: 0
};

const STORE = new JsonStore<GoogleAccountsState>(
  path.join(process.cwd(), "storage", "settings", "google-accounts.json"),
  DEFAULT_STATE
);

function now() {
  return new Date().toISOString();
}

export class GoogleAccountStore {
  listPublic(): { accounts: GoogleAccountPublic[]; rotation: AccountRotationSettings } {
    const state = STORE.read();
    return {
      accounts: state.accounts.map(({ encryptedApiKey, ...rest }) => rest),
      rotation: state.rotation
    };
  }

  add(input: { label: string; apiKey: string; enabled: boolean; capabilities: GoogleAccountCapability[]; quotaWeight: number }) {
    const state = STORE.read();
    const rec: GoogleAccountRecord = {
      id: `gacc_${crypto.randomBytes(8).toString("hex")}`,
      label: input.label,
      encryptedApiKey: encryptSecret(input.apiKey),
      maskedApiKey: maskSecret(input.apiKey),
      enabled: input.enabled,
      capabilities: input.capabilities,
      quotaWeight: input.quotaWeight,
      failCount: 0,
      lastHealthStatus: "unknown",
      createdAt: now(),
      updatedAt: now()
    };
    state.accounts.push(rec);
    STORE.write(state);
    const { encryptedApiKey, ...pub } = rec;
    return pub;
  }

  update(input: {
    id: string;
    label?: string;
    apiKey?: string;
    enabled?: boolean;
    capabilities?: GoogleAccountCapability[];
    quotaWeight?: number;
  }) {
    const state = STORE.read();
    const idx = state.accounts.findIndex((a) => a.id === input.id);
    if (idx < 0) throw new Error("Google account not found.");
    const rec = state.accounts[idx];
    state.accounts[idx] = {
      ...rec,
      ...(input.label !== undefined ? { label: input.label } : {}),
      ...(input.apiKey !== undefined ? { encryptedApiKey: encryptSecret(input.apiKey), maskedApiKey: maskSecret(input.apiKey) } : {}),
      ...(input.enabled !== undefined ? { enabled: input.enabled } : {}),
      ...(input.capabilities !== undefined ? { capabilities: input.capabilities } : {}),
      ...(input.quotaWeight !== undefined ? { quotaWeight: input.quotaWeight } : {}),
      updatedAt: now()
    };
    STORE.write(state);
    const { encryptedApiKey, ...pub } = state.accounts[idx];
    return pub;
  }

  remove(id: string) {
    const state = STORE.read();
    state.accounts = state.accounts.filter((a) => a.id !== id);
    STORE.write(state);
    return { removed: true };
  }

  setRotation(rotation: AccountRotationSettings) {
    const state = STORE.read();
    state.rotation = rotation;
    STORE.write(state);
    return rotation;
  }

  getApiKey(id: string) {
    const state = STORE.read();
    const rec = state.accounts.find((a) => a.id === id);
    if (!rec) throw new Error("Google account not found.");
    return decryptSecret(rec.encryptedApiKey);
  }

  select(capability: GoogleAccountCapability, sceneIndex = 0) {
    const state = STORE.read();
    const candidates = state.accounts.filter((a) => a.enabled && a.capabilities.includes(capability));
    if (candidates.length === 0) {
      const envKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      if (!envKey) throw new Error(`No Google account/API key available for ${capability}.`);
      return { accountId: "env", label: "ENV GEMINI_API_KEY", apiKey: envKey };
    }

    let selected: GoogleAccountRecord;
    if (!state.rotation.enabled) {
      selected = candidates[0];
    } else if (state.rotation.perScene) {
      selected = candidates[sceneIndex % candidates.length];
    } else if (state.rotation.strategy === "least_recent") {
      selected = [...candidates].sort((a, b) => (a.lastUsedAt || "").localeCompare(b.lastUsedAt || ""))[0];
    } else {
      selected = candidates[state.cursor % candidates.length];
      state.cursor = state.cursor + 1;
    }

    selected.lastUsedAt = now();
    STORE.write(state);
    return { accountId: selected.id, label: selected.label, apiKey: decryptSecret(selected.encryptedApiKey) };
  }

  markHealth(id: string, ok: boolean) {
    const state = STORE.read();
    const rec = state.accounts.find((a) => a.id === id);
    if (!rec) return;
    rec.lastHealthAt = now();
    rec.lastHealthStatus = ok ? "ok" : "failed";
    rec.failCount = ok ? 0 : rec.failCount + 1;
    rec.updatedAt = now();
    STORE.write(state);
  }
}
