"""Records player actions so play sessions can be analysed for CT skills.

Each event is a flat JSON-friendly dict: when it happened, which puzzle,
what kind of action, plus action-specific data.
"""
import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable


class Telemetry:
    def __init__(self, session_id: str | None = None, clock: Callable[[], float] = time.time):
        self.session_id = session_id or uuid.uuid4().hex[:8]
        self.events: list[dict[str, Any]] = []
        self._clock = clock

    def log(self, puzzle: str, action: str, **data: Any) -> None:
        self.events.append({"t": self._clock(), "puzzle": puzzle, "action": action, **data})

    def save(self, directory: Path | str = "telemetry") -> Path | None:
        """Write the session to <directory>/session-<id>.json. Skips empty sessions."""
        if not self.events:
            return None
        path = Path(directory) / f"session-{self.session_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"session": self.session_id, "events": self.events}, indent=2))
        return path
