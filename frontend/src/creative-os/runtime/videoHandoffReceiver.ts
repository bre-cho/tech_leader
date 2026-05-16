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
export function readVideoHandoffFromUrl(): VideoHandoffPayload | null {
  const encoded = new URLSearchParams(window.location.search).get('handoff')
  if (!encoded) return null
  try { return JSON.parse(decodeURIComponent(encoded)) as VideoHandoffPayload } catch { return null }
}
