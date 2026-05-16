import ColorIntelligenceDashboard from "@/components/creative-infra/ColorIntelligenceDashboard";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";

export default function Page() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-8 pt-8">
        <OperationFlowBridge sourceKey="color-intelligence" title="COLOR INTELLIGENCE - OPERATION FLOW" />
      </section>
      <ColorIntelligenceDashboard />
    </div>
  );
}
