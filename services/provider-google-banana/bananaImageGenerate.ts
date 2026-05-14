import { GoogleBananaClient } from "./bananaClient";
import { BananaRequestSchema } from "./bananaTypes";

export async function bananaImageGenerate(raw: unknown) {
  const req = BananaRequestSchema.parse({ mode: "generate", ...(raw as object) });
  return new GoogleBananaClient().run(req);
}
