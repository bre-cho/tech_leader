import { GoogleBananaClient } from "./bananaClient";
import { BananaRequestSchema } from "./bananaTypes";

export async function bananaImageEdit(raw: unknown) {
  const req = BananaRequestSchema.parse({ mode: "edit", ...(raw as object) });
  if (req.images.length < 1) throw new Error("Image edit requires at least one input image.");
  return new GoogleBananaClient().run(req);
}
