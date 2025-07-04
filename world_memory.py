"""Module for managing persistent TTRPG world memory entries."""

from __future__ import annotations

import json
import os
import uuid
from typing import Dict, Any


ALLOWED_TYPES = [
    "city",
    "faction",
    "business",
    "monster",
    "event",
]


class WorldMemory:
    """Manage persistent world memory stored in a JSON file."""

    def __init__(self, filepath: str = "world_memory.json") -> None:
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save({})

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_memory_entry(self, entry: Dict[str, Any]) -> str:
        """Add a new entry to the world memory.

        Parameters
        ----------
        entry: Dict[str, Any]
            Dictionary containing at least ``type`` and ``name`` keys.

        Returns
        -------
        str
            The identifier of the newly created entry.
        """
        required = ["type", "name"]
        if any(not entry.get(k) for k in required):
            raise ValueError("Missing required fields: type and name")

        if entry["type"] not in ALLOWED_TYPES:
            raise ValueError(f"Invalid type: {entry['type']}")

        data = self._load()
        entry_id = str(uuid.uuid4())
        data[entry_id] = entry
        self._save(data)
        return entry_id

    def get_entry(self, entry_id: str) -> Dict[str, Any] | None:
        data = self._load()
        return data.get(entry_id)

    def link_entities(
        self, entry_id: str, related_id: str, *, bidirectional: bool = False
    ) -> None:
        """Create a link between two entries.

        If ``bidirectional`` is True, the link is added in both directions
        provided both IDs exist in the data.
        """
        data = self._load()
        if entry_id not in data or related_id not in data:
            return
        related = data[entry_id].setdefault("related_to", [])
        if related_id not in related:
            related.append(related_id)
        if bidirectional:
            other_related = data[related_id].setdefault("related_to", [])
            if entry_id not in other_related:
                other_related.append(entry_id)
        self._save(data)

    def remove_entry(self, entry_id: str) -> None:
        data = self._load()
        if entry_id in data:
            del data[entry_id]
            self._save(data)

    def all_entries(self) -> Dict[str, Any]:
        return self._load()
