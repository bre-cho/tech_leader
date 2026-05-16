import { useMemo, useState } from 'react'
import { readMovieHandoff } from '../movie-os-v3/runtime/movieHandoffReceiver'
import '../styles/movie-os-v3.css'

export default function MovieStudioV3() {
  const movie = readMovieHandoff()
  const [currentScene, setCurrentScene] = useState(1)

  const renderSteps = useMemo(() => {
    if (!movie) return []

    return movie.storyboard.map((scene) => ({
      sceneIndex: scene.scene_index,
      title: scene.title,
      batchIndex: Math.ceil(scene.scene_index / movie.sequential_render_policy.planned_batch_size),
      status:
        scene.scene_index < currentScene
          ? 'completed'
          : scene.scene_index === currentScene
            ? 'rendering'
            : 'waiting',
    }))
  }, [movie, currentScene])

  if (!movie) {
    return (
      <main className="studio3-shell">
        <section className="studio3-hero">
          <div className="studio3-eyebrow">MOVIE STUDIO V3</div>
          <h1>Waiting for Movie Handoff</h1>
          <p>Open this page with `?movie_handoff=...` from Next.js.</p>
        </section>
      </main>
    )
  }

  return (
    <main className="studio3-shell">
      <section className="studio3-hero">
        <div className="studio3-eyebrow">MOVIE STUDIO V3</div>
        <h1>Director Plan → Sequential Render</h1>
        <p>{movie.mood_profile.primary_mood} · {movie.editor_plan.edit_style}</p>
      </section>

      <section className="studio3-grid">
        <div className="studio3-card">
          <div className="studio3-eyebrow">STORYBOARD RUNTIME</div>
          <h2>{movie.storyboard.length} cinematic scenes</h2>

          <div className="studio3-scenes">
            {movie.storyboard.map((scene) => (
              <article className="studio3-scene" key={scene.id}>
                <div className="studio3-frame">S{scene.scene_index}</div>
                <h3>{scene.title}</h3>
                <p>{scene.camera}</p>
                <p>{scene.duration}s</p>
              </article>
            ))}
          </div>
        </div>

        <div className="studio3-card">
          <div className="studio3-eyebrow">PROVIDER RUNTIME</div>
          <h2>{movie.sequential_render_policy.provider.toUpperCase()}</h2>
          <Row label="Batch size" value={movie.sequential_render_policy.planned_batch_size} />
          <Row label="Concurrency" value="1/1" />
          <Row label="Mode" value="Sequential" />
          <button className="studio3-button" onClick={() => setCurrentScene((value) => Math.min(value + 1, movie.storyboard.length + 1))}>Simulate next scene</button>
        </div>
      </section>

      <section className="studio3-card">
        <div className="studio3-eyebrow">SEQUENTIAL RENDER QUEUE</div>
        <div className="studio3-render-list">
          {renderSteps.map((step) => (
            <div className={`studio3-render ${step.status}`} key={step.sceneIndex}>
              <strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong>
              <span>{step.title}</span>
              <em>{step.status}</em>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) {
  return <div className="studio3-row"><span>{label}</span><strong>{value}</strong></div>
}
