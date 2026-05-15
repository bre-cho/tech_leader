const steps = [
  { label: "Creative Brief", key: "target_define" },
  { label: "Image Battle + Winner", key: "execute" },
  { label: "Fashion DNA + BPM", key: "plan" },
  { label: "Rhythm Graph + Micro Hooks", key: "execute" },
  { label: "Camera + Runway Escalation", key: "execute" },
  { label: "Retention Validator", key: "verify" },
  { label: "Provider Payload Compiler", key: "distill_to_skill" },
  { label: "Memory + Promotion Gate", key: "memory_update" },
];

type WorkflowSidebarProps = {
  isRunning: boolean;
  result: {
    law_trace?: Partial<Record<string, boolean>>;
  } | null;
};

function stepStatus(
  key: string,
  isRunning: boolean,
  trace: Partial<Record<string, boolean>> | undefined,
): string {
  if (trace?.[key]) {
    return "done";
  }
  if (isRunning) {
    return "running";
  }
  return "waiting";
}

export function WorkflowSidebar({ isRunning, result }: WorkflowSidebarProps) {
  return (
    <aside className="workflow-sidebar">
      <div className="sidebar-title">AI Project OS</div>

      {steps.map((step, index) => (
        <div key={`${step.label}-${index}`} className="workflow-item">
          <div className="workflow-index">{String(index + 1).padStart(2, "0")}</div>

          <div>
            <div className="workflow-name">{step.label}</div>
            <div className="workflow-status">{stepStatus(step.key, isRunning, result?.law_trace)}</div>
          </div>
        </div>
      ))}
    </aside>
  );
}
