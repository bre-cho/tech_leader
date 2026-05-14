export type LogLevel = "debug" | "info" | "warn" | "error";
const sinks: Record<LogLevel, (...args: unknown[]) => void> = {
  debug: console.debug,
  info: console.info,
  warn: console.warn,
  error: console.error,
};

export function log(
  level: LogLevel,
  scope: string,
  message: string,
  meta: Record<string, unknown> = {}
): void {
  const sink = sinks[level];
  sink(`[${scope}] ${message}`, meta);
}
