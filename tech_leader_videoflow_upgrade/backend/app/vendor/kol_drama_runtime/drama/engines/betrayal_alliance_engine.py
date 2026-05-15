from __future__ import annotations

import os
from typing import Any, Dict, List


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


class BetrayalAllianceEngine:
    """Simple directional relationship mutation for betrayal/alliance events.

    Deltas are tunable via environment variables so operations teams can adjust
    dramatic sensitivity without a code deploy:

    ==========================================  =============  ========
    Env var                                     Default        Effect
    ==========================================  =============  ========
    ``BETRAYAL_TRUST_DELTA``                    ``-0.25``      Trust shift on betrayal outcome
    ``BETRAYAL_RESENTMENT_DELTA``               ``0.30``       Resentment shift on betrayal
    ``RESCUE_TRUST_DELTA``                      ``0.20``       Trust shift on rescue/reassurance
    ``RESCUE_RESENTMENT_DELTA``                 ``-0.10``      Resentment shift on rescue
    ==========================================  =============  ========
    """

    def apply(self, relationship_snapshot: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(relationship_snapshot or {})
        outcome_type = (outcome.get("outcome_type") or "").lower()

        trust = float(updated.get("trust_level", 0.0) or 0.0)
        resentment = float(updated.get("resentment_level", 0.0) or 0.0)

        if outcome_type == "betrayal":
            trust = max(0.0, trust + _env_float("BETRAYAL_TRUST_DELTA", -0.25))
            resentment = min(1.0, resentment + _env_float("BETRAYAL_RESENTMENT_DELTA", 0.30))
        elif outcome_type in {"rescue", "reassurance"}:
            trust = min(1.0, trust + _env_float("RESCUE_TRUST_DELTA", 0.20))
            resentment = max(0.0, resentment + _env_float("RESCUE_RESENTMENT_DELTA", -0.10))
        elif outcome_type in {"forgiveness", "reconciliation"}:
            trust = min(1.0, trust + _env_float("FORGIVENESS_TRUST_DELTA", 0.15))
            resentment = max(0.0, resentment + _env_float("FORGIVENESS_RESENTMENT_DELTA", -0.20))
        elif outcome_type in {"catharsis", "resolution"}:
            trust = min(1.0, trust + _env_float("CATHARSIS_TRUST_DELTA", 0.10))
            resentment = max(0.0, resentment + _env_float("CATHARSIS_RESENTMENT_DELTA", -0.15))

        updated["trust_level"] = trust
        updated["resentment_level"] = resentment
        return updated

    def evaluate_all_pairs(
        self,
        characters: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        scene_context: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Evaluate betrayal/alliance state for all unique character pairs.

        Iterates over all ordered (source → target) relationship edges and
        applies :meth:`apply` with any matching outcome from *scene_context*,
        returning a list of updated relationship snapshots.

        Parameters
        ----------
        characters:
            List of character dicts (keys: ``id`` or ``avatar_id`` or ``name``).
        relationships:
            List of relationship edge dicts (keys: ``source_character_id``,
            ``target_character_id``, plus trust/resentment fields consumed by
            :meth:`apply`).
        scene_context:
            Optional current scene context.  If it contains an ``"outcome"``
            key, that dict is forwarded to :meth:`apply` for each pair.

        Returns
        -------
        list of dict
            Each element is the updated relationship snapshot returned by
            :meth:`apply`, with ``source_character_id`` and
            ``target_character_id`` keys preserved.
        """
        outcome = (scene_context or {}).get("outcome") or {}
        results: List[Dict[str, Any]] = []
        for rel in relationships:
            src = rel.get("source_character_id", "")
            tgt = rel.get("target_character_id", "")
            if not src or not tgt:
                continue
            updated = self.apply(dict(rel), outcome)
            updated.setdefault("source_character_id", src)
            updated.setdefault("target_character_id", tgt)
            results.append(updated)
        return results
