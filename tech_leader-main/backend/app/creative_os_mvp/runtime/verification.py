class VerificationEngine:
    def verify(self, reasoning, artifacts: list, prompt: str) -> dict:
        checks={
            "commercial_reasoning_present": reasoning is not None and reasoning.total_score > 0,
            "artifact_contract_present": bool(artifacts) and all(a.size_bytes > 0 and a.checksum_sha256 for a in artifacts),
            "prompt_contains_product_logic": "Product hero" in prompt and "Typography" in prompt,
            "attention_route_present": bool(reasoning.attention_route),
        }
        passed=all(checks.values())
        return {"passed": passed, "checks": checks, "score": reasoning.total_score if reasoning else 0}

class PromotionGate:
    def evaluate(self, verification: dict, reasoning) -> dict:
        if not verification["passed"]:
            return {"approved": False, "reason":"verification failed", "checks": verification["checks"]}
        if reasoning.total_score < 78:
            return {"approved": False, "reason":"commercial score below threshold", "score": reasoning.total_score}
        return {"approved": True, "reason":"approved for memory/winner DNA", "score": reasoning.total_score}
