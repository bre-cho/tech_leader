import crypto from "node:crypto";
import path from "node:path";
import { JsonStore } from "@/lib/runtime/jsonStore";
import { decryptSecret, encryptSecret, maskSecret } from "@/lib/runtime/secretCrypto";

// -----------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------
export type KieAccountRecord = {
  id: string;
  label: string;
  encryptedApiKey: string;
  maskedApiKey: string;
  enabled: boolean;
  lastHealthStatus: "ok" | "failed" | "unknown";
  failCount: number;
  createdAt: string;
  updatedAt: string;
};

export type KieAccountPublic = Omit<KieAccountRecord, "encryptedApiKey">;

export type KieAccountsState = {
  accounts: KieAccountRecord[];
};

// -----------------------------------------------------------------------
// Persistence
// -----------------------------------------------------------------------
const DEFAULT_STATE: KieAccountsState = { accounts: [] };

const STORE = new JsonStore<KieAccountsState>(
  path.join(process.cwd(), "storage", "settings", "kie-accounts.json"),
  DEFAULT_STATE
);

function now() {
  return new Date().toISOString();
}

// -----------------------------------------------------------------------
// Store class
// -----------------------------------------------------------------------
export class KieAccountStore {
  listPublic(): KieAccountPublic[] {
    const state = STORE.read();
    return state.accounts.map(({ encryptedApiKey, ...rest }) => rest);
  }

  add(input: { label: string; apiKey: string; enabled?: boolean }) {
    const state = STORE.read();
    const rec: KieAccountRecord = {
      id: `kie_${crypto.randomBytes(8).toString("hex")}`,
      label: input.label,
      encryptedApiKey: encryptSecret(input.apiKey),
      maskedApiKey: maskSecret(input.apiKey),
      enabled: input.enabled ?? true,
      lastHealthStatus: "unknown",
      failCount: 0,
      createdAt: now(),
      updatedAt: now(),
    };
    state.accounts.push(rec);
    STORE.write(state);
    const { encryptedApiKey, ...pub } = rec;
    return pub;
  }

  update(input: { id: string; label?: string; apiKey?: string; enabled?: boolean }) {
    const state = STORE.read();
    const idx = state.accounts.findIndex((a) => a.id === input.id);
    if (idx < 0) throw new Error("KIE account not found.");
    const rec = state.accounts[idx];
    state.accounts[idx] = {
      ...rec,
      ...(input.label !== undefined ? { label: input.label } : {}),
      ...(input.apiKey !== undefined
        ? { encryptedApiKey: encryptSecret(input.apiKey), maskedApiKey: maskSecret(input.apiKey) }
        : {}),
      ...(input.enabled !== undefined ? { enabled: input.enabled } : {}),
      updatedAt: now(),
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

  /** Returns the decrypted API key of the first enabled account, or null. */
  resolveKey(): string | null {
    const state = STORE.read();
    const active = state.accounts.find((a) => a.enabled);
    if (!active) return null;
    try {
      return decryptSecret(active.encryptedApiKey);
    } catch {
      return null;
    }
  }

  markHealth(id: string, status: "ok" | "failed") {
    const state = STORE.read();
    const idx = state.accounts.findIndex((a) => a.id === id);
    if (idx < 0) return;
    state.accounts[idx] = {
      ...state.accounts[idx],
      lastHealthStatus: status,
      failCount: status === "failed" ? state.accounts[idx].failCount + 1 : 0,
      updatedAt: now(),
    };
    STORE.write(state);
  }
}

export const kieAccountStore = new KieAccountStore();
