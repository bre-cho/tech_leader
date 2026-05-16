'use client'

import { useState } from 'react'
import { analyzeFashionRuntime } from '@/lib/fashion-runtime-api'
import type { FashionRuntimeResponse } from '@/types/fashion-runtime'

const steps = [
  'Visual DNA',
  'Emotional Graph',
  'Character Continuity',
  'Fashion Motion',
  'Beauty Commerce',
  'Storyboard',
  'Sequential Render',
  'Winner Memory',
]

export default function FashionRuntimeStudio() {
  const [brief, setBrief] = useState('Luxury K-beauty pastel fashion campaign with peach lavender motion energy, glossy black hair, soft feminine luxury, social commerce identity fantasy')
  const [duration, setDuration] = useState(60)
  const [provider, setProvider] = useState('kling')
  const [batchSize, setBatchSize] = useState(6)
  const [runtime, setRuntime] = useState<FashionRuntimeResponse | null>(null)
  const [status, setStatus] = useState('ready')
  const [error, setError] = useState('')

  async function runRuntime() {
    setStatus('running')
    setError('')

    try {
      const response = await analyzeFashionRuntime({
        brief,
        target_duration: duration,
        provider,
        planned_batch_size: batchSize,
        max_concurrent_render: 1,
        channel: 'tiktok_reels_shorts',
        language: 'vi',
      })
      setRuntime(response)
      setStatus('connected')
    } catch (err) {
      setStatus('failed')
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  function openViteStudio() {
    if (!runtime) return
    const payload = encodeURIComponent(JSON.stringify(runtime))
    const studioUrl = process.env.NEXT_PUBLIC_VIDEO_STUDIO_URL || 'http://localhost:5173'
    window.open(`${studioUrl}?fashion_handoff=${payload}`, '_blank')
  }

  return (
    <main className="fr-shell">
      <aside className="fr-sidebar">
        <div className="fr-logo">Fashion Runtime V1</div>
        <p className="fr-muted">AI-Native Cinematic Fashion Intelligence Infrastructure.</p>
        <div className="fr-step-list">
          {steps.map((step, index) => (
            <button className={index < 6 ? 'fr-step active' : 'fr-step'} key={step}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{step}</strong>
            </button>
          ))}
        </div>
      </aside>

      <section className="fr-main">
        <section className="fr-hero">
          <div>
            <div className="fr-eyebrow">VISUAL DNA → STORYBOARD → VIDEO RUNTIME</div>
            <h1>AI Fashion Beauty Runtime</h1>
            <p className="fr-muted">Dựa trên 2 bộ ảnh luxury beauty + pastel motion để tạo visual DNA, storyboard và winner memory.</p>
          </div>
          <button className="fr-primary" onClick={runRuntime}>Run Fashion Runtime</button>
        </section>

        <section className="fr-grid">
          <div className="fr-card">
            <div className="fr-eyebrow">CREATIVE BRIEF</div>
            <h2>Nhập ý đồ chiến dịch</h2>
            <textarea className="fr-textarea" value={brief} onChange={(event) => setBrief(event.target.value)} />
          </div>

          <div className="fr-card">
            <div className="fr-eyebrow">RUNTIME CONFIG</div>
            <h2>Provider + thời lượng</h2>
            <div className="fr-form">
              <label className="fr-label">Thời lượng video<input type="number" value={duration} onChange={(event) => setDuration(Number(event.target.value))}/></label>
              <label className="fr-label">Provider<select value={provider} onChange={(event) => setProvider(event.target.value)}><option value="kling">Kling</option><option value="runway">Runway</option><option value="veo">Veo</option><option value="seedance">Seedance</option></select></label>
              <label className="fr-label">Số cảnh / batch<input type="number" value={batchSize} onChange={(event) => setBatchSize(Number(event.target.value))}/></label>
              <label className="fr-label">Render đồng thời<input value="1 cảnh" readOnly /></label>
            </div>
          </div>
        </section>

        {error && <section className="fr-card"><div className="fr-eyebrow">ERROR</div><p>{error}</p></section>}

        {runtime && (
          <>
            <section className="fr-card">
              <div className="fr-eyebrow">VISUAL DNA</div>
              <h2>{runtime.visual_dna.archetype}</h2>
              <Row label="Lighting" value={runtime.visual_dna.lighting_language}/>
              <Row label="Hair" value={runtime.visual_dna.hair_signature}/>
              <Row label="Commerce angle" value={runtime.visual_dna.commerce_angle}/>
              <div className="fr-tags">{runtime.visual_dna.palette.map((item) => <span key={item}>{item}</span>)}</div>
            </section>

            <section className="fr-card">
              <div className="fr-eyebrow">SCORES</div>
              <div className="fr-score-grid">
                {Object.entries(runtime.visual_dna.scores).map(([key, value]) => (
                  <div className="fr-score" key={key}><span>{key}</span><br/><strong>{value}</strong></div>
                ))}
              </div>
            </section>

            <section className="fr-grid">
              <div className="fr-card">
                <div className="fr-eyebrow">CHARACTER CONTINUITY</div>
                <h2>Identity lock</h2>
                <Row label="Face" value={runtime.continuity_lock.face_identity}/>
                <Row label="Hair" value={runtime.continuity_lock.hair_identity}/>
                <div className="fr-tags">{runtime.continuity_lock.drift_guards.map((item) => <span key={item}>{item}</span>)}</div>
              </div>

              <div className="fr-card">
                <div className="fr-eyebrow">BEAUTY COMMERCE</div>
                <h2>{runtime.beauty_commerce.product_positioning}</h2>
                <p className="fr-muted">{runtime.beauty_commerce.audience_desire}</p>
                <div className="fr-tags">{runtime.beauty_commerce.conversion_triggers.map((item) => <span key={item}>{item}</span>)}</div>
              </div>
            </section>

            <section className="fr-card">
              <div className="fr-eyebrow">STORYBOARD RUNTIME</div>
              <h2>{runtime.storyboard.length} cảnh</h2>
              <div className="fr-storyboard">
                {runtime.storyboard.map((scene) => (
                  <article className="fr-scene" key={scene.id}>
                    <div className="fr-frame">Scene {scene.scene_index}</div>
                    <h3>{scene.title}</h3>
                    <p>{scene.camera}</p>
                    <p>{scene.duration}s</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="fr-card">
              <div className="fr-eyebrow">SAFE SEQUENTIAL RENDER</div>
              <h2>Render tuần tự từng cảnh</h2>
              <div className="fr-render-grid">
                {runtime.sequential_render_plan.map((step) => (
                  <article className="fr-render" key={step.scene_index}>
                    <strong>Batch {step.batch_index}</strong>
                    <p>Scene {step.scene_index}</p>
                    <p>{step.execution_mode} · 1/1</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="fr-card">
              <div className="fr-eyebrow">VIDEO HANDOFF</div>
              <h2>Gửi sang Vite Fashion Movie Studio</h2>
              <button className="fr-primary" onClick={openViteStudio}>Open Fashion Movie Studio</button>
            </section>
          </>
        )}
      </section>

      <aside className="fr-right">
        <section className="fr-card">
          <div className="fr-eyebrow">LIVE RUNTIME</div>
          <h2>{status}</h2>
          <div className="fr-log">Backend: /api/v1/fashion-runtime/analyze</div>
          <div className="fr-log">Proxy: Next route handler</div>
          <div className="fr-log">Handoff: fashion_handoff</div>
          <div className="fr-log">Concurrency: 1/1 scene</div>
        </section>

        {runtime && (
          <section className="fr-card">
            <div className="fr-eyebrow">WINNER DNA MEMORY</div>
            <h2>{runtime.winner_dna_memory.archetype}</h2>
            <div className="fr-tags">
              {runtime.winner_dna_memory.why_this_wins?.map((item: string) => <span key={item}>{item}</span>)}
            </div>
          </section>
        )}
      </aside>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) {
  return <div className="fr-row"><span>{label}</span><strong>{value}</strong></div>
}
