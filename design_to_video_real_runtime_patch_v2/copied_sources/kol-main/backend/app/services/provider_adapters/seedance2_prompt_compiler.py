from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Seedance2PromptContract:
    subject: str
    motion: str = ""
    environment: str = ""
    aesthetics: str = ""
    camera: str = ""
    audio: str = ""
    negative_prompt: str = ""
    references: dict[str, Any] = field(default_factory=dict)


class Seedance2PromptCompiler:
    version = "seedance2_prompt_compiler_v1"

    def compile(self, contract: Seedance2PromptContract | dict[str, Any]) -> dict[str, Any]:
        if isinstance(contract, dict):
            contract = Seedance2PromptContract(**contract)
        parts = [
            f"Subject: {contract.subject}" if contract.subject else "",
            f"Motion: {contract.motion}" if contract.motion else "",
            f"Environment: {contract.environment}" if contract.environment else "",
            f"Aesthetics: {contract.aesthetics}" if contract.aesthetics else "",
            f"Camera: {contract.camera}" if contract.camera else "",
            f"Audio: {contract.audio}" if contract.audio else "",
        ]
        final_prompt = "\n".join([p for p in parts if p]).strip()
        reference_map = self._compile_reference_map(contract.references)
        return {
            "compiler_version": self.version,
            "final_prompt": final_prompt,
            "negative_prompt": contract.negative_prompt,
            "reference_map": reference_map,
        }

    def _compile_reference_map(self, references: dict[str, Any]) -> dict[str, Any]:
        return {
            "images": references.get("images", []),
            "videos": references.get("videos", []),
            "audio": references.get("audio", []),
            "usage": references.get("usage", {
                "image": "character/product/style reference",
                "video": "camera/action/motion reference",
                "audio": "beat/voice/sound reference",
            }),
        }
