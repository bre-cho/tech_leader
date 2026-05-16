'use client'
import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import type { GeneratedSourceImage, ProviderDurationProfile, ProviderKey, RenderStep, StoryboardPlan } from '@/types/creative-os'

const PROJECT_ID = 'demo-project'
const API_TIMEOUT_MS = 30000  // 30 seconds to allow for slower networks/concurrent requests
type ApiState = 'connected' | 'degraded' | 'down'

const providerDefaults: Record<ProviderKey, number> = {
    veo: 8,
    runway: 5,
    kling: 5,
    seedance: 6,
}

const defaultRuntimeLogs = [
    'Strategy Agent ready',
    'Research Agent waiting for storyboard plan',
    'Image Agent waiting for source',
    'Storyboard Agent idle',
    'Provider Runtime locked to sequential render',
]

async function fetchJsonWithTimeout<T>(url: string, init: RequestInit, actionLabel: string): Promise<T> {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), API_TIMEOUT_MS)

    try {
        const response = await fetch(url, { ...init, signal: controller.signal })
        if (!response.ok) {
            const detail = await response.text()
            const message = detail || response.statusText || 'Unknown API error'
            throw new Error(`${actionLabel} failed (${response.status}): ${message}`)
        }
        return await response.json() as T
    } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
            throw new Error(`${actionLabel} timeout sau ${Math.round(API_TIMEOUT_MS / 1000)} giây.`)
        }
        throw error
    } finally {
        clearTimeout(timer)
    }
}

function compactImageReference(url: string, source: 'upload' | 'generated'): string {
    if (!url.startsWith('data:')) return url
    return source === 'upload' ? 'upload://local-device-image' : 'generated://inline-preview'
}

export function CreativeOSControlPlane() {
    const [imageSource, setImageSource] = useState<'upload' | 'generated'>('upload')
    const [imageUrl, setImageUrl] = useState('/uploads/demo-winner-image.png')
    const [imagePrompt, setImagePrompt] = useState('Luxury skincare product hero shot, studio lighting, premium cosmetic bottle, clean beauty campaign')
    const [duration, setDuration] = useState(60)
    const [provider, setProvider] = useState<ProviderKey>('kling')
    const [plannedBatchSize, setPlannedBatchSize] = useState(6)
    const [plan, setPlan] = useState<StoryboardPlan | null>(null)
    const [renderSteps, setRenderSteps] = useState<RenderStep[]>([])
    const [providerProfiles, setProviderProfiles] = useState<Record<string, ProviderDurationProfile>>({})
    const [isPlanning, setIsPlanning] = useState(false)
    const [apiError, setApiError] = useState<string | null>(null)
    const [runtimeLogs, setRuntimeLogs] = useState<string[]>(defaultRuntimeLogs)
    const [profilesStatus, setProfilesStatus] = useState<ApiState>('degraded')
    const [storyboardStatus, setStoryboardStatus] = useState<ApiState>('degraded')
    const [queueStatus, setQueueStatus] = useState<ApiState>('degraded')
    const [eventsStatus, setEventsStatus] = useState<ApiState>('degraded')
    const [sourceStatus, setSourceStatus] = useState<ApiState>('degraded')
    const [sourceError, setSourceError] = useState<string | null>(null)
    const [isGeneratingSource, setIsGeneratingSource] = useState(false)

    const overallHealth = useMemo(() => {
        const statuses: ApiState[] = [profilesStatus, storyboardStatus, queueStatus, eventsStatus]
        if (statuses.some((status) => status === 'down')) {
            return {
                tone: 'is-down',
                title: 'Backend Down',
                detail: 'Có ít nhất một khối không kết nối được backend hoặc event stream.',
            }
        }
        if (statuses.every((status) => status === 'connected')) {
            return {
                tone: 'is-healthy',
                title: 'Backend Healthy',
                detail: 'Toàn bộ khối chính đang đồng bộ với backend và event stream hoạt động.',
            }
        }
        return {
            tone: 'is-degraded',
            title: 'Partial Degradation',
            detail: 'Một phần khối đang chờ dữ liệu hoặc mới kết nối một phần với backend.',
        }
    }, [eventsStatus, profilesStatus, queueStatus, storyboardStatus])

    useEffect(() => {
        let isMounted = true

        async function loadProviderProfiles() {
            try {
                setProfilesStatus('degraded')
                const data = await fetchJsonWithTimeout<Record<string, ProviderDurationProfile>>(
                    '/api/v1/creative-os/provider-profiles',
                    { method: 'GET' },
                    'Load provider profiles',
                )
                if (!isMounted) return
                setProviderProfiles(data)
                setProfilesStatus('connected')

                const profile = data[provider]
                if (profile?.default_planned_batch_size) {
                    setPlannedBatchSize(profile.default_planned_batch_size)
                }
            } catch (error) {
                if (!isMounted) return
                const message = error instanceof Error ? error.message : 'Không thể tải provider profiles từ backend API.'
                setApiError(message)
                setProfilesStatus('down')
                setRuntimeLogs((prev) => [`Provider profile error: ${message}`, ...prev])
            }
        }

        loadProviderProfiles()

        return () => {
            isMounted = false
        }
    }, [provider])

    useEffect(() => {
        let isMounted = true
        let pollingInterval: ReturnType<typeof setInterval> | null = null
        let lastCount = 0

        async function pollEvents() {
            try {
                const response = await fetch(`/api/v1/creative-os/projects/${PROJECT_ID}/events`)
                if (!response.ok) throw new Error(`Events: ${response.status}`)

                const events = (await response.json()) as Array<{ message?: string }>
                if (!isMounted) return

                // Only display new events
                if (events.length > lastCount) {
                    events.slice(lastCount).forEach((e) => {
                        const msg = e?.message
                        if (typeof msg === 'string' && msg.length > 0) {
                            setRuntimeLogs((prev) => [msg, ...prev].slice(0, 16))
                        }
                    })
                    lastCount = events.length
                }
                setEventsStatus('connected')
            } catch (error) {
                if (!isMounted) return
                const message = error instanceof Error ? error.message : 'Events polling failed'
                setRuntimeLogs((prev) => [`Runtime events error: ${message}`, ...prev].slice(0, 16))
                setEventsStatus('degraded')
            }
        }

        // Start polling immediately, then every 2 seconds
        pollEvents()
        pollingInterval = setInterval(pollEvents, 2000)

        return () => {
            isMounted = false
            if (pollingInterval) clearInterval(pollingInterval)
        }
    }, [])

    const estimated = useMemo(() => {
        const recommended = providerProfiles[provider]?.recommended_duration_per_scene ?? providerDefaults[provider]
        const sceneCount = Math.max(1, Math.ceil(duration / recommended))
        const sceneDuration = Number((duration / sceneCount).toFixed(2))
        return {
            recommended,
            sceneCount,
            sceneDuration,
            totalBatches: Math.ceil(sceneCount / plannedBatchSize),
        }
    }, [duration, provider, plannedBatchSize, providerProfiles])

    async function generatePlan() {
        setIsPlanning(true)
        setApiError(null)
        setPlan(null)
        setRenderSteps([])
        setStoryboardStatus('degraded')
        setQueueStatus('degraded')
        setRuntimeLogs((prev) => ['Planning storyboard via backend API...', ...prev])

        try {
            const compactImageUrl = compactImageReference(imageUrl, imageSource)
            const planData = await fetchJsonWithTimeout<StoryboardPlan>(
                `/api/v1/creative-os/projects/${PROJECT_ID}/plan-storyboard`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_source: imageSource,
                        image_url: compactImageUrl,
                        target_video_duration: duration,
                        provider,
                        planned_batch_size: plannedBatchSize,
                        max_concurrent_render: 1,
                    }),
                },
                'Plan storyboard',
            )
            setPlan(planData)
            setStoryboardStatus('connected')

            const steps = await fetchJsonWithTimeout<RenderStep[]>(
                `/api/v1/creative-os/projects/${PROJECT_ID}/render-steps?scene_count=${planData.scene_count}&planned_batch_size=${planData.planned_batch_size}`,
                { method: 'GET' },
                'Load render steps',
            )
            setRenderSteps(steps)
            setQueueStatus('connected')
            setRuntimeLogs((prev) => [
                `Storyboard planned: ${planData.scene_count} scenes / ${planData.total_batches} batches`,
                compactImageUrl !== imageUrl ? 'Using compact image reference for planning payload.' : 'Using direct image URL for planning payload.',
                'Render steps loaded from backend queue',
                ...prev,
            ])
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Backend planning failed.'
            setApiError(message)
            if (message.includes('Plan storyboard')) {
                setStoryboardStatus('down')
                setQueueStatus('down')
            } else {
                setQueueStatus('down')
            }
            setRuntimeLogs((prev) => [`Planning failed: ${message}`, ...prev])
        } finally {
            setIsPlanning(false)
        }
    }

    function handleSourceImageUpload(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0]
        if (!file) return

        const reader = new FileReader()
        setSourceError(null)
        setSourceStatus('degraded')

        reader.onload = () => {
            const value = typeof reader.result === 'string' ? reader.result : ''
            if (!value) {
                setSourceError('Không thể đọc ảnh từ thiết bị.')
                setSourceStatus('down')
                return
            }

            setImageSource('upload')
            setImageUrl(value)
            setSourceStatus('connected')
            setRuntimeLogs((prev) => [`Source image loaded from device: ${file.name}`, ...prev].slice(0, 16))
        }

        reader.onerror = () => {
            setSourceError('Đọc file ảnh thất bại.')
            setSourceStatus('down')
        }

        reader.readAsDataURL(file)
    }

    async function generateSourceImage() {
        setIsGeneratingSource(true)
        setSourceError(null)
        setSourceStatus('degraded')

        try {
            const data = await fetchJsonWithTimeout<GeneratedSourceImage>(
                '/api/v1/creative-os/source-image/generate',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: imagePrompt,
                        aspectRatio: '4:5',
                        resolution: '2K',
                    }),
                },
                'Generate source image',
            )

            setImageSource('generated')
            setImageUrl(data.image_url)
            setSourceStatus('connected')
            setRuntimeLogs((prev) => [`AI source image generated: ${data.model}${data.is_mock ? ' (mock fallback)' : ''}`, ...prev].slice(0, 16))
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Generate source image failed.'
            setSourceError(message)
            setSourceStatus('down')
            setRuntimeLogs((prev) => [`Source image generation failed: ${message}`, ...prev].slice(0, 16))
        } finally {
            setIsGeneratingSource(false)
        }
    }

    function openVideoStudio() {
        if (!plan) {
            setRuntimeLogs((prev) => ['[HANDOFF] No plan available.', ...prev].slice(0, 16))
            return
        }

        const payload = JSON.stringify({
            project_id: plan.project_id,
            winner_image_url: plan.image_url,
            storyboard: plan.scenes,
            provider_targets: [plan.provider],
            render_mode: 'image_to_video',
            planned_batch_size: plan.planned_batch_size,
            max_concurrent_render: 1,
            execution_mode: 'sequential',
        })

        const handoffUrl = 'https://shiny-memory-gxq4x7jx7xv6fjw9-5173.app.github.dev/creative-os?handoff=1'

        // Open immediately in user-click sync flow to avoid popup blockers.
        const popup = window.open('about:blank', '_blank')
        if (!popup) {
            setRuntimeLogs((prev) => [
                '[HANDOFF] Popup bị chặn. Hãy cho phép popup cho trang này.',
                ...prev,
            ].slice(0, 16))
            return
        }

        // Send payload via window.name to avoid oversized query strings (about:blank#blocked).
        popup.name = payload
        popup.location.href = handoffUrl
        setRuntimeLogs((prev) => [
            `[HANDOFF] Opened Video Studio: ${handoffUrl}`,
            `[HANDOFF] Handoff complete: ${plan.scene_count} scenes / ${plan.total_batches} batches`,
            ...prev,
        ].slice(0, 16))
    }

    return (
        <main className="creative-os-shell">
            <section className="creative-os-main">
                <div className="os-column-heading">MAIN CONTENT</div>

                <section className={`os-overall-status ${overallHealth.tone}`}>
                    <div className="os-overall-label">SYSTEM HEALTH</div>
                    <h2>{overallHealth.title}</h2>
                    <p>{overallHealth.detail}</p>
                </section>

                <div className="os-hero">
                    <div>
                        <div className="os-eyebrow">AI CREATIVE PRODUCTION OPERATING SYSTEM</div>
                        <h1>Image → Storyboard → Video</h1>
                        <p>Upload ảnh hoặc dùng ảnh AI tạo ra, nhập thời lượng video, chọn provider, tự tính số cảnh và render tuần tự từng cảnh.</p>
                    </div>
                    <button className="os-primary" onClick={generatePlan} disabled={isPlanning}>
                        {isPlanning ? 'Generating via Backend...' : 'Generate Storyboard Plan'}
                    </button>
                </div>

                {apiError ? <div className="os-api-error">{apiError}</div> : null}

                <div className="os-grid">
                    <section className="os-card">
                        <div className="os-card-head"><div className="os-eyebrow">IMAGE SOURCE PANEL</div><ApiBadge state={sourceStatus} label="source image" /></div>
                        <h2>Ảnh nguồn</h2>
                        <div className="os-form-grid">
                            <label className="os-label">Nguồn ảnh<select value={imageSource} onChange={(e) => setImageSource(e.target.value as 'upload' | 'generated')}><option value="upload">Upload từ thiết bị</option><option value="generated">Ảnh AI/code tạo ra</option></select></label>
                            <label className="os-label">Image URL<input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} /></label>
                            <label className="os-label">Upload ảnh<input type="file" accept="image/*" onChange={handleSourceImageUpload} /></label>
                            <label className="os-label">Prompt tạo ảnh AI<textarea className="os-textarea" value={imagePrompt} onChange={(e) => setImagePrompt(e.target.value)} /></label>
                        </div>
                        <div className="os-source-actions">
                            <button className="os-secondary" onClick={generateSourceImage} disabled={isGeneratingSource}>{isGeneratingSource ? 'Generating image...' : 'Generate AI Source Image'}</button>
                            <span className="os-muted">Upload ảnh từ thiết bị hoặc tạo ảnh AI bằng code rồi dùng chung cho backend plan-storyboard.</span>
                        </div>
                        {sourceError ? <div className="os-api-error">{sourceError}</div> : null}
                        {imageSource === 'generated' && imageUrl ? <p className="os-muted">Generated source đang dùng cho storyboard planning. Nếu thiếu API key, hệ thống tự dùng mock fallback để demo UI.</p> : null}
                        <div className="os-image-preview">{imageUrl ? <img src={imageUrl} alt={imageSource === 'upload' ? 'Uploaded source' : 'Generated source'} className="os-preview-image" /> : imageSource === 'upload' ? 'UPLOADED IMAGE' : 'GENERATED IMAGE'}</div>
                    </section>

                    <section className="os-card">
                        <div className="os-card-head"><div className="os-eyebrow">DURATION + PROVIDER PLANNER</div><ApiBadge state={profilesStatus} label="Profiles" /></div>
                        <h2>Tính số cảnh và batch</h2>
                        <div className="os-form-grid">
                            <label className="os-label">Thời lượng video<input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} /></label>
                            <label className="os-label">Provider<select value={provider} onChange={(e) => setProvider(e.target.value as ProviderKey)}><option value="veo">Veo</option><option value="runway">Runway</option><option value="kling">Kling</option><option value="seedance">Seedance</option></select></label>
                            <label className="os-label">Số cảnh/batch kế hoạch<input type="number" value={plannedBatchSize} onChange={(e) => setPlannedBatchSize(Number(e.target.value))} /></label>
                            <label className="os-label">Render đồng thời<input value="1 cảnh" readOnly /></label>
                        </div>
                        <div className="os-metrics-grid">
                            <Metric label="Số cảnh" value={estimated.sceneCount} />
                            <Metric label="Thời lượng/cảnh" value={`${estimated.sceneDuration}s`} />
                            <Metric label="Tổng batch" value={estimated.totalBatches} />
                            <Metric label="Mode" value="Sequential" />
                        </div>
                    </section>
                </div>

                <section className="os-card">
                    <div className="os-card-head"><div className="os-eyebrow">IMAGE BATTLE VIEW</div><ApiBadge state={storyboardStatus} label="Plan payload" /></div>
                    <h2>Mapping backend input</h2>
                    <div className="os-card-mini">
                        <div className="os-status"><span>Project ID</span><strong>{PROJECT_ID}</strong></div>
                        <div className="os-status"><span>Image source</span><strong>{imageSource}</strong></div>
                        <div className="os-status"><span>Winner image URL</span><strong>{imageUrl || '-'}</strong></div>
                        <div className="os-status"><span>Provider</span><strong>{provider}</strong></div>
                        <p className="os-muted">Khối này map trực tiếp vào payload của endpoint plan-storyboard. Backend hiện chưa có endpoint chấm điểm A/B/C riêng.</p>
                    </div>
                </section>

                <section className="os-card">
                    <div className="os-card-head"><div className="os-eyebrow">STORYBOARD DEPENDENCY GRAPH</div><ApiBadge state={storyboardStatus} label="plan-storyboard" /></div>
                    <h2>{plan ? `${plan.scene_count} cảnh từ ảnh thắng` : 'Chưa có storyboard từ backend'}</h2>
                    {plan ? (
                        <div className="os-chain">
                            {plan.scenes.map((scene) => (
                                <article className="os-scene-card" key={scene.id}>
                                    <strong>Scene {scene.index}</strong>
                                    <h3>{scene.title}</h3>
                                    <p>Camera: {scene.camera}</p>
                                    <p>Motion: {scene.motion}</p>
                                    <p>Duration: {scene.duration}s</p>
                                    <p>Provider: {scene.provider}</p>
                                </article>
                            ))}
                        </div>
                    ) : (
                        <p className="os-muted">Nhấn Generate Storyboard Plan để lấy dữ liệu storyboard thật từ backend.</p>
                    )}
                </section>

                <section className="os-card">
                    <div className="os-card-head"><div className="os-eyebrow">SAFE SEQUENTIAL RENDER QUEUE</div><ApiBadge state={queueStatus} label="render-steps" /></div>
                    <h2>Batch kế hoạch — render từng cảnh một</h2>
                    <div className="os-metrics-grid">
                        <Metric label="Planned batch size" value={plan?.planned_batch_size ?? plannedBatchSize} />
                        <Metric label="Max concurrent render" value="1 cảnh" />
                        <Metric label="Total batches" value={plan?.total_batches ?? '-'} />
                        <Metric label="Overload risk" value={renderSteps.length > 0 ? 'Low' : 'Pending'} />
                    </div>
                    {renderSteps.length > 0 ? (
                        <div className="os-batch-list">
                            {renderSteps.map((step) => (
                                <div className="os-batch-card" key={`step-${step.batch_index}-${step.scene_index}`}>
                                    <strong>Batch {step.batch_index}</strong>
                                    <span>Scene {step.scene_index}</span>
                                    <em>{step.execution_mode} / {step.status}</em>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="os-muted">Render queue map từ endpoint render-steps, sẽ hiển thị sau khi plan-storyboard trả về scene_count.</p>
                    )}
                </section>

                <section className="os-card">
                    <div className="os-card-head"><div className="os-eyebrow">VIDEO HANDOFF</div><ApiBadge state={plan ? 'connected' : storyboardStatus === 'down' ? 'down' : 'degraded'} label="handoff" /></div>
                    <h2>Gửi sang Vite Video Studio</h2>
                    <button className="os-primary" onClick={openVideoStudio} disabled={!plan}>Open Vite Video Studio</button>
                    {!plan ? <p className="os-muted">Cần plan từ backend trước khi handoff.</p> : null}
                    {plan ? <p className="os-muted">Payload handoff dùng scenes/batches từ response plan-storyboard.</p> : null}
                </section>
            </section>

            <aside className="os-right-panel">
                <div className="os-column-heading">LIVE RUNTIME</div>
                <section className="os-card">
                    <div className="os-card-head"><div className="os-eyebrow">LIVE RUNTIME</div><ApiBadge state={eventsStatus} label="events" /></div>
                    <h2>Agent Runtime (events stream)</h2>
                    {runtimeLogs.map((log, index) => (
                        <div className="os-runtime-log" key={`${index}-${log}`}>{log}</div>
                    ))}
                </section>

                {plan ? (
                    <section className="os-card">
                        <div className="os-card-head"><div className="os-eyebrow">PROVIDER STATUS</div><ApiBadge state={profilesStatus} label="provider-profiles" /></div>
                        <h2>{plan.provider.toUpperCase()}</h2>
                        <Metric label="Scene count" value={plan.scene_count} />
                        <Metric label="Batch size" value={plan.planned_batch_size} />
                        <Metric label="Concurrency" value="1/1" />
                        <Metric label="Mode" value="Sequential" />
                        <Metric label="Cooldown" value={`${providerProfiles[plan.provider]?.cooldown_seconds ?? '-'}s`} />
                        <Metric label="Retry limit" value={providerProfiles[plan.provider]?.retry_limit ?? '-'} />
                    </section>
                ) : null}
            </aside>
        </main>
    )
}

function Metric({ label, value }: { label: string; value: string | number }) {
    return <div className="os-status"><span>{label}</span><strong>{value}</strong></div>
}

function ApiBadge({ state, label }: { state: ApiState; label: string }) {
    const tone = state === 'connected' ? 'is-connected' : state === 'degraded' ? 'is-degraded' : 'is-down'
    const text = state === 'connected' ? 'Connected' : state === 'degraded' ? 'Degraded' : 'Down'
    return <span className={`os-api-badge ${tone}`}>{label}: {text}</span>
}
