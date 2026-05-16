import { readVideoHandoffFromUrl } from '../creative-os/runtime/videoHandoffReceiver'
import '../styles/creative-os.css'

const PROVIDERS = ['veo', 'runway', 'kling', 'seedance'] as const

function getSceneTitle(scene: Record<string, unknown>, index: number): string {
  const title = scene.title
  return typeof title === 'string' && title.trim().length > 0 ? title : `Scene ${index + 1}`
}

export default function DesignStudioCreativeOS() {
  const handoff = readVideoHandoffFromUrl()

  if (!handoff) {
    const params = new URLSearchParams(window.location.search)
    const hasMarker = params.has('handoff')
    const hasNamedPayload = typeof window.name === 'string' && window.name.trim().length > 0

    const reason = hasMarker && !hasNamedPayload
      ? 'Đã nhận marker handoff, nhưng chưa nhận payload từ Next.js (window.name đang rỗng).'
      : hasMarker && hasNamedPayload
        ? 'Đã nhận marker và payload thô, nhưng payload không đúng schema yêu cầu.'
        : 'Chưa nhận marker handoff từ Next.js. Hãy mở từ nút Open Vite Video Studio.'

    return (
      <main className="studio-shell">
        <section className="studio-card hero">
          <div className="studio-eyebrow">REALTIME VIDEO STUDIO</div>
          <h1>Waiting for Storyboard Handoff</h1>
          <p>Gửi storyboard từ Next.js Control Plane để bắt đầu timeline và render tuần tự.</p>
          <p>{reason}</p>
        </section>
      </main>
    )
  }

  const activeProviders = PROVIDERS.filter((provider) => handoff.provider_targets.includes(provider))
  const runtimeProviders = activeProviders.length > 0 ? activeProviders : [handoff.provider_targets[0] ?? 'veo']
  const steps = handoff.storyboard.map((scene, index) => ({
    sceneIndex: index + 1,
    batchIndex: Math.ceil((index + 1) / handoff.planned_batch_size),
    provider: runtimeProviders[index % runtimeProviders.length],
    title: getSceneTitle(scene, index),
  }))

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
              <span>{getSceneTitle(scene, index)}</span>
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
                <strong>{provider.toUpperCase()}</strong>
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
          <span>Planned batch size</span>
          <strong>{handoff.planned_batch_size}</strong>
        </div>
        <div className="studio-row">
          <span>Max concurrent render</span>
          <strong>{handoff.max_concurrent_render}</strong>
        </div>
        {steps.map((step) => (
          <div className="studio-row" key={step.sceneIndex}>
            <strong>Batch {step.batchIndex} · Scene {step.sceneIndex}</strong>
            <span>{step.provider.toUpperCase()} render · {step.title}</span>
          </div>
        ))}
      </section>
    </main>
  )
}
