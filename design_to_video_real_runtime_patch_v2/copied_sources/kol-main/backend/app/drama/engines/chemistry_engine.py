from __future__ import annotations

from typing import Any, Dict, List


class ChemistryEngine:
    """Optional lightweight chemistry estimator used during recompute passes."""

    def score(self, relationship_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        trust = float(relationship_snapshot.get("trust_level", 0.0) or 0.0)
        attraction = float(relationship_snapshot.get("attraction_level", 0.0) or 0.0)
        fear = float(relationship_snapshot.get("fear_level", 0.0) or 0.0)

        affinity = max(0.0, min(1.0, 0.6 * trust + 0.4 * attraction - 0.25 * fear))
        volatility = max(0.0, min(1.0, abs(attraction - trust) + fear * 0.4))
        return {
            "affinity": round(affinity, 3),
            "volatility": round(volatility, 3),
        }

    def compute_all_pairs(
        self,
        characters: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        scene_context: Dict[str, Any] | None = None,  # noqa: ARG002 — reserved for future use
    ) -> List[Dict[str, Any]]:
        """Score chemistry for all relationship edges in the scene.

        Calls :meth:`score` for every entry in *relationships* and augments
        the result with ``source_character_id`` and ``target_character_id``
        keys so callers can map results back to directed pairs.

        Parameters
        ----------
        characters:
            List of character dicts (unused directly; reserved for future
            pair-synthesis when no explicit edge exists).
        relationships:
            List of relationship edge dicts.  Each dict is passed to
            :meth:`score`; the keys ``source_character_id`` and
            ``target_character_id`` are preserved in the output.
        scene_context:
            Optional scene context (reserved for future model-based scoring).

        Returns
        -------
        list of dict
            Each element contains ``affinity``, ``volatility``, plus
            ``source_character_id`` and ``target_character_id`` from the
            original edge.
        """
        results: List[Dict[str, Any]] = []
        for rel in relationships:
            chemistry = self.score(rel)
            chemistry["source_character_id"] = rel.get("source_character_id", "")
            chemistry["target_character_id"] = rel.get("target_character_id", "")
            results.append(chemistry)
        return results
