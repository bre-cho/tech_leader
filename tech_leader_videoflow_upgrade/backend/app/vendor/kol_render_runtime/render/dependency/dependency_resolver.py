from __future__ import annotations

from typing import Any, Dict, List

from app.render.reassembly._sort_utils import scene_sort_key


class CyclicDependencyError(ValueError):
    def __init__(self, cycle: List[str]) -> None:
        self.cycle = list(cycle)
        super().__init__(f"Cyclic dependency detected: {' → '.join(self.cycle)}")


class DependencyResolver:
    """Builds a dependency edge list from a list of scene manifests.

    Rules applied (in order):

    1. **Timeline** — every scene creates a ``timeline`` edge to all later
       scenes, because a duration change in scene N shifts the presentation
       offset of scenes N+1 … end.
    2. **Avatar** — scenes sharing the same ``avatar_id`` have mutual
       ``avatar`` edges (bidirectional continuity requirement).
    3. **Style** — scenes sharing the same ``style_id`` have mutual ``style``
       edges.
    4. **Shared assets** — scenes that reference overlapping items in
       ``shared_assets`` have mutual ``shared_asset`` edges.
    """

    def build_from_manifests(
        self,
        manifests: List[Dict[str, Any]],
        *,
        check_cycles: bool = True,
    ) -> List[Dict[str, Any]]:
        """Build and return dependency edge dicts from *manifests*.

        Manifests are sorted by ``order_index`` / ``scene_index`` before
        processing so that timeline edges are constructed in the correct
        sequence.

        Args:
            manifests: List of scene manifest dicts.  Each dict must contain
                at minimum ``scene_id``.

        Returns:
            List of dependency dicts, each with keys ``source_scene_id``,
            ``target_scene_id``, ``dependency_type``, ``reason``, and
            ``strength``.
        """
        dependencies: List[Dict[str, Any]] = []

        sorted_manifests = sorted(manifests, key=scene_sort_key)

        for idx, scene in enumerate(sorted_manifests):
            scene_id: str = scene["scene_id"]

            # 1. Timeline dependency — each scene affects all later scenes.
            for later in sorted_manifests[idx + 1:]:
                dependencies.append({
                    "source_scene_id": scene_id,
                    "target_scene_id": later["scene_id"],
                    "dependency_type": "timeline",
                    "reason": "later scenes depend on previous scene duration",
                    "strength": 1.0,
                })

            # 2. Avatar continuity.
            avatar_id = scene.get("avatar_id")
            if avatar_id:
                for other in sorted_manifests:
                    if other["scene_id"] == scene_id:
                        continue
                    if other.get("avatar_id") == avatar_id:
                        dependencies.append({
                            "source_scene_id": scene_id,
                            "target_scene_id": other["scene_id"],
                            "dependency_type": "avatar",
                            "reason": f"shared avatar_id={avatar_id}",
                            "strength": 0.8,
                        })

            # 3. Style continuity.
            style_id = scene.get("style_id")
            if style_id:
                for other in sorted_manifests:
                    if other["scene_id"] == scene_id:
                        continue
                    if other.get("style_id") == style_id:
                        dependencies.append({
                            "source_scene_id": scene_id,
                            "target_scene_id": other["scene_id"],
                            "dependency_type": "style",
                            "reason": f"shared style_id={style_id}",
                            "strength": 0.6,
                        })

            # 4. Shared assets.
            assets = set(scene.get("shared_assets") or [])
            if assets:
                for other in sorted_manifests:
                    if other["scene_id"] == scene_id:
                        continue
                    overlap = assets.intersection(set(other.get("shared_assets") or []))
                    if overlap:
                        dependencies.append({
                            "source_scene_id": scene_id,
                            "target_scene_id": other["scene_id"],
                            "dependency_type": "shared_asset",
                            "reason": f"shared assets: {sorted(overlap)}",
                            "strength": 0.7,
                        })

        if check_cycles:
            cycle = self.detect_cycles(dependencies)
            if cycle is not None:
                raise CyclicDependencyError(cycle)
        return dependencies

    def detect_cycles(self, dependencies: List[Dict[str, Any]]) -> List[str] | None:
        adjacency: dict[str, set[str]] = {}
        for dep in dependencies or []:
            source = str(dep.get("source_scene_id") or "").strip()
            target = str(dep.get("target_scene_id") or "").strip()
            if not source or not target:
                continue
            adjacency.setdefault(source, set()).add(target)
            adjacency.setdefault(target, set())

        visited: set[str] = set()
        in_stack: set[str] = set()
        path: list[str] = []

        def _dfs(node: str) -> List[str] | None:
            visited.add(node)
            in_stack.add(node)
            path.append(node)

            for nxt in adjacency.get(node, set()):
                if nxt not in visited:
                    cycle = _dfs(nxt)
                    if cycle is not None:
                        return cycle
                elif nxt in in_stack:
                    idx = path.index(nxt)
                    return path[idx:] + [nxt]

            in_stack.remove(node)
            path.pop()
            return None

        for node in list(adjacency.keys()):
            if node in visited:
                continue
            cycle = _dfs(node)
            if cycle is not None:
                return cycle
        return None
