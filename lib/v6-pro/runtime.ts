export type V6ScoredVariant = {
  prompt?: string;
  score?: number;
  [key: string]: unknown;
};

export type V6Winner = {
  prompt?: string;
  hook?: string;
  score?: {
    total?: number;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type RunAdsFactoryV6ProResult = {
  industry: string;
  winner: V6Winner | null;
  scored_variants: Record<string, V6ScoredVariant>;
  next_hints?: string[];
  [key: string]: unknown;
};

export async function runAdsFactoryV6Pro(_: Record<string, unknown>): Promise<RunAdsFactoryV6ProResult> {
  return {
    industry: "general",
    winner: null,
    scored_variants: {},
    next_hints: [],
  };
}
