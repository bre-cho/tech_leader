export async function analyzeFashionRuntime(payload: {
  brief: string
  target_duration: number
  provider: string
  planned_batch_size: number
  max_concurrent_render: number
  channel: string
  language: string
}) {
  const res = await fetch('/api/v1/fashion-runtime/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Fashion runtime failed: ${res.status} ${text}`)
  }

  return res.json()
}
