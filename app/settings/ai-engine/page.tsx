import GoogleAccountsManager from "@/components/settings/GoogleAccountsManager";
import KieAccountsPanel from "@/components/settings/KieAccountsPanel";
import NanoBananaAccountsPanel from "@/components/settings/NanoBananaAccountsPanel";
import OpenRouterSettingsPanel from "@/components/settings/OpenRouterSettingsPanel";

export default function AIEngineSettingsPage() {
  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <div className="mx-auto max-w-6xl">
        <section className="mb-6 rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <p className="text-xs uppercase tracking-[0.24em] text-amber-300">Settings</p>
          <h1 className="mt-2 text-3xl font-bold">AI Engine And Provider Account Management</h1>
          <p className="mt-2 text-neutral-300">
            Configure OpenRouter, NanoBanana, and Google account rotation to keep IMAGE -&gt; STORYBOARD -&gt; VIDEO
            runtime stable under production load.
          </p>
        </section>

        <OpenRouterSettingsPanel />
        <NanoBananaAccountsPanel />
        <GoogleAccountsManager />

        {/* Bytedance Seedance 2.0 via kie.ai */}
        <section className="mt-6 rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <p className="text-xs uppercase tracking-[0.24em] text-violet-400">Video Generation</p>
          <h2 className="mt-2 text-xl font-bold">Bytedance Seedance 2.0 (kie.ai)</h2>
          <p className="mb-6 mt-1 text-sm text-neutral-400">
            Power the Creative OS video render pipeline with Seedance 2.0.
            Select provider <code className="rounded bg-neutral-800 px-1 text-violet-300">seedance2</code> when running a render job.
          </p>
          <KieAccountsPanel />
        </section>
      </div>
    </main>
  );
}
