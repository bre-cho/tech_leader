import path from "node:path";

const STORAGE_ROOT = path.resolve(process.cwd(), "storage");

function isInsideStorage(absPath: string): boolean {
  return absPath === STORAGE_ROOT || absPath.startsWith(`${STORAGE_ROOT}${path.sep}`);
}

export function resolveStorageOutputDir(outputDir?: string, fallback = "storage/runtime"): string {
  const raw = (outputDir ?? fallback).trim();
  const normalizedInput = (raw || fallback).replace(/\\/g, "/");
  const absolute = path.resolve(process.cwd(), normalizedInput);
  const normalizedAbsolute = path.normalize(absolute);

  if (!isInsideStorage(normalizedAbsolute)) {
    throw new Error(`outputDir must stay inside storage/: ${raw || fallback}`);
  }

  return normalizedAbsolute;
}
