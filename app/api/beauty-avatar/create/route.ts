import { createBeautyAvatar, BeautyAvatarRequest } from "@/lib/beauty-avatar/beautyAvatarGenerator";

export async function POST(request: Request) {
  try {
    const payload = (await request.json()) as BeautyAvatarRequest;
    const result = createBeautyAvatar(payload);

    return Response.json(result, { status: 200 });
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 }
    );
  }
}
