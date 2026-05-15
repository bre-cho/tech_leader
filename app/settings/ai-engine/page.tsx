import GoogleAccountsManager from "@/components/settings/GoogleAccountsManager";
import OpenRouterSettingsPanel from "@/components/settings/OpenRouterSettingsPanel";
import NanoBananaAccountsPanel from "@/components/settings/NanoBananaAccountsPanel";

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
      </div>
    </main>
  );
}
