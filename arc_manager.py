"""Story arc management for campaigns."""

from __future__ import annotations

from typing import Any, Dict

from .campaign_manager import CampaignManager
from .world_memory import WorldMemoryManager

DEFAULT_VILLAIN = {
    "type": "villain",
    "name": "The Shadow Lord",
    "description": "A mysterious foe seeking dominion over the realm.",
    "tags": ["arc"],
}


class ArcManager:
    """Manage campaign-level story arcs and villains."""

    def __init__(self, campaign_name: str) -> None:
        self.campaign_name = campaign_name
        self.campaign = CampaignManager(campaign_name)
        self.dm_memory = WorldMemoryManager(campaign_name, hidden=True)
        self.villain_id = self._ensure_villain()

    # --------------------------------------------------------------
    # Villain helpers
    # --------------------------------------------------------------
    def _ensure_villain(self) -> str:
        """Return the existing villain ID or create a default villain."""
        villains = self.dm_memory.search_memory("", type_filter="villain")
        if villains:
            return villains[0]["id"]
        return self.dm_memory.add_memory_entry(DEFAULT_VILLAIN)

    def get_villain(self) -> Dict[str, Any]:
        """Return the current villain entry."""
        results = self.dm_memory.search_memory("", type_filter="villain")
        return results[0] if results else {}

    def progress_villain(self, description: str) -> str:
        """Record the villain's latest move in the DM event log."""
        self.campaign.log_event(description, hidden=True)
        villain = self.get_villain()
        if villain:
            self.dm_memory.update_memory_entry(villain["id"], {"description": description})
        return description
