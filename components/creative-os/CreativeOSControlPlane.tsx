'use client';

import { useMemo, useState } from 'react';

import type { ProviderKey, StoryboardPlan } from '@/types/creative-os';
import { ObsidianVaultPanel } from '@/components/creative-os/ObsidianVaultPanel';
import { WikiKnowledgeGraph } from '@/components/creative-os/WikiKnowledgeGraph';

const steps = [
  'Creative Brief',
  'Image Source',
  'Duration Planner',
  'Provider Selection',
  'Image Battle',
  'Winner Selection',
  'Storyboard Builder',
  'Batch Planner',
  'Sequential Render',
  'Video Handoff',
  'Delivery',
  'Memory Learning',
];

const providerDuration: Record<ProviderKey, number> = {
  veo: 8,
  runway: 5,
  kling: 5,
  seedance: 6,
};

export function CreativeOSControlPlane() {
  const [imageSource, setImageSource] = useState<'upload' | 'generated'>('upload');
  const [imageUrl, setImageUrl] = useState('/uploads/demo-winner-image.png');
  const [duration, setDuration] = useState(60);
  const [provider, setProvider] = useState<ProviderKey>('kling');
  const [plannedBatchSize, setPlannedBatchSize] = useState(6);
  const [plan, setPlan] = useState<StoryboardPlan | null>(null);

  const estimated = useMemo(() => {
    const recommended = providerDuration[provider];
    const sceneCount = Math.max(1, Math.ceil(duration / recommended));
    const sceneDuration = Number((duration / sceneCount).toFixed(2));
    return {
      recommended,
      sceneCount,
      sceneDuration,
      totalBatches: Math.ceil(sceneCount / plannedBatchSize),
    };
  }, [duration, provider, plannedBatchSize]);

  function generatePlan() {
    const scenes = Array.from({ length: estimated.sceneCount }).map((_, index) => ({
      id: `scene-${index + 1}`,
      index: index + 1,
      title: ['Hook Scene', 'Product Focus', 'Desire Scene', 'Trust Scene', 'Transformation', 'CTA Scene'][index % 6],
      camera: ['slow push-in', 'macro beauty shot', 'portrait close-up', 'medium shot', 'smooth reveal', 'logo reveal'][index % 6],
      motion: ['cinematic glide', 'soft rotation', 'slow zoom', 'light drift', 'before-after motion', 'front hero motion'][index % 6],
      subtitle: ['Open with attention', 'Show product details', 'Build desire', 'Increase trust', 'Show transformation', 'Call to action'][index % 6],
      provider,
      duration: estimated.sceneDuration,
      continuity_key: `continuity_scene_${String(index + 1).padStart(2, '0')}`,
      status: 'planned',
    }));

    const batches = [];
    for (let i = 0; i < scenes.length; i += plannedBatchSize) {
      batches.push({
        id: `batch-${batches.length + 1}`,
        batch_index: batches.length + 1,
        scene_indexes: scenes.slice(i, i + plannedBatchSize).map((s) => s.index),
        planned_batch_size: plannedBatchSize,
        max_concurrent_render: 1 as const,
        execution_mode: 'sequential',
        status: 'queued',
      });
    }

    setPlan({
      project_id: 'demo-project',
      image_source: imageSource,
      image_url: imageUrl,
      target_video_duration: duration,
      provider,
      recommended_duration_per_scene: estimated.recommended,
      scene_count: estimated.sceneCount,
      scene_duration: estimated.sceneDuration,
      planned_batch_size: plannedBatchSize,
      max_concurrent_render: 1,
      total_batches: estimated.totalBatches,
      execution_mode: 'sequential',
      scenes,
      batches,
    });
  }

  function openVideoStudio() {
    if (!plan) return;
    const payload = encodeURIComponent(
      JSON.stringify({
        project_id: plan.project_id,
        winner_image_url: plan.image_url,
        storyboard: plan.scenes,
        provider_targets: [plan.provider],
        render_mode: 'image_to_video',
        planned_batch_size: plan.planned_batch_size,
        max_concurrent_render: 1,
        execution_mode: 'sequential',
      })
    );
    const studioUrl = process.env.NEXT_PUBLIC_VIDEO_STUDIO_URL || 'http://localhost:5173';
    window.open(`${studioUrl}?handoff=${payload}`, '_blank');
  }

  return (
    <main className="creative-os-shell">
      <aside className="os-sidebar">
        <div className="os-logo">Creative OS</div>
        <p className="os-muted">Pipeline-based sidebar, not module launcher.</p>
        <div className="os-stage-list">
          {steps.map((s, i) => (
            <button className={i < 4 ? 'os-stage active' : 'os-stage'} key={s}>
              <span>{String(i + 1).padStart(2, '0')}</span>
              <strong>{s}</strong>
            </button>
          ))}
        </div>
      </aside>

      <section className="creative-os-main">
        <div className="os-hero">
          <div>
            <div className="os-eyebrow">AI CREATIVE PRODUCTION OPERATING SYSTEM</div>
            <h1>Image to Storyboard to Video</h1>
            <p>
              Upload image or use generated image, set target video duration,
              choose provider, then plan scene count and safe sequential render.
            </p>
          </div>
          <button className="os-primary" onClick={generatePlan}>
            Generate Storyboard Plan
          </button>
        </div>

        <div className="os-grid">
          <section className="os-card">
            <div className="os-eyebrow">IMAGE SOURCE PANEL</div>
            <h2>Source Image</h2>
            <div className="os-form-grid">
              <label className="os-label">
                Image source
                <select value={imageSource} onChange={(e) => setImageSource(e.target.value as 'upload' | 'generated')}>
                  <option value="upload">Upload from device</option>
                  <option value="generated">Generated image</option>
                </select>
              </label>
              <label className="os-label">
                Image URL
                <input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} />
              </label>
            </div>
            <div className="os-image-preview">{imageSource === 'upload' ? 'UPLOADED IMAGE' : 'GENERATED IMAGE'}</div>
          </section>

          <section className="os-card">
            <div className="os-eyebrow">DURATION AND PROVIDER PLANNER</div>
            <h2>Plan scenes and batches</h2>
            <div className="os-form-grid">
              <label className="os-label">
                Target duration
                <input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
              </label>
              <label className="os-label">
                Provider
                <select value={provider} onChange={(e) => setProvider(e.target.value as ProviderKey)}>
                  <option value="veo">Veo</option>
                  <option value="runway">Runway</option>
                  <option value="kling">Kling</option>
                  <option value="seedance">Seedance</option>
                </select>
              </label>
              <label className="os-label">
                Planned scenes per batch
                <input
                  type="number"
                  value={plannedBatchSize}
                  onChange={(e) => setPlannedBatchSize(Number(e.target.value))}
                />
              </label>
              <label className="os-label">
                Concurrent render
                <input value="1 scene" readOnly />
              </label>
            </div>
            <div className="os-metrics-grid">
              <Metric label="Scene count" value={estimated.sceneCount} />
              <Metric label="Duration per scene" value={`${estimated.sceneDuration}s`} />
              <Metric label="Total batches" value={estimated.totalBatches} />
              <Metric label="Mode" value="Sequential" />
            </div>
          </section>
        </div>

        <section className="os-card">
          <div className="os-eyebrow">IMAGE BATTLE VIEW</div>
          <h2>Image A/B/C and winner selection</h2>
          <div className="os-battle-grid">
            {['A', 'B', 'C'].map((id, i) => (
              <article className="os-card-mini" key={id}>
                <div className="os-image-preview">IMAGE {id}</div>
                <Metric label="Heat score" value={[91, 88, 95][i]} />
                <Metric label="CTR" value={['3.1%', '2.9%', '3.6%'][i]} />
                <button className="os-secondary">Select Winner</button>
              </article>
            ))}
          </div>
        </section>

        <div className="os-grid">
          <ObsidianVaultPanel />
          <WikiKnowledgeGraph />
        </div>

        {plan ? (
          <>
            <section className="os-card">
              <div className="os-eyebrow">STORYBOARD GRAPH</div>
              <h2>{plan.scene_count} scenes from winner image</h2>
              <div className="os-chain">
                {plan.scenes.map((scene) => (
                  <article className="os-scene-card" key={scene.id}>
                    <strong>Scene {scene.index}</strong>
                    <h3>{scene.title}</h3>
                    <p>Camera: {scene.camera}</p>
                    <p>Duration: {scene.duration}s</p>
                    <p>Provider: {scene.provider}</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="os-card">
              <div className="os-eyebrow">SAFE SEQUENTIAL RENDER QUEUE</div>
              <h2>Planned batches with one-scene-at-a-time render</h2>
              <div className="os-metrics-grid">
                <Metric label="Planned batch size" value={plan.planned_batch_size} />
                <Metric label="Max concurrent render" value="1 scene" />
                <Metric label="Total batches" value={plan.total_batches} />
                <Metric label="Overload risk" value="Low" />
              </div>
              <div className="os-batch-list">
                {plan.batches.map((b) => (
                  <div className="os-batch-card" key={b.id}>
                    <strong>Batch {b.batch_index}</strong>
                    <span>Scenes {b.scene_indexes.join(', ')}</span>
                    <em>Render runs sequentially for each scene.</em>
                  </div>
                ))}
              </div>
            </section>

            <section className="os-card">
              <div className="os-eyebrow">VIDEO HANDOFF</div>
              <h2>Send to Vite Video Studio</h2>
              <button className="os-primary" onClick={openVideoStudio}>
                Open Vite Video Studio
              </button>
            </section>
          </>
        ) : null}
      </section>

      <aside className="os-right-panel">
        <section className="os-card">
          <div className="os-eyebrow">LIVE RUNTIME</div>
          <h2>Agent Runtime</h2>
          {[
            'Strategy Agent ready',
            'Image Agent ready',
            'Storyboard Agent ready',
            'Provider Runtime locked to sequential render',
          ].map((x) => (
            <div className="os-runtime-log" key={x}>
              {x}
            </div>
          ))}
        </section>

        {plan ? (
          <section className="os-card">
            <div className="os-eyebrow">PROVIDER STATUS</div>
            <h2>{plan.provider.toUpperCase()}</h2>
            <Metric label="Scene count" value={plan.scene_count} />
            <Metric label="Concurrency" value="1/1" />
            <Metric label="Mode" value="Sequential" />
          </section>
        ) : null}
      </aside>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="os-status">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
