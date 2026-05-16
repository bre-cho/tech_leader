export async function directMovie(payload: {
  prompt: string
  target_duration: number
  provider: string
  planned_batch_size: number
  max_concurrent_render: number
}) {
  const res = await fetch('/api/v1/movie-os/direct', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Failed to direct movie: ${res.status} ${text}`)
  }

  return res.json()
}
