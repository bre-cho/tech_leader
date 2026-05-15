const buckets = new Map<string, { count: number; resetAt: number }>();

export function bananaRateLimit(key: string, limit = 30, windowMs = 60_000) {
  const now = Date.now();
  const current = buckets.get(key);
  if (!current || current.resetAt < now) {
    buckets.set(key, { count: 1, resetAt: now + windowMs });
    return;
  }
  if (current.count >= limit) {
    throw new Error("Google Banana provider rate limit exceeded.");
  }
  current.count += 1;
}
