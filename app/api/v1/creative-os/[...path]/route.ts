import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE =
  process.env.BACKEND_API_BASE ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://127.0.0.1:8000";

const PROXY_TIMEOUT_MS = Number(process.env.CREATIVE_OS_PROXY_TIMEOUT_MS || 30000);

function stripTrailingSlash(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function buildTargetUrl(request: NextRequest, path: string[]): URL {
  const base = stripTrailingSlash(BACKEND_BASE);
  const suffix = path.length > 0 ? `/${path.join("/")}` : "";
  const target = new URL(`${base}/api/v1/creative-os${suffix}`);

  request.nextUrl.searchParams.forEach((value, key) => {
    target.searchParams.append(key, value);
  });

  return target;
}

function sanitizeRequestHeaders(input: Headers): Headers {
  const headers = new Headers(input);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");
  return headers;
}

function sanitizeResponseHeaders(input: Headers): Headers {
  const headers = new Headers(input);
  headers.delete("content-encoding");
  headers.delete("transfer-encoding");
  headers.delete("connection");
  return headers;
}

async function proxyToBackend(request: NextRequest, path: string[]): Promise<NextResponse> {
  const target = buildTargetUrl(request, path);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), PROXY_TIMEOUT_MS);

  try {
    const body = request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.arrayBuffer();

    const response = await fetch(target, {
      method: request.method,
      headers: sanitizeRequestHeaders(request.headers),
      body,
      signal: controller.signal,
      cache: "no-store",
    });

    const responseBody = await response.arrayBuffer();
    return new NextResponse(responseBody, {
      status: response.status,
      headers: sanitizeResponseHeaders(response.headers),
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      return NextResponse.json(
        {
          detail: `Creative OS proxy timeout after ${Math.round(PROXY_TIMEOUT_MS / 1000)}s`,
          backend_base: BACKEND_BASE,
        },
        { status: 504 },
      );
    }

    return NextResponse.json(
      {
        detail: "Creative OS proxy cannot reach backend service",
        backend_base: BACKEND_BASE,
      },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
}

type Params = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function POST(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function PUT(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function PATCH(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function DELETE(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function OPTIONS(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}

export async function HEAD(request: NextRequest, context: Params): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyToBackend(request, path);
}
