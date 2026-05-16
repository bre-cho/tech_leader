'use client'

import { useState } from 'react'
import { directMovie } from '@/lib/movie-os-v3-api'
import type { MovieDirectorResponse } from '@/types/movie-os-v3'

export function MovieDirectorSystemV3() {
  const [prompt, setPrompt] = useState('A gothic ruby queen transforms into a butterfly couture goddess in a cinematic fantasy movie')
  const [duration, setDuration] = useState(60)
  const [provider, setProvider] = useState('kling')
  const [plannedBatchSize, setPlannedBatchSize] = useState(6)
  const [movie, setMovie] = useState<MovieDirectorResponse | null>(null)
  const [status, setStatus] = useState('ready')
  const [error, setError] = useState('')

  async function runDirector() {
    setStatus('running')
    setError('')

    try {
      const response = await directMovie({
        prompt,
        target_duration: duration,
        provider,
        planned_batch_size: plannedBatchSize,
        max_concurrent_render: 1,
      })

      setMovie(response)
      setStatus('connected')
    } catch (err) {
      setStatus('failed')
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  function openStudio() {
    if (!movie) return
    const payload = encodeURIComponent(JSON.stringify(movie))
    const studioUrl = process.env.NEXT_PUBLIC_VIDEO_STUDIO_URL || 'http://localhost:5173'
    window.open(`${studioUrl}?movie_handoff=${payload}`, '_blank')
  }

  return (
    <main className="movie-shell">
      <aside className="movie-sidebar">
        <div className="movie-logo">Movie OS V3</div>
        <p className="movie-muted">Repo-compatible V3 using backend route + Next proxy + Vite handoff.</p>
      </aside>

      <section className="movie-main">
        <section className="movie-hero">
          <div>
            <div className="movie-eyebrow">CINEMATIC DIRECTOR SYSTEM V3</div>
            <h1>Prompt → Backend Director → Movie Studio</h1>
            <p className="movie-muted">Luồng này gọi backend thật qua proxy `/api/v1/movie-os/direct`.</p>
          </div>
          <button className="movie-primary" onClick={runDirector}>Run AI Director</button>
        </section>

        <section className="movie-grid">
          <div className="movie-card">
            <div className="movie-eyebrow">DIRECTOR PROMPT</div>
            <h2>Ý đồ điện ảnh</h2>
            <textarea className="movie-textarea" value={prompt} onChange={(event) => setPrompt(event.target.value)} />
          </div>

          <div className="movie-card">
            <div className="movie-eyebrow">MOVIE CONFIG</div>
            <h2>Runtime setup</h2>
            <div className="movie-form">
              <label className="movie-label">Duration<input type="number" value={duration} onChange={(event) => setDuration(Number(event.target.value))}/></label>
              <label className="movie-label">Provider<select value={provider} onChange={(event) => setProvider(event.target.value)}><option value="kling">Kling</option><option value="runway">Runway</option><option value="veo">Veo</option><option value="seedance">Seedance</option></select></label>
              <label className="movie-label">Planned batch size<input type="number" value={plannedBatchSize} onChange={(event) => setPlannedBatchSize(Number(event.target.value))}/></label>
              <label className="movie-label">Concurrency<input value="1 scene" readOnly /></label>
            </div>
          </div>
        </section>

        {error && <section className="movie-card"><div className="movie-eyebrow">ERROR</div><p>{error}</p></section>}

        {movie && (
          <>
            <section className="movie-grid">
              <div className="movie-card">
                <div className="movie-eyebrow">MOOD ENGINE</div>
                <h2>{movie.mood_profile.primary_mood}</h2>
                <Row label="Lighting" value={movie.mood_profile.lighting}/>
                <Row label="Lens" value={movie.mood_profile.lens}/>
                <div className="movie-tags">{movie.mood_profile.color_script.map((item) => <span key={item}>{item}</span>)}</div>
              </div>

              <div className="movie-card">
                <div className="movie-eyebrow">CHARACTER CONSISTENCY</div>
                <h2>Character Bible</h2>
                <Row label="Face" value={movie.character_bible.face}/>
                <Row label="Costume" value={movie.character_bible.costume}/>
                <Row label="Jewelry" value={movie.character_bible.jewelry}/>
                <Row label="Makeup" value={movie.character_bible.makeup}/>
              </div>
            </section>

            <section className="movie-card">
              <div className="movie-eyebrow">STORYBOARD FROM BACKEND</div>
              <h2>{movie.storyboard.length} cinematic scenes</h2>
              <div className="movie-storyboard">
                {movie.storyboard.map((scene) => (
                  <article className="movie-scene" key={scene.id}>
                    <div className="movie-scene-frame">Scene {scene.scene_index}</div>
                    <h3>{scene.title}</h3>
                    <p>{scene.camera}</p>
                    <p>{scene.lens}</p>
                    <p>{scene.duration}s</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="movie-card">
              <div className="movie-eyebrow">VIDEO STUDIO HANDOFF</div>
              <h2>Open Vite Movie Studio V3</h2>
              <button className="movie-primary" onClick={openStudio}>Open Movie Studio V3</button>
            </section>
          </>
        )}
      </section>

      <aside className="movie-right">
        <section className="movie-card">
          <div className="movie-eyebrow">DIRECTOR RUNTIME</div>
          <h2>{status}</h2>
          <div className="movie-log">API mode: Next proxy</div>
          <div className="movie-log">Backend route: /api/v1/movie-os/direct</div>
          <div className="movie-log">Vite handoff key: movie_handoff</div>
          <div className="movie-log">Sequential runtime: concurrency 1/1</div>
        </section>
      </aside>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) {
  return <div className="movie-row"><span>{label}</span><strong>{value}</strong></div>
}
