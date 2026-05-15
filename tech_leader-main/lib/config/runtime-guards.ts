export function isRuntimeMockAllowed(): boolean {
  return process.env.NODE_ENV !== "production";
}

export function isProductionLikeRuntime(): boolean {
  return process.env.NODE_ENV === "production";
}
