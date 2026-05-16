'use client'

import { useMemo, useState } from 'react'

type ProviderKey = 'veo' | 'runway' | 'kling' | 'seedance'
type RenderStatus = 'waiting' | 'rendering' | 'completed'
type Scene = { id: string; index: number; title: string; camera: string; duration: number; provider: ProviderKey; thumbnail: string }
type RenderStep = { sceneIndex: number; batchIndex: number; status: RenderStatus }
type StoryboardPlanRequest = {
  image_source: 'upload' | 'generated'
  image_url: string
  target_video_duration: number
  provider: ProviderKey
  planned_batch_size: number
  max_concurrent_render: 1
}
type StoryboardPlanResponse = {
  project_id: string
  image_url: string
  provider: ProviderKey
  scene_count: number
  scene_duration: number
  planned_batch_size: number
  total_batches: number
  scenes: Scene[]
}

const PROJECT_ID = 'demo-project-v2'
const steps = ['Image Source', 'Duration Planner', 'Storyboard Graph', 'Timeline Track', 'Sequential Render', 'Provider Runtime', 'Delivery', 'Memory Learning']
const providerDuration: Record<ProviderKey, number> = { veo: 8, runway: 5, kling: 5, seedance: 6 }
const sceneNames = ['Hook Scene', 'Product Focus', 'Desire Scene', 'Trust Scene', 'Transformation', 'CTA Scene']
const cameras = ['slow push-in', 'macro beauty shot', 'portrait close-up', 'medium shot', 'smooth reveal', 'logo reveal']

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const message = await res.text()
    throw new Error(message || `Request failed: ${res.status}`)
  }
  return await res.json() as T
}

export function CreativeOSVisualRuntimeV2() {
  const [imageUrl, setImageUrl] = useState('/uploads/demo-winner-image.png')
  const [duration, setDuration] = useState(60)
  const [provider, setProvider] = useState<ProviderKey>('kling')
  const [plannedBatchSize, setPlannedBatchSize] = useState(6)
  const [currentRenderIndex, setCurrentRenderIndex] = useState(1)
  const [hasPlan, setHasPlan] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [runtimeEvents, setRuntimeEvents] = useState<string[]>([])
  const [scenes, setScenes] = useState<Scene[]>([])

  const fallbackSceneCount = Math.max(1, Math.ceil(duration / providerDuration[provider]))
  const fallbackSceneDuration = Number((duration / fallbackSceneCount).toFixed(2))
  const visualScenes: Scene[] = useMemo(() => {
    if (scenes.length > 0) return scenes
    return Array.from({ length: fallbackSceneCount }).map((_, i) => ({
      id: `scene-${i + 1}`,
      index: i + 1,
      title: sceneNames[i % sceneNames.length],
      camera: cameras[i % cameras.length],
      duration: fallbackSceneDuration,
      provider,
      thumbnail: imageUrl,
    }))
  }, [fallbackSceneCount, fallbackSceneDuration, provider, imageUrl, scenes])

  const sceneCount = visualScenes.length
  const sceneDuration = visualScenes[0]?.duration ?? fallbackSceneDuration
  const totalBatches = Math.ceil(sceneCount / plannedBatchSize)

  const renderSteps: RenderStep[] = useMemo(() => visualScenes.map((scene) => ({
    sceneIndex: scene.index,
    batchIndex: Math.ceil(scene.index / plannedBatchSize),
    status: !hasPlan ? 'waiting' : scene.index < currentRenderIndex ? 'completed' : scene.index === currentRenderIndex ? 'rendering' : 'waiting',
  })), [visualScenes, plannedBatchSize, currentRenderIndex, hasPlan])

  const currentScene = visualScenes.find((s) => s.index === currentRenderIndex)
  const nextScene = visualScenes.find((s) => s.index === currentRenderIndex + 1)

  async function generatePlan() {
    setApiError(null)
    setHasPlan(false)
    setCurrentRenderIndex(1)

    try {
      const payload: StoryboardPlanRequest = {
        image_source: 'upload',
        image_url: imageUrl,
        target_video_duration: duration,
        provider,
        planned_batch_size: plannedBatchSize,
        max_concurrent_render: 1,
      }

      const plan = await fetchJson<StoryboardPlanResponse>(`/api/v1/creative-os/projects/${PROJECT_ID}/plan-storyboard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const serverScenes = Array.isArray(plan.scenes) ? plan.scenes : []
      if (serverScenes.length > 0) {
        setScenes(serverScenes.map((scene, index) => ({
          ...scene,
          index: scene.index || index + 1,
          thumbnail: imageUrl,
        })))
      }

      const stepsFromApi = await fetchJson<RenderStep[]>(`/api/v1/creative-os/projects/${PROJECT_ID}/render-steps?scene_count=${plan.scene_count}&planned_batch_size=${plan.planned_batch_size}`)
      const eventsFromApi = await fetchJson<Array<{ message?: string }>>(`/api/v1/creative-os/projects/${PROJECT_ID}/events`)

      setPlannedBatchSize(plan.planned_batch_size)
      setHasPlan(true)
      setRuntimeEvents([
        `Storyboard planned: ${plan.scene_count} scenes, ${plan.total_batches} batches.`,
        `Render steps loaded from API: ${stepsFromApi.length}.`,
        ...eventsFromApi.map((event) => event.message).filter((msg): msg is string => typeof msg === 'string'),
      ])
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Khong the lap storyboard tu backend.'
      setApiError(message)
      setRuntimeEvents((prev) => [`Plan failed: ${message}`, ...prev])
    }
  }

  function simulateNextStep() { if (hasPlan) setCurrentRenderIndex((v) => Math.min(v + 1, sceneCount + 1)) }

  function openViteStudio() {
    const payload = encodeURIComponent(JSON.stringify({
      project_id: 'demo-project-v2',
      winner_image_url: imageUrl,
      storyboard: visualScenes,
      provider_targets: [provider],
      render_mode: 'image_to_video',
      planned_batch_size: plannedBatchSize,
      max_concurrent_render: 1,
      execution_mode: 'sequential',
      current_render_index: currentRenderIndex,
    }))
    const studioUrl = process.env.NEXT_PUBLIC_VIDEO_STUDIO_URL || 'http://localhost:5173'
    window.open(`${studioUrl}?handoff=${payload}`, '_blank')
  }

  return (
    <main className="v2-shell">
      <aside className="v2-sidebar">
        <div className="v2-logo">Creative OS V2</div>
        <p className="v2-muted">Visual timeline runtime, storyboard thumbnails, sequential render state.</p>
        <div className="v2-step-list">{steps.map((s, i) => <button key={s} className={i < 5 ? 'v2-step active' : 'v2-step'}><span>{String(i + 1).padStart(2, '0')}</span><strong>{s}</strong></button>)}</div>
      </aside>

      <section className="v2-main">
        <section className="v2-hero">
          <div><div className="v2-eyebrow">UIUX V2 VISUAL TIMELINE RUNTIME</div><h1>Visual Storyboard - Timeline - Render State</h1><p className="v2-muted">Them thumbnail storyboard, timeline track va trang thai render dong theo luat concurrency = 1.</p></div>
          <button className="v2-primary" onClick={generatePlan}>Generate Visual Timeline</button>
        </section>

        {apiError ? <section className="v2-card"><strong>{apiError}</strong></section> : null}

        <section className="v2-grid">
          <div className="v2-card"><div className="v2-eyebrow">LARGE VISUAL BOARD</div><h2>Anh thang / anh nguon</h2><div className="v2-image-board">{imageUrl ? <img src={imageUrl} alt="Winner visual" /> : <span>WINNER IMAGE</span>}</div></div>
          <div className="v2-card"><div className="v2-eyebrow">PLANNER</div><h2>Duration + Provider</h2><div className="v2-form"><label className="v2-label">Image URL<input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} /></label><label className="v2-label">Thoi luong video<input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} /></label><label className="v2-label">Provider<select value={provider} onChange={(e) => setProvider(e.target.value as ProviderKey)}><option value="veo">Veo</option><option value="runway">Runway</option><option value="kling">Kling</option><option value="seedance">Seedance</option></select></label><label className="v2-label">So canh/batch<input type="number" value={plannedBatchSize} onChange={(e) => setPlannedBatchSize(Number(e.target.value))} /></label></div><Metric label="Scene count" value={sceneCount} /><Metric label="Scene duration" value={`${sceneDuration}s`} /><Metric label="Total batches" value={totalBatches} /><Metric label="Concurrency" value="1/1" /></div>
        </section>

        <section className="v2-card"><div className="v2-eyebrow">VISUAL STORYBOARD STRIP</div><h2>{sceneCount} thumbnail scenes</h2><div className="v2-thumb-strip">{visualScenes.map((scene) => <article className="v2-thumb" key={scene.id}><div className="v2-thumb-frame">{scene.thumbnail ? <img src={scene.thumbnail} alt={scene.title} /> : `Scene ${scene.index}`}</div><div className="v2-thumb-body"><span className="v2-pill">Scene {scene.index}</span><h3>{scene.title}</h3><p>{scene.camera}</p><p>{scene.duration}s</p></div></article>)}</div></section>

        <section className="v2-card"><div className="v2-eyebrow">TIMELINE COMPOSITION TRACK</div><h2>Video / Subtitle / Effects track</h2><div className="v2-timeline">{visualScenes.map((scene) => <div className="v2-clip" key={scene.id}><strong>S{scene.index}</strong><span>{scene.duration}s</span><em>{scene.title}</em></div>)}</div></section>

        <section className="v2-card"><div className="v2-eyebrow">DYNAMIC SEQUENTIAL RENDER STATE</div><h2>Render queue dong</h2><button className="v2-secondary" onClick={simulateNextStep}>Simulate Next Render Step</button><div className="v2-render-grid" style={{ marginTop: 18 }}>{renderSteps.map((step) => <article className={`v2-render-step ${step.status}`} key={step.sceneIndex}><strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong><p>{step.status}</p><span className="v2-pill">concurrency 1/1</span></article>)}</div></section>

        <section className="v2-card"><div className="v2-eyebrow">VIDEO STUDIO HANDOFF</div><h2>Gui sang Vite Studio V2</h2><button className="v2-primary" onClick={openViteStudio}>Open Vite Studio V2</button></section>
      </section>

      <aside className="v2-right">
        <section className="v2-card"><div className="v2-eyebrow">PROVIDER LOAD SAFETY</div><h2>{provider.toUpperCase()}</h2><Metric label="Queue depth" value={sceneCount} /><Metric label="Current scene" value={currentScene ? currentScene.index : 'done'} /><Metric label="Next scene" value={nextScene ? nextScene.index : '-'} /><Metric label="Cooldown" value={provider === 'kling' ? '6s' : '5s'} /><Metric label="Retry limit" value={2} /><Metric label="Risk" value="Low" /></section>
        <section className="v2-card"><div className="v2-eyebrow">LIVE RUNTIME</div><h2>Agent State</h2><Log text="Storyboard Agent generated visual strip." /><Log text="Timeline Agent composed video track." /><Log text="Provider Runtime locked concurrency to 1." /><Log text={hasPlan ? `Rendering Scene ${currentRenderIndex}` : 'Waiting for visual timeline.'} />{runtimeEvents.slice(0, 6).map((event, idx) => <Log key={`${event}-${idx}`} text={event} />)}</section>
      </aside>
    </main>
  )
}

function Metric({ label, value }: { label: string; value: string | number }) { return <div className="v2-metric"><span>{label}</span><strong>{value}</strong></div> }
function Log({ text }: { text: string }) { return <div className="v2-log">{text}</div> }