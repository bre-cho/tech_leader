import { useMemo, useState } from 'react'
import { readVideoHandoffV2 } from '../creative-os-v2/runtime/videoHandoffReceiverV2'
import '../styles/creative-os-v2.css'

export default function DesignStudioCreativeOSV2() {
  const handoff = readVideoHandoffV2()
  const [current, setCurrent] = useState(handoff?.current_render_index || 1)

  const renderSteps = useMemo(() => {
    if (!handoff) return []
    return handoff.storyboard.map((scene, index) => {
      const sceneIndex = index + 1
      return {
        sceneIndex,
        title: scene.title || `Scene ${sceneIndex}`,
        batchIndex: Math.ceil(sceneIndex / handoff.planned_batch_size),
        status: sceneIndex < current ? 'completed' : sceneIndex === current ? 'rendering' : 'waiting',
      }
    })
  }, [handoff, current])

  if (!handoff) {
    return <main className="studio-v2-shell"><section className="studio-v2-hero"><div className="studio-v2-eyebrow">VITE VIDEO STUDIO V2</div><h1>Waiting for Visual Timeline Handoff</h1><p>Gui storyboard tu Next.js Control Plane de bat dau.</p></section></main>
  }

  return (
    <main className="studio-v2-shell">
      <section className="studio-v2-hero"><div className="studio-v2-eyebrow">VITE VIDEO STUDIO V2</div><h1>Timeline Track - Sequential Render</h1><p>VideoFlow mode: storyboard da duoc chuyen thanh timeline va queue render tuan tu.</p></section>
      <section className="studio-v2-grid">
        <div className="studio-v2-card"><div className="studio-v2-eyebrow">STORYBOARD THUMBNAILS</div><h2>{handoff.storyboard.length} scenes</h2><div className="studio-v2-thumb-grid">{handoff.storyboard.map((scene, index) => <article className="studio-v2-thumb" key={index}><div className="studio-v2-frame">{handoff.winner_image_url ? <img src={handoff.winner_image_url} alt="" /> : `Scene ${index + 1}`}</div><strong>Scene {index + 1}</strong><span>{scene.title || 'Scene'}</span></article>)}</div></div>
        <div className="studio-v2-card"><div className="studio-v2-eyebrow">PROVIDER RUNTIME</div><h2>{handoff.provider_targets.join(' / ')}</h2><Row label="Planned batch size" value={handoff.planned_batch_size} /><Row label="Max concurrent render" value="1" /><Row label="Execution mode" value="Sequential" /><button className="studio-v2-button" onClick={() => setCurrent((v) => Math.min(v + 1, handoff.storyboard.length + 1))}>Simulate next scene</button></div>
      </section>
      <section className="studio-v2-card"><div className="studio-v2-eyebrow">TIMELINE TRACK</div><div className="studio-v2-track">{handoff.storyboard.map((scene, index) => <div className="studio-v2-clip" key={index}><strong>S{index + 1}</strong><span>{scene.duration || 5}s</span></div>)}</div></section>
      <section className="studio-v2-card"><div className="studio-v2-eyebrow">DYNAMIC RENDER QUEUE</div><div className="studio-v2-render-list">{renderSteps.map((step) => <div className={`studio-v2-render ${step.status}`} key={step.sceneIndex}><strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong><span>{step.title}</span><em>{step.status}</em></div>)}</div></section>
    </main>
  )
}

function Row({ label, value }: { label: string; value: string | number }) { return <div className="studio-v2-row"><span>{label}</span><strong>{value}</strong></div> }