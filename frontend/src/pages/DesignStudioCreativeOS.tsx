import { readVideoHandoffFromUrl } from '../creative-os/runtime/videoHandoffReceiver';
import { KnowledgeTimelineRuntime } from '../creative-os/KnowledgeTimelineRuntime';
import '../styles/creative-os.css';

type StoryboardScene = {
  title?: string;
};

export default function DesignStudioCreativeOS() {
  const handoff = readVideoHandoffFromUrl();

  if (!handoff) {
    return (
      <main className="studio-shell">
        <section className="studio-card hero">
          <div className="studio-eyebrow">REALTIME VIDEO STUDIO</div>
          <h1>Waiting for Storyboard Handoff</h1>
          <p>Gui storyboard tu Next.js Control Plane de bat dau.</p>
        </section>
      </main>
    );
  }

  const steps = handoff.storyboard.map((_, index) => ({
    sceneIndex: index + 1,
    batchIndex: Math.ceil((index + 1) / handoff.planned_batch_size),
  }));

  return (
    <main className="studio-shell">
      <section className="studio-card hero">
        <div className="studio-eyebrow">VITE VIDEO STUDIO</div>
        <h1>Storyboard to Sequential Render</h1>
        <p>Batch la nhom ke hoach. He thong chi render 1 canh tai mot thoi diem.</p>
      </section>

      <section className="studio-grid">
        <div className="studio-card">
          <div className="studio-eyebrow">STORYBOARD</div>
          <h2>{handoff.storyboard.length} scenes</h2>
          {handoff.storyboard.map((scene, index) => {
            const typedScene = scene as StoryboardScene;
            return (
              <div className="studio-row" key={index}>
                <strong>Scene {index + 1}</strong>
                <span>{typedScene.title || 'Scene'}</span>
              </div>
            );
          })}
        </div>

        <div className="studio-card">
          <div className="studio-eyebrow">SAFE RENDER QUEUE</div>
          <h2>Sequential</h2>
          <div className="studio-row">
            <span>Planned batch size</span>
            <strong>{handoff.planned_batch_size}</strong>
          </div>
          <div className="studio-row">
            <span>Max concurrent render</span>
            <strong>1</strong>
          </div>
          {steps.map((step) => (
            <div className="studio-row" key={step.sceneIndex}>
              <strong>Batch {step.batchIndex}</strong>
              <span>Scene {step.sceneIndex} queued</span>
            </div>
          ))}
        </div>
      </section>

      <KnowledgeTimelineRuntime />
    </main>
  );
}
