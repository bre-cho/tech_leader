const fallbackChecks = ["Brand visibility", "Subtitle safety", "Provider compatibility", "Continuity drift"];

type ReleaseGatePanelProps = {
  promotionGate: Record<string, unknown> | null;
  verification: Record<string, unknown> | null;
};

function readChecks(verification: Record<string, unknown> | null): string[] {
  if (!verification) {
    return fallbackChecks;
  }
  const checks = verification.checks;
  if (checks && typeof checks === "object") {
    return Object.keys(checks as Record<string, unknown>);
  }
  return fallbackChecks;
}

function checkState(
  key: string,
  verification: Record<string, unknown> | null,
): "PASS" | "FAIL" | "WAIT" {
  if (!verification) {
    return "WAIT";
  }
  const checks = verification.checks;
  if (!checks || typeof checks !== "object") {
    return "WAIT";
  }
  const value = (checks as Record<string, unknown>)[key];
  if (value === true) {
    return "PASS";
  }
  if (value === false) {
    return "FAIL";
  }
  return "WAIT";
}

export function ReleaseGatePanel({ promotionGate, verification }: ReleaseGatePanelProps) {
  const checks = readChecks(verification);

  return (
    <div className="pipeline-card">
      <div className="section-eyebrow">RELEASE GATE</div>

      <h2>Validation Engine</h2>

      <div className="validation-list">
        {checks.map((check) => (
          <div key={check} className="validation-item">
            <span>{check}</span>
            <span className={checkState(check, verification) === "PASS" ? "validation-ok" : "workflow-status"}>
              {checkState(check, verification)}
            </span>
          </div>
        ))}
      </div>

      <div className="scene-meta">
        <div>Promotion: {promotionGate?.passed === true ? "GO" : "HOLD"}</div>
      </div>
    </div>
  );
}
