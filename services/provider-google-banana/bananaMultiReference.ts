import { GoogleBananaClient } from "./bananaClient";
import { BananaRequestSchema } from "./bananaTypes";

export async function bananaMultiReference(raw: unknown) {
  const req = BananaRequestSchema.parse({ mode: "multi_reference", ...raw });
  if (req.images.length < 2) throw new Error("Multi-reference generation requires at least two reference images.");
  return new GoogleBananaClient().run(req);
}
