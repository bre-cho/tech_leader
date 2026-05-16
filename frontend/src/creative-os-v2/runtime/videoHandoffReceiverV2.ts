type StoryboardItem = {
  title?: string
  duration?: number
}

export type VideoHandoffPayloadV2 = {
  project_id: string
  winner_image_url?: string
  storyboard: StoryboardItem[]
  provider_targets: string[]
  render_mode: 'image_to_video'
  planned_batch_size: number
  max_concurrent_render: 1
  execution_mode: 'sequential'
  current_render_index?: number
}

function isVideoHandoffPayloadV2(value: unknown): value is VideoHandoffPayloadV2 {
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

function parseEncodedHandoff(value: string | null): VideoHandoffPayloadV2 | null {
  if (!value) return null
  try {
    const parsed = JSON.parse(decodeURIComponent(value)) as unknown
    return isVideoHandoffPayloadV2(parsed) ? parsed : null
  } catch {
    return null
  }
}

export function readVideoHandoffV2(): VideoHandoffPayloadV2 | null {
  const fromQuery = parseEncodedHandoff(new URLSearchParams(window.location.search).get('handoff'))
  if (fromQuery) return fromQuery

  const namedPayload = window.name
  if (!namedPayload) return null
  try {
    const parsed = JSON.parse(namedPayload) as unknown
    return isVideoHandoffPayloadV2(parsed) ? parsed : null
  } catch {
    return null
  }
}