import { compileBananaCommercialPrompt } from "../services/provider-google-banana/bananaCommercialPrompt";
import { BananaRequestSchema } from "../services/provider-google-banana/bananaTypes";
import { scoreBananaCommercial } from "../services/provider-google-banana/bananaCommercialScoring";

const req = BananaRequestSchema.parse({
  mode: "commercial_poster",
  prompt: "Beauty ad poster with product bottle, headline and CTA",
  outputDir: "storage/test"
});

const prompt = compileBananaCommercialPrompt(req);
if (!prompt.includes("Commercial constraints")) throw new Error("prompt compiler failed");
if (!prompt.includes("Poster rules")) throw new Error("poster rules missing");

const score = scoreBananaCommercial(req, [{
  artifactId: "art_test",
  type: "image",
  path: "x.png",
  mimeType: "image/png",
  sizeBytes: 10,
  checksumSha256: "abc",
  provider: "google-banana",
  model: req.model,
  metadata: {}
}]);

if (!score.pass) throw new Error("commercial scoring failed");

console.log("Google Banana provider logic test passed", score.final_score);
