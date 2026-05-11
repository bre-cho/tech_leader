"use client";

type Scene = {
  scene: number;
  role: string;
  prompt: string;
};

type Props = {
  scenes: Scene[];
};

export function StoryboardPanel({ scenes }: Props) {
  if (!scenes.length) {
    return null;
  }

  return (
    <section className="rounded-2xl bg-neutral-900 p-6">
      <h2 className="text-2xl font-semibold">Storyboard Preview</h2>
      <div className="grid md:grid-cols-5 gap-3 mt-4">
        {scenes.map((s) => (
          <div key={s.scene} className="rounded-xl bg-neutral-800 p-4">
            <p className="text-yellow-300">Scene {s.scene}</p>
            <h3 className="font-semibold">{s.role}</h3>
            <p className="text-sm text-neutral-400 mt-2">{s.prompt}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
