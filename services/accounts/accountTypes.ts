import { z } from "zod";

export const GoogleAccountCreateSchema = z.object({
  label: z.string().min(1),
  apiKey: z.string().min(10),
  enabled: z.boolean().default(true),
  capabilities: z.array(z.enum(["nano_banana", "veo_3_1"])).default(["nano_banana", "veo_3_1"]),
  quotaWeight: z.number().min(1).max(100).default(1)
});

export const GoogleAccountUpdateSchema = z.object({
  id: z.string(),
  label: z.string().optional(),
  apiKey: z.string().min(10).optional(),
  enabled: z.boolean().optional(),
  capabilities: z.array(z.enum(["nano_banana", "veo_3_1"])).optional(),
  quotaWeight: z.number().min(1).max(100).optional()
});

export type GoogleAccountCapability = "nano_banana" | "veo_3_1";

export type GoogleAccountRecord = {
  id: string;
  label: string;
  encryptedApiKey: string;
  maskedApiKey: string;
  enabled: boolean;
  capabilities: GoogleAccountCapability[];
  quotaWeight: number;
  lastUsedAt?: string;
  lastHealthAt?: string;
  lastHealthStatus?: "ok" | "failed" | "unknown";
  failCount: number;
  createdAt: string;
  updatedAt: string;
};

export type GoogleAccountPublic = Omit<GoogleAccountRecord, "encryptedApiKey">;

export type AccountRotationSettings = {
  enabled: boolean;
  strategy: "round_robin" | "least_recent" | "weighted";
  perScene: boolean;
};

export type GoogleAccountsState = {
  accounts: GoogleAccountRecord[];
  rotation: AccountRotationSettings;
  cursor: number;
};
