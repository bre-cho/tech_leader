import OpenRouterSettingsPanel from "@/components/settings/OpenRouterSettingsPanel";
import NanoBananaAccountsPanel from "@/components/settings/NanoBananaAccountsPanel";

export default function AIEngineSettingsPage() {
  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <div className="mx-auto max-w-6xl">
        <OpenRouterSettingsPanel />
        <NanoBananaAccountsPanel />
      </div>
    </main>
  );
}
