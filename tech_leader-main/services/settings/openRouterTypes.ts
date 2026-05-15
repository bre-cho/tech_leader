import { z } from "zod";

export const OpenRouterSettingsUpdateSchema = z.object({
  apiKey: z.string().min(10).optional(),
  selectedModel: z.string().min(1).optional(),
  siteUrl: z.string().url().optional().or(z.literal("")).default(""),
  appTitle: z.string().optional().default("AI Creative OS"),
  enabled: z.boolean().optional()
});

export type OpenRouterSettings = {
  enabled: boolean;
  encryptedApiKey?: string;
  maskedApiKey?: string;
  selectedModel: string;
  siteUrl?: string;
  appTitle?: string;
  updatedAt?: string;
};
