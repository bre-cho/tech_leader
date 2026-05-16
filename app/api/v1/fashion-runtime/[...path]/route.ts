import { NextRequest, NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000/api/v1'

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  const search = request.nextUrl.search || ''
  const backendUrl = `${BACKEND_API_BASE_URL}/fashion-runtime/${path.join('/')}${search}`

  const init: RequestInit = {
    method: request.method,
    headers: {
      'Content-Type': request.headers.get('Content-Type') || 'application/json',
    },
    cache: 'no-store',
  }

  if (!['GET', 'HEAD'].includes(request.method)) {
    init.body = await request.text()
  }

  const response = await fetch(backendUrl, init)
  const contentType = response.headers.get('Content-Type') || 'application/json'
  const body = await response.text()

  return new NextResponse(body, {
    status: response.status,
    headers: { 'Content-Type': contentType },
  })
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxy(request, context)
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxy(request, context)
}
