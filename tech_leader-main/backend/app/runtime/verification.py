from typing import Dict, Any
from app.governance.operating_law import OperatingLawEnforcer

class VerificationEngine:
    def __init__(self):
        self.law_enforcer = OperatingLawEnforcer()

    def verify(self, context: Dict[str, Any], reasoning: Dict[str, Any] | None = None, artifact: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Support both old and new signatures for backward compatibility
        if reasoning is None:
            reasoning = {"commercial_reasoning_score": 85}
        if artifact is None:
            artifact = context.get("artifact") if isinstance(context, dict) else None
        artifact = artifact or {}

        # Handle both old (trace with completed_steps) and new (context with trace dict) signatures
        if "completed_steps" in context and "trace" not in context:
            # Old signature: context is actually the trace with completed_steps
            trace_dict = context
            # Convert completed_steps list to individual keys for validate_trace
            trace = {
                "target_define": "TARGET_DEFINE" in trace_dict.get("completed_steps", []),
                "research": "RESEARCH" in trace_dict.get("completed_steps", []),
                "plan": "PLAN" in trace_dict.get("completed_steps", []),
                "execute": "EXECUTE" in trace_dict.get("completed_steps", []),
                "verify": "VERIFY" in trace_dict.get("completed_steps", []),
                "distill_to_skill": "DISTILL_TO_SKILL" in trace_dict.get("completed_steps", []),
                "memory_update": "MEMORY_UPDATE" in trace_dict.get("completed_steps", []),
                "winner_dna_update": "WINNER_DNA_UPDATE" in trace_dict.get("completed_steps", []),
            }
        else:
            # New signature: context has "trace" key with individual boolean keys
            trace = context.get("trace", {})

        law = self.law_enforcer.validate_trace(trace)
        artifact_id = str(artifact.get("artifact_id") or "")
        checksum = str(artifact.get("checksum") or "")
        artifact_is_valid = bool(artifact_id and not artifact_id.startswith("mock_") and checksum and not checksum.startswith("mock_"))
        checks = {
            "operating_law": law.passed,
            "commercial_reasoning_score": reasoning.get("commercial_reasoning_score", 85) >= 80,
            "artifact_contract": artifact_is_valid,
            "provider_status_valid": artifact.get("status") in ["succeeded", "ready_to_call"],
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "law": {
                "passed": law.passed,
                "missing_steps": law.missing_steps,
                "status": law.status,
                "reason": law.message
            },
            "score": reasoning.get("commercial_reasoning_score", 85)
        }

class PromotionGate:
    def evaluate(self, verification: Dict[str, Any]) -> Dict[str, Any]:
        if verification["passed"] and verification["score"] >= 85:
            return {"status": "PROMOTED", "reason": "Commercial score and operating law passed"}
        if verification["passed"]:
            return {"status": "CANDIDATE", "reason": "Passed but score below winner threshold"}
        return {"status": "BLOCKED", "reason": "Verification failed", "checks": verification["checks"]}
