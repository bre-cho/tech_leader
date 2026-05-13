import { NextResponse } from "next/server";
import { GoogleAccountCreateSchema } from "@/services/accounts/accountTypes";
import { GoogleAccountStore } from "@/services/accounts/googleAccountStore";

export async function GET() {
  return NextResponse.json(new GoogleAccountStore().listPublic());
}

export async function POST(req: Request) {
  try {
    const body = GoogleAccountCreateSchema.parse(await req.json());
    const account = new GoogleAccountStore().add(body);
    return NextResponse.json(account);
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 400 });
  }
}
