import path from "node:path";

import { STORYBOARD_PROVIDERS } from "../lib/contracts/providerContract";
import { resolveStorageOutputDir } from "../lib/runtime/safeOutputDir";
import { normalizeProviderName } from "../services/providerRouter";

const safeDir = resolveStorageOutputDir("storage/test/runtime-guard");
if (!safeDir.endsWith(path.join("storage", "test", "runtime-guard"))) {
  throw new Error(`Expected normalized storage path, got ${safeDir}`);
}

let blocked = false;
try {
  resolveStorageOutputDir("../escape");
} catch {
  blocked = true;
}

if (!blocked) {
  throw new Error("Expected outputDir traversal attempt to be blocked");
}

for (const provider of STORYBOARD_PROVIDERS) {
  const normalized = normalizeProviderName(provider);
  if (provider === "banana") {
    if (normalized !== "google-banana") {
      throw new Error("Expected banana to normalize to google-banana");
    }
    continue;
  }
  if (normalized !== provider) {
    throw new Error(`Provider mapping mismatch for ${provider}`);
  }
}

console.log("Runtime guards regression test passed");
