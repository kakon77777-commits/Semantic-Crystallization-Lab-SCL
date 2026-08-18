from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class CognitionState:
    agent: str
    independent_package: dict
    active_package: dict
    version: int = 1
    accepted_hashes: list[str] = field(default_factory=list)
    superseded_hashes: list[str] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)

    def history_digest(self) -> str:
        payload = json.dumps(self.history, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def restart_cognition(state: CognitionState, *, persistent: bool) -> CognitionState:
    if persistent:
        return copy.deepcopy(state)
    independent = copy.deepcopy(state.independent_package)
    return CognitionState(
        agent=state.agent,
        independent_package=independent,
        active_package=copy.deepcopy(independent),
        version=1,
        accepted_hashes=[independent["sha256"]],
        superseded_hashes=[],
        history=[],
    )
