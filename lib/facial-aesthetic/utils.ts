export function clampScore(value: number): number {
  if (Number.isNaN(value)) return 0;
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function avg(values: number[]): number {
  if (!values.length) return 0;
  return clampScore(values.reduce((a, b) => a + b, 0) / values.length);
}

export function includesAny(text: string | undefined, words: string[]): boolean {
  const s = (text ?? "").toLowerCase();
  return words.some((w) => s.includes(w.toLowerCase()));
}

export function scoreByTraits(base: number, boosts: Array<[boolean, number]>, penalties: Array<[boolean, number]> = []): number {
  let score = base;
  for (const [ok, delta] of boosts) if (ok) score += delta;
  for (const [bad, delta] of penalties) if (bad) score -= delta;
  return clampScore(score);
}

export function joinPrompt(parts: Array<string | undefined | false>): string {
  return parts.filter(Boolean).join(", ").replace(/\s+/g, " ").trim();
}
