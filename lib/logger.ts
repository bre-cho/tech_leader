type LogLevel = "info" | "warn" | "error";

function baseLog(level: LogLevel, ...args: unknown[]) {
  const target = level === "info" ? console.info : level === "warn" ? console.warn : console.error;
  target(...args);
}

export function log(level: LogLevel, ...args: unknown[]) {
  baseLog(level, ...args);
}

log.info = (...args: unknown[]) => baseLog("info", ...args);
log.warn = (...args: unknown[]) => baseLog("warn", ...args);
log.error = (...args: unknown[]) => baseLog("error", ...args);

