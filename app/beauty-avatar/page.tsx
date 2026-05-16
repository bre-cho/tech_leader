import VirtualAvatarStudio from "@/components/beauty-avatar/VirtualAvatarStudio";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";

export default function BeautyAvatarPage() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-8 pt-8">
        <OperationFlowBridge sourceKey="beauty-avatar" title="BEAUTY AVATAR - OPERATION FLOW" />
      </section>
      <VirtualAvatarStudio />
    </div>
  );
}
