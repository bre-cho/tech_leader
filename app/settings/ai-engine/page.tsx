import OpenRouterSettingsPanel from "@/components/settings/OpenRouterSettingsPanel";
import GoogleAccountsManager from "@/components/settings/GoogleAccountsManager";

export default function AIEngineSettingsPage() {
  return (
    <main className="brain-route-main">
      <div className="brain-route-wrap">
        <section className="brain-route-head">
          <p className="brain-route-kicker">Model Governance</p>
          <h1 className="brain-route-title">AI Engine Settings</h1>
          <p className="brain-route-desc">
            Quản lý provider, key, routing policy và tham số runtime cho OpenRouter và Google Nano Banana / Veo trên một màn.
          </p>
        </section>

        <section style={{ display: "grid", gap: "1.25rem" }}>
          <p className="brain-route-kicker">OpenRouter</p>
          <OpenRouterSettingsPanel />
        </section>

        <section style={{ display: "grid", gap: "1.25rem" }}>
          <p className="brain-route-kicker">Google Accounts — Nano Banana &amp; Veo 3.1</p>
          <GoogleAccountsManager />
        </section>
      </div>
    </main>
  );
}
