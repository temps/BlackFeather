"""World memory management for a TTRPG campaign engine."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Allowed entity types for validation
# ``villain`` and ``plot`` are used internally for DM information.
ALLOWED_TYPES = [
    "city",
    "faction",
    "business",
    "monster",
    "event",
    "villain",
    "plot",
]

from .campaign_manager import CAMPAIGNS_DIR, deep_update


class WorldMemoryManager:
    """Handle persistent world memory for a specific campaign."""

    def __init__(self, campaign_name: str, hidden: bool = False) -> None:
        self.campaign_name = campaign_name
        self.hidden = hidden
        self.path = os.path.join(CAMPAIGNS_DIR, campaign_name)
        os.makedirs(self.path, exist_ok=True)
        filename = "world_memory_dm.json" if hidden else "world_memory.json"
        self.file_path = os.path.join(self.path, filename)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def _load(self) -> Dict[str, Any]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_memory_entry(self, entry: Dict[str, Any]) -> str:
        """Add a new memory entry and return its ID."""
        data = self._load()

        required = ["type", "name"]
        if any(not entry.get(k) for k in required):
            raise ValueError("Missing required fields: type and name")

        if entry["type"] not in ALLOWED_TYPES:
            raise ValueError(f"Invalid type: {entry['type']}")

        entry_id = str(uuid.uuid4())
        entry_obj = {
            "id": entry_id,
            "type": entry.get("type", ""),
            "name": entry.get("name", ""),
            "description": entry.get("description", ""),
            "tags": entry.get("tags", []),
            "related_to": entry.get("related_to", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        data[entry_id] = entry_obj
        self._save(data)
        return entry_id

    def search_memory(self, query: str, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search memory entries by keyword and optional type."""
        data = self._load()
        results: List[Dict[str, Any]] = []
        for entry in data.values():
            if type_filter and entry.get("type") != type_filter:
                continue
            haystack = json.dumps(entry).lower()
            if query.lower() in haystack:
                results.append(entry)
        return results

    def update_memory_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory entry using deep merging."""
        data = self._load()
        if entry_id not in data:
            return False
        deep_update(data[entry_id], updates)
        self._save(data)
        return True

    def link_entities(self, entry_id: str, related_id: str, bidirectional: bool = False) -> bool:
        """Link two memory entities by ID."""
        data = self._load()
        if entry_id not in data or related_id not in data:
            return False
        related = data[entry_id].setdefault("related_to", [])
        if related_id not in related:
            related.append(related_id)
        if bidirectional:
            back = data[related_id].setdefault("related_to", [])
            if entry_id not in back:
                back.append(entry_id)
        self._save(data)
        return True
