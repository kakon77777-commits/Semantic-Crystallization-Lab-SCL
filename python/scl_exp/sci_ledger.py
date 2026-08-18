from __future__ import annotations

import hashlib
import json


ALLOWED_EVENT_TYPES = {
    "imprint.proposal",
    "imprint.objection",
    "imprint.correction",
    "imprint.merge",
    "imprint.transfer",
    "imprint.contamination",
}


def _digest(value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class SciLedger:
    def __init__(self, *, topic: str) -> None:
        self.topic = topic
        self.events: list[dict] = []

    def append(self, event_type: str, agent: str, payload: dict) -> dict:
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"unsupported SCI event type: {event_type}")
        seq = len(self.events) + 1
        base = {
            "schema": "sci-board-ledger/v0.1",
            "event_id": f"SCI-{seq:06d}",
            "sequence": seq,
            "logical_instant": f"I*-{seq:06d}",
            "ctcl_mode": "ctcl-compatible-logical-not-verified",
            "topic": self.topic,
            "event_type": event_type,
            "agent": agent,
            "prev_sha256": self.events[-1]["sha256"] if self.events else None,
            "payload": payload,
        }
        event = dict(base)
        event["sha256"] = _digest(base)
        self.events.append(event)
        return event
