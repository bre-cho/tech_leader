export type LogLevel = "debug" | "info" | "warn" | "error";

export function log(
  level: LogLevel,
  scope: string,
  message: string,
  meta: Record<string, unknown> = {}
): void {
  const sink = level === "debug" ? console.debug : level === "info" ? console.info : level === "warn" ? console.warn : console.error;
  sink(`[${scope}] ${message}`, meta);
}
