import { useMemo, useState } from 'react'
import { readMovieOSV4Handoff } from '../movie-os-v4/runtime/movieOSV4Handoff'
import '../styles/movie-os-v4.css'

export default function AutonomousMovieStudioV4() {
  const movie = readMovieOSV4Handoff()
  const [currentScene, setCurrentScene] = useState(1)

  const renderSteps = useMemo(() => {
    if (!movie) return []

    return movie.storyboard.map((scene) => ({
      sceneIndex: scene.scene_index,
      title: scene.title,
      batchIndex: Math.ceil(scene.scene_index / movie.sequential_runtime_plan.planned_batch_size),
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
      <main className="studio4-shell">
        <section className="studio4-hero">
          <div className="studio4-eyebrow">AUTONOMOUS MOVIE STUDIO V4</div>
          <h1>Waiting for Movie OS V4 Handoff</h1>
          <p>Gửi movie plan từ Next.js Movie OS V4 để bắt đầu autonomous timeline runtime.</p>
        </section>
      </main>
    )
  }

  return (
    <main className="studio4-shell">
      <section className="studio4-hero">
        <div className="studio4-eyebrow">AUTONOMOUS MOVIE STUDIO V4</div>
        <h1>Timeline With Memory → Sequential Runtime</h1>
        <p>{movie.mood_profile.mood} · {movie.editor_plan.edit_style}</p>
      </section>

      <section className="studio4-grid">
        <div className="studio4-card">
          <div className="studio4-eyebrow">STORYBOARD RUNTIME</div>
          <h2>{movie.storyboard.length} scenes</h2>
          <div className="studio4-scenes">
            {movie.storyboard.map((scene) => (
              <article className="studio4-scene" key={scene.id}>
                <div className="studio4-frame">S{scene.scene_index}</div>
                <h3>{scene.title}</h3>
                <p>{scene.camera_move}</p>
                <p>{scene.duration}s</p>
              </article>
            ))}
          </div>
        </div>

        <div className="studio4-card">
          <div className="studio4-eyebrow">PROVIDER RUNTIME</div>
          <h2>{movie.sequential_runtime_plan.provider.toUpperCase()}</h2>
          <Row label="Batch size" value={movie.sequential_runtime_plan.planned_batch_size} />
          <Row label="Concurrency" value="1/1" />
          <Row label="Mode" value="Sequential" />
          <Row label="Current scene" value={currentScene > movie.storyboard.length ? 'done' : currentScene} />
          <button className="studio4-button" onClick={() => setCurrentScene((value) => Math.min(value + 1, movie.storyboard.length + 1))}>Simulate next scene</button>
        </div>
      </section>

      <section className="studio4-card">
        <div className="studio4-eyebrow">EMOTIONAL TIMELINE</div>
        <div className="studio4-track">
          {movie.emotional_timeline.points.map((point) => (
            <div className="studio4-clip" key={point.scene_index}>
              <strong>S{point.scene_index}</strong>
              <span>{point.emotional_state}</span>
              <em>{point.visual_density}</em>
            </div>
          ))}
        </div>
      </section>

      <section className="studio4-card">
        <div className="studio4-eyebrow">SEQUENTIAL RENDER QUEUE</div>
        <div className="studio4-render-list">
          {renderSteps.map((step) => (
            <div className={`studio4-render ${step.status}`} key={step.sceneIndex}>
              <strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong>
              <span>{step.title}</span>
              <em>{step.status}</em>
            </div>
          ))}
        </div>
      </section>

      <section className="studio4-card">
        <div className="studio4-eyebrow">FINAL MOVIE ASSEMBLY</div>
        <div className="studio4-tags">
          {movie.assembly_plan.tracks.map((track) => <span key={track}>{track}</span>)}
        </div>
      </section>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) {
  return <div className="studio4-row"><span>{label}</span><strong>{value}</strong></div>
}
