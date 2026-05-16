import StoryboardV30Studio from "@/components/storyboard-v30/StoryboardV30Studio";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";

export default function Page() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-8 pt-8">
        <OperationFlowBridge sourceKey="storyboard-v30" title="STORYBOARD V30 - OPERATION FLOW" />
      </section>
      <StoryboardV30Studio />
    </div>
  );
}
