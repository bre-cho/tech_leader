import { useEffect, useMemo, useState } from 'react'
import { readVideoHandoffFromUrl } from '../creative-os/runtime/videoHandoffReceiver'
import '../styles/creative-os.css'

const PROVIDERS = ['veo', 'runway', 'kling', 'seedance'] as const
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || deriveApiBaseUrl()
const DEMO_PROJECT_ID = 'demo-project'

type RuntimeStep = {
  batch_index: number
  scene_index: number
  status: string
  provider?: string
  artifact_path?: string | null
}

type RuntimeStatus = {
  status: 'idle' | 'running' | 'completed' | 'failed'
  completed_scenes?: number
  failed_scenes?: number
  steps: RuntimeStep[]
}

async function fetchCreativeOsJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

function deriveApiBaseUrl(): string {
  const origin = window.location.origin
  if (origin.includes('.app.github.dev')) {
    return origin.replace(/-\d+\.app\.github\.dev$/, '-8000.app.github.dev')
  }
  return 'http://localhost:8000'
}

function getSceneTitle(scene: Record<string, unknown>, index: number): string {
  const title = scene.title
  return typeof title === 'string' && title.trim().length > 0 ? title : `Scene ${index + 1}`
}

function getScenePrompt(scene: Record<string, unknown>): string | null {
  const prompt = scene.prompt
  return typeof prompt === 'string' && prompt.trim().length > 0 ? prompt : null
}

function getProviderLabel(provider: string): string {
  const key = provider.trim().toLowerCase()
  if (key === 'seedance2-fast' || key === 'seedance2') return 'Seedance Fast MVP'
  if (key === 'seedance') return 'Seedance'
  if (key === 'kling') return 'Kling'
  if (key === 'runway') return 'Runway'
  if (key === 'veo') return 'Veo'
  return provider
}

export default function DesignStudioCreativeOS() {
  const handoff = readVideoHandoffFromUrl()
  const hasHandoffMarker = new URLSearchParams(window.location.search).has('handoff')
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatus | null>(null)
  const [runtimeError, setRuntimeError] = useState<string | null>(null)

  const activeProviders = useMemo(
    () => (handoff ? PROVIDERS.filter((provider) => handoff.provider_targets.includes(provider)) : []),
    [handoff],
  )
  const runtimeProviders = useMemo(
    () => (activeProviders.length > 0 ? activeProviders : handoff ? [handoff.provider_targets[0] ?? 'veo'] : []),
    [activeProviders, handoff],
  )

  useEffect(() => {
    if (!handoff) return
    const runtimeHandoff = handoff

    let isMounted = true
    let intervalId: number | null = null

    async function pollStatus() {
      try {
        const data = await fetchCreativeOsJson<RuntimeStatus>(`/api/v1/creative-os/projects/${runtimeHandoff.project_id}/render-status`)
        if (!isMounted) return
        setRuntimeStatus(data)
        if (data.status === 'completed' || data.status === 'failed') {
          if (intervalId) window.clearInterval(intervalId)
        }
      } catch (error) {
        if (!isMounted) return
        setRuntimeError(error instanceof Error ? error.message : 'Poll render status failed.')
        if (intervalId) window.clearInterval(intervalId)
      }
    }

    async function startExecution() {
      setRuntimeError(null)
      try {
        const data = await fetchCreativeOsJson<RuntimeStatus>(`/api/v1/creative-os/projects/${runtimeHandoff.project_id}/execute-render`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scene_count: runtimeHandoff.storyboard.length,
            planned_batch_size: runtimeHandoff.planned_batch_size,
            provider: runtimeProviders[0] ?? 'veo',
            image_url: runtimeHandoff.winner_image_url ?? null,
          }),
        })

        if (!isMounted) return
        setRuntimeStatus(data)
        if (data.status === 'running') {
          intervalId = window.setInterval(pollStatus, 1500)
        }
      } catch (error) {
        if (!isMounted) return
        setRuntimeError(error instanceof Error ? error.message : 'Execute render failed.')
      }
    }

    startExecution()

    return () => {
      isMounted = false
      if (intervalId) window.clearInterval(intervalId)
    }
  }, [handoff, runtimeProviders])

  useEffect(() => {
    if (handoff || !hasHandoffMarker) return

    let isMounted = true
    let intervalId: number | null = null

    async function pollStatus() {
      try {
        const status = await fetchCreativeOsJson<RuntimeStatus>(`/api/v1/creative-os/projects/${DEMO_PROJECT_ID}/render-status`)
        if (!isMounted) return
        setRuntimeStatus(status)
        if (status.status === 'completed' || status.status === 'failed') {
          if (intervalId) window.clearInterval(intervalId)
        }
      } catch (error) {
        if (!isMounted) return
        setRuntimeError(error instanceof Error ? error.message : 'Poll render status failed.')
        if (intervalId) window.clearInterval(intervalId)
      }
    }

    async function bootstrapWithMarker() {
      setRuntimeError(null)
      try {
        const plan = await fetchCreativeOsJson<{ scene_count: number; planned_batch_size: number; provider: string }>(
          `/api/v1/creative-os/projects/${DEMO_PROJECT_ID}/plan-storyboard`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              image_source: 'generated',
              image_url: 'generated://inline-preview',
              target_video_duration: 24,
              provider: 'kling',
              planned_batch_size: 4,
              max_concurrent_render: 1,
            }),
          },
        )

        const execution = await fetchCreativeOsJson<RuntimeStatus>(
          `/api/v1/creative-os/projects/${DEMO_PROJECT_ID}/execute-render`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              scene_count: plan.scene_count,
              planned_batch_size: plan.planned_batch_size,
              provider: plan.provider,
              image_url: 'generated://inline-preview',
            }),
          },
        )

        if (!isMounted) return
        setRuntimeStatus(execution)
        if (execution.status === 'running') {
          intervalId = window.setInterval(pollStatus, 1500)
        }
      } catch (error) {
        if (!isMounted) return
        setRuntimeError(error instanceof Error ? error.message : 'Auto bootstrap from handoff marker failed.')
      }
    }

    bootstrapWithMarker()

    return () => {
      isMounted = false
      if (intervalId) window.clearInterval(intervalId)
    }
  }, [handoff, hasHandoffMarker])

  if (!handoff) {
    const markerSteps = runtimeStatus?.steps?.map((step) => ({
      sceneIndex: step.scene_index,
      batchIndex: step.batch_index,
      provider: step.provider || 'kling',
      status: step.status,
      artifactPath: step.artifact_path || null,
    })) || []

    return (
      <main className="studio-shell">
        <section className="studio-card hero">
          <div className="studio-eyebrow">REALTIME VIDEO STUDIO</div>
          <h1>{hasHandoffMarker ? 'Creative OS Marker Mode' : 'Creative OS Preview Mode'}</h1>
          <p>
            {hasHandoffMarker
              ? 'Đã nhận marker handoff. Hệ thống đang tự bootstrap storyboard và đồng bộ render-status từ backend.'
              : 'Trang này đang chạy ở chế độ xem trước vì chưa nhận được payload storyboard từ Next.js.'}
          </p>
        </section>

        <section className="studio-grid">
          <div className="studio-card">
            <div className="studio-eyebrow">DEMO PROVIDERS</div>
            <h2>Provider runtime ready</h2>
            {PROVIDERS.map((provider) => (
              <div className="studio-row" key={provider}>
                <strong>{provider.toUpperCase()}</strong>
                <span>standby</span>
              </div>
            ))}
          </div>

          <div className="studio-card">
            <div className="studio-eyebrow">WHAT TO DO NEXT</div>
            <h2>{hasHandoffMarker ? 'Runtime sync status' : 'Send storyboard handoff'}</h2>
            {hasHandoffMarker ? (
              <>
                <div className="studio-row">
                  <strong>Project</strong>
                  <span>{DEMO_PROJECT_ID}</span>
                </div>
                <div className="studio-row">
                  <strong>Runtime</strong>
                  <span>{runtimeStatus?.status || 'starting'}</span>
                </div>
                <div className="studio-row">
                  <strong>Provider</strong>
                  <span>{getProviderLabel(runtimeProviders[0] ?? 'veo')}</span>
                </div>
                <div className="studio-row">
                  <strong>Completed</strong>
                  <span>{runtimeStatus?.completed_scenes ?? 0}</span>
                </div>
              </>
            ) : (
              <>
                <div className="studio-row">
                  <strong>1</strong>
                  <span>Mở Next.js control plane và tạo storyboard.</span>
                </div>
                <div className="studio-row">
                  <strong>2</strong>
                  <span>Gửi payload qua handoff để bật sequential render.</span>
                </div>
                <div className="studio-row">
                  <strong>3</strong>
                  <span>Quay lại link này với payload đầy đủ để xem timeline.</span>
                </div>
              </>
            )}
          </div>
        </section>

        {hasHandoffMarker ? (
          <section className="studio-card">
            <div className="studio-eyebrow">VIDEOFLOW RENDER QUEUE</div>
            <h2>Sequential execution (marker bootstrap)</h2>
            {runtimeError ? (
              <div className="studio-row">
                <strong>Runtime error</strong>
                <span>{runtimeError}</span>
              </div>
            ) : null}
            {markerSteps.length === 0 ? (
              <div className="studio-row">
                <strong>Queue</strong>
                <span>Đang đồng bộ render-status...</span>
              </div>
            ) : (
              markerSteps.map((step) => (
                <div className="studio-row" key={step.sceneIndex}>
                  <strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong>
                  <span>{getProviderLabel(step.provider)} render · {step.status}{step.artifactPath ? ' · artifact ready' : ''}</span>
                </div>
              ))
            )}
          </section>
        ) : null}
      </main>
    )
  }

  const fallbackSteps = handoff.storyboard.map((scene, index) => ({
    sceneIndex: index + 1,
    batchIndex: Math.ceil((index + 1) / handoff.planned_batch_size),
    provider: runtimeProviders[index % runtimeProviders.length] || 'veo',
    title: getSceneTitle(scene, index),
    status: 'queued',
    artifactPath: null as string | null,
  }))

  const steps = runtimeStatus?.steps?.length
    ? runtimeStatus.steps.map((step) => ({
        sceneIndex: step.scene_index,
        batchIndex: step.batch_index,
        provider: step.provider || runtimeProviders[(step.scene_index - 1) % runtimeProviders.length] || 'veo',
        title: getSceneTitle(handoff.storyboard[step.scene_index - 1] || {}, step.scene_index - 1),
        status: step.status,
        artifactPath: step.artifact_path || null,
      }))
    : fallbackSteps

  return (
    <main className="studio-shell">
      <section className="studio-card hero">
        <div className="studio-eyebrow">VITE VIDEO STUDIO</div>
        <h1>Storyboard → Sequential Render</h1>
        <p>VideoFlow đã bật: render tuần tự từng scene, đồng bộ provider runtime với Next Control Plane.</p>
      </section>

      <section className="studio-grid">
        <div className="studio-card">
          <div className="studio-eyebrow">STORYBOARD</div>
          <h2>{handoff.storyboard.length} scenes</h2>
          {handoff.storyboard.map((scene, index) => (
            <div className="studio-row" key={index}>
                <strong>Scene {index + 1}</strong>
                <span>
                  {getSceneTitle(scene, index)}
                  {getScenePrompt(scene) ? ` · ${getScenePrompt(scene)}` : ''}
                </span>
            </div>
          ))}
        </div>

        <div className="studio-card">
          <div className="studio-eyebrow">PROVIDER RUNTIME</div>
          <h2>veo / runway / kling / seedance</h2>
          {PROVIDERS.map((provider) => {
            const isActive = runtimeProviders.includes(provider)
            return (
              <div className="studio-row" key={provider}>
                <strong>{getProviderLabel(provider)}</strong>
                <span>{isActive ? 'active' : 'standby'}</span>
              </div>
            )
          })}
        </div>
      </section>

      <section className="studio-card">
        <div className="studio-eyebrow">VIDEOFLOW RENDER QUEUE</div>
        <h2>Sequential execution</h2>
        <div className="studio-row">
          <span>Runtime status</span>
          <strong>{runtimeStatus?.status || 'running'}</strong>
        </div>
        <div className="studio-row">
          <span>Planned batch size</span>
          <strong>{handoff.planned_batch_size}</strong>
        </div>
        <div className="studio-row">
          <span>Max concurrent render</span>
          <strong>{handoff.max_concurrent_render}</strong>
        </div>
        {runtimeError ? (
          <div className="studio-row">
            <strong>Runtime error</strong>
            <span>{runtimeError}</span>
          </div>
        ) : null}
        {steps.map((step) => (
          <div className="studio-row" key={step.sceneIndex}>
            <strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong>
            <span>{getProviderLabel(step.provider || 'veo')} render · {step.title} · {step.status}{step.artifactPath ? ' · artifact ready' : ''}</span>
          </div>
        ))}
      </section>
    </main>
  )
}
