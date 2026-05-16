import type { FashionRuntimeResponse } from '../../types/fashion-runtime'

export function readFashionHandoff(): FashionRuntimeResponse | null {
  const encoded = new URLSearchParams(window.location.search).get('fashion_handoff')
  if (!encoded) return null

  try {
    return JSON.parse(decodeURIComponent(encoded)) as FashionRuntimeResponse
  } catch {
    return null
  }
}
