import { useMemo, useState } from 'react'
import { readFashionHandoff } from '../fashion-runtime/runtime/fashionHandoffReceiver'
import '../styles/fashion-runtime.css'

export default function FashionMovieStudio() {
  const runtime = readFashionHandoff()
  const [currentScene, setCurrentScene] = useState(1)

  const renderSteps = useMemo(() => {
    if (!runtime) return []

    return runtime.sequential_render_plan.map((step) => ({
      ...step,
      title: runtime.storyboard.find((scene) => scene.scene_index === step.scene_index)?.title || `Scene ${step.scene_index}`,
      status:
        step.scene_index < currentScene
          ? 'completed'
          : step.scene_index === currentScene
            ? 'rendering'
            : 'waiting',
    }))
  }, [runtime, currentScene])

  if (!runtime) {
    return (
      <main className="fashion-studio-shell">
        <section className="fashion-studio-hero">
          <div className="fashion-studio-eyebrow">FASHION MOVIE STUDIO</div>
          <h1>Waiting for Fashion Runtime Handoff</h1>
          <p>Gửi dữ liệu từ Next.js Fashion Runtime bằng query `fashion_handoff`.</p>
        </section>
      </main>
    )
  }

  return (
    <main className="fashion-studio-shell">
      <section className="fashion-studio-hero">
        <div className="fashion-studio-eyebrow">FASHION MOVIE STUDIO</div>
        <h1>Visual DNA → Timeline → Render</h1>
        <p>{runtime.visual_dna.archetype} · {runtime.fashion_motion.motion_style}</p>
      </section>

      <section className="fashion-studio-grid">
        <div className="fashion-studio-card">
          <div className="fashion-studio-eyebrow">STORYBOARD</div>
          <h2>{runtime.storyboard.length} scenes</h2>
          <div className="fashion-studio-scenes">
            {runtime.storyboard.map((scene) => (
              <article className="fashion-studio-scene" key={scene.id}>
                <div className="fashion-studio-frame">S{scene.scene_index}</div>
                <h3>{scene.title}</h3>
                <p>{scene.camera}</p>
                <p>{scene.duration}s</p>
              </article>
            ))}
          </div>
        </div>

        <div className="fashion-studio-card">
          <div className="fashion-studio-eyebrow">PROVIDER RUNTIME</div>
          <h2>{runtime.storyboard[0]?.provider?.toUpperCase() || 'PROVIDER'}</h2>
          <Row label="Batch size" value={runtime.sequential_render_plan[0]?.batch_index ? runtime.winner_dna_memory?.planned_batch_size || 'configured' : 'configured'} />
          <Row label="Concurrency" value="1/1" />
          <Row label="Mode" value="Sequential" />
          <Row label="Current scene" value={currentScene > runtime.storyboard.length ? 'done' : currentScene} />
          <button className="fashion-studio-button" onClick={() => setCurrentScene((value) => Math.min(value + 1, runtime.storyboard.length + 1))}>Simulate next scene</button>
        </div>
      </section>

      <section className="fashion-studio-card">
        <div className="fashion-studio-eyebrow">TIMELINE TRACK</div>
        <div className="fashion-studio-track">
          {runtime.storyboard.map((scene) => (
            <div className="fashion-studio-clip" key={scene.id}>
              <strong>S{scene.scene_index}</strong>
              <span>{scene.duration}s</span>
              <em>{scene.title}</em>
            </div>
          ))}
        </div>
      </section>

      <section className="fashion-studio-card">
        <div className="fashion-studio-eyebrow">SEQUENTIAL RENDER QUEUE</div>
        <div className="fashion-studio-render-list">
          {renderSteps.map((step) => (
            <div className={`fashion-studio-render ${step.status}`} key={step.scene_index}>
              <strong>Batch {step.batch_index} · Scene {step.scene_index}</strong>
              <span>{step.title}</span>
              <em>{step.status}</em>
            </div>
          ))}
        </div>
      </section>

      <section className="fashion-studio-card">
        <div className="fashion-studio-eyebrow">WINNER DNA</div>
        <div className="fashion-studio-tags">
          {runtime.visual_dna.palette.map((item) => <span key={item}>{item}</span>)}
        </div>
      </section>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) {
  return <div className="fashion-studio-row"><span>{label}</span><strong>{value}</strong></div>
}
