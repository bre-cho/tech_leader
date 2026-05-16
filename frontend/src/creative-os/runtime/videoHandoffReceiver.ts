export type VideoHandoffPayload = {
  project_id: string
  winner_image_url?: string
  storyboard: Array<Record<string, unknown>>
  provider_targets: string[]
  render_mode: 'image_to_video'
  planned_batch_size: number
  max_concurrent_render: 1
  execution_mode: 'sequential'
}

function isVideoHandoffPayload(value: unknown): value is VideoHandoffPayload {
  if (!value || typeof value !== 'object') return false
  const data = value as Record<string, unknown>
  return (
    typeof data.project_id === 'string' &&
    Array.isArray(data.storyboard) &&
    Array.isArray(data.provider_targets) &&
    typeof data.planned_batch_size === 'number' &&
    data.render_mode === 'image_to_video' &&
    data.max_concurrent_render === 1 &&
    data.execution_mode === 'sequential'
  )
}

export function readVideoHandoffFromUrl(): VideoHandoffPayload | null {
  const encoded = new URLSearchParams(window.location.search).get('handoff')
  if (encoded) {
    try {
      const parsed = JSON.parse(decodeURIComponent(encoded)) as unknown
      if (isVideoHandoffPayload(parsed)) return parsed
    } catch {
      // Continue to window.name fallback for marker values like handoff=1.
    }
  }

  // Fallback for cross-origin handoff from Next.js using popup window.name.
  const namedPayload = window.name
  if (!namedPayload) return null
  try {
    const parsed = JSON.parse(namedPayload) as unknown
    return isVideoHandoffPayload(parsed) ? parsed : null
  } catch {
    return null
  }
}
