"""Player journal management for tracking campaign details."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

from campaign_manager import CAMPAIGNS_DIR


class JournalManager:
    """Maintain a persistent journal for a player within a campaign."""

    def __init__(self, campaign_name: str, character_name: str) -> None:
        """Create a journal for ``character_name`` in ``campaign_name``."""

        safe_campaign = campaign_name.lower().replace(" ", "_")
        safe_name = character_name.lower().replace(" ", "_")

        self.campaign_name = campaign_name
        self.character_name = character_name
        self.dir = os.path.join(CAMPAIGNS_DIR, safe_campaign, "players")
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, f"{safe_name}_journal.json")
        if not os.path.exists(self.path):
            self._save(
                {
                    "inventory": [],
                    "gold": 0,
                    "experience": 0,
                    "npcs": [],
                    "quests": [],
                    "events": [],
                    "images": [],
                }
            )

    def _load(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)

    # ------------------------------------------------------------------
    # Entry helpers
    # ------------------------------------------------------------------
    def add_item(self, item: str) -> None:
        """Append ``item`` to the character's inventory."""
        data = self._load()
        data.setdefault("inventory", []).append(item)
        self._save(data)

    def remove_item(self, item: str) -> None:
        """Remove ``item`` from the inventory if present."""
        data = self._load()
        items = data.setdefault("inventory", [])
        if item in items:
            items.remove(item)
            self._save(data)

    def update_gold(self, delta: int) -> None:
        """Change gold by ``delta`` and clamp the total to zero or more.

        Negative amounts that would result in a negative balance leave the
        total at zero.
        """
        data = self._load()
        data["gold"] = max(data.get("gold", 0) + int(delta), 0)
        self._save(data)

    def add_gold(self, amount: int) -> None:
        """Increase gold by ``amount``."""
        self.update_gold(int(amount))

    def remove_gold(self, amount: int) -> None:
        """Decrease gold by ``amount``.

        The total gold is clamped at zero by :py:meth:`update_gold`.
        """
        self.update_gold(-int(amount))

    def update_experience(self, delta: int) -> None:
        """Change experience points by ``delta``."""
        data = self._load()
        data["experience"] = data.get("experience", 0) + int(delta)
        self._save(data)

    def add_experience(self, amount: int) -> None:
        """Increase experience by ``amount``."""
        self.update_experience(int(amount))

    def remove_experience(self, amount: int) -> None:
        """Decrease experience by ``amount``."""
        self.update_experience(-int(amount))

    def add_npc(self, name: str) -> None:
        """Record that ``name`` was encountered."""
        data = self._load()
        npcs: List[str] = data.setdefault("npcs", [])
        if name not in npcs:
            npcs.append(name)
            self._save(data)

    def add_quest(self, name: str) -> None:
        """Add a quest title to the journal."""
        data = self._load()
        quests: List[str] = data.setdefault("quests", [])
        if name not in quests:
            quests.append(name)
            self._save(data)

    def remove_quest(self, name: str) -> None:
        """Remove ``name`` from the quest list if present."""
        data = self._load()
        quests: List[str] = data.setdefault("quests", [])
        if name in quests:
            quests.remove(name)
            self._save(data)

    def add_event(self, description: str, title: str | None = None) -> None:
        """Log a timestamped event with optional ``title``."""
        data = self._load()
        events: List[Dict[str, Any]] = data.setdefault("events", [])
        events.append(
            {
                "title": title or "",
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self._save(data)

    def add_image(self, image: str) -> None:
        """Track an image reference requested by the player."""
        data = self._load()
        images: List[str] = data.setdefault("images", [])
        images.append(image)
        self._save(data)

    def get_journal(self) -> Dict[str, Any]:
        """Return the full journal data."""
        return self._load()
