import BeautyCommerceV28Studio from "@/components/beauty-commerce-v28/BeautyCommerceV28Studio";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";

export default function Page() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-8 pt-8">
        <OperationFlowBridge sourceKey="beauty-commerce-v28" title="BEAUTY COMMERCE V28 - OPERATION FLOW" />
      </section>
      <BeautyCommerceV28Studio />
    </div>
  );
}
