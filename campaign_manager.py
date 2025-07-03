"""Campaign management module for a TTRPG chatbot engine."""

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List


def deep_update(orig: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively update ``orig`` with values from ``new``."""
    for key, value in new.items():
        if (
            isinstance(value, dict)
            and isinstance(orig.get(key), dict)
        ):
            deep_update(orig[key], value)
        else:
            orig[key] = value
    return orig

# Base directories
PLAYERS_DIR = os.path.join(os.getcwd(), "players")
CAMPAIGNS_DIR = os.path.join(os.getcwd(), "campaigns")

# Campaign data schema versioning
VERSION = 1


@dataclass
class PlayerCharacter:
    name: str
    race: str
    character_class: str
    level: int = 1
    background: str = ""
    attributes: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PlayerManager:
    """Manage player character creation and storage."""

    @staticmethod
    def _player_file(name: str) -> str:
        filename = f"{name.lower().replace(' ', '_')}.json"
        return os.path.join(PLAYERS_DIR, filename)

    def create_character(self) -> PlayerCharacter:
        """Prompt user for character details and save the character."""
        os.makedirs(PLAYERS_DIR, exist_ok=True)
        name = input("Character name: ")
        race = input("Race: ")
        char_class = input("Class: ")
        level = int(input("Level [1]: ") or 1)
        background = input("Background: ")
        attributes = {}
        while True:
            attr_name = input("Add attribute (or leave blank to finish): ")
            if not attr_name:
                break
            attr_value = input(f"Value for {attr_name}: ")
            try:
                attr_value = int(attr_value)
            except ValueError:
                pass
            attributes[attr_name] = attr_value

        pc = PlayerCharacter(
            name=name,
            race=race,
            character_class=char_class,
            level=level,
            background=background,
            attributes=attributes,
        )
        with open(self._player_file(name), "w", encoding="utf-8") as f:
            json.dump(pc.to_dict(), f, indent=2)
        return pc

    def load_character(self, name: str) -> PlayerCharacter | None:
        path = self._player_file(name)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PlayerCharacter(**data)


class CampaignManager:
    """Manage campaign world state."""

    DEFAULT_FILES = [
        "npcs.json",
        "quests.json",
        "items.json",
        "events_log.json",
        "world_state.json",
    ]

    def __init__(self, name: str):
        self.name = name
        self.path = os.path.join(CAMPAIGNS_DIR, name)
        os.makedirs(self.path, exist_ok=True)
        # ensure versioning file
        version_file = os.path.join(self.path, "version.json")
        if not os.path.exists(version_file):
            with open(version_file, "w", encoding="utf-8") as fp:
                json.dump({"version": VERSION}, fp, indent=2)

        # create default data files
        for f in self.DEFAULT_FILES:
            file_path = os.path.join(self.path, f)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as fp:
                    if f == "quests.json":
                        json.dump({"active": {}, "completed": {}, "missed": {}}, fp, indent=2)
                    else:
                        json.dump({}, fp, indent=2)

        # ensure players directory inside each campaign
        os.makedirs(os.path.join(self.path, "players"), exist_ok=True)

    def _load_json(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.path, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_json(self, filename: str, data: Dict[str, Any]):
        path = os.path.join(self.path, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------
    # Player state management
    # ------------------------------------------------------
    def _player_state_file(self, player_name: str) -> str:
        """Return path to a player's dynamic state file."""
        filename = f"{player_name.lower().replace(' ', '_')}.json"
        return os.path.join(self.path, "players", filename)

    def initialize_player_state(self, player_name: str) -> None:
        """Create a default player state file if it doesn't exist."""
        file_path = self._player_state_file(player_name)
        if not os.path.exists(file_path):
            default_state = {"gold": 0, "inventory": [], "quests": []}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_state, f, indent=2)

    def update_player_state(self, player_name: str, updates: Dict[str, Any]):
        """Update dynamic player state with provided values."""
        self.initialize_player_state(player_name)
        file_path = self._player_state_file(player_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        deep_update(data, updates)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------
    # Quest management helpers
    # ------------------------------------------------------
    def _load_quests(self) -> Dict[str, Dict[str, Any]]:
        quests = self._load_json("quests.json")
        if not all(k in quests for k in ("active", "completed", "missed")):
            quests = {"active": {}, "completed": {}, "missed": {}}
        return quests

    def _save_quests(self, quests: Dict[str, Dict[str, Any]]):
        self._save_json("quests.json", quests)

    def add_npc(self, npc_data: Dict[str, Any]) -> str:
        """Add a new NPC to the campaign.

        ``npc_data`` may optionally include a ``relationships`` mapping. Example::

            {
                "name": "Ari", "race": "elf",
                "relationships": {
                    "Damian": {"trust": 80, "notes": "He defended her honor."}
                }
            }
        """
        npcs = self._load_json("npcs.json")
        npc_id = str(uuid.uuid4())
        npc_data.setdefault("timestamp", datetime.utcnow().isoformat())
        npcs[npc_id] = npc_data
        self._save_json("npcs.json", npcs)
        return npc_id

    def update_npc(self, npc_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing NPC entry using deep merging."""
        npcs = self._load_json("npcs.json")
        if npc_id not in npcs:
            return False
        deep_update(npcs[npc_id], updates)
        self._save_json("npcs.json", npcs)
        return True

    def add_quest(self, quest_data: Dict[str, Any]) -> str:
        quests = self._load_quests()
        quest_id = str(uuid.uuid4())
        quest_data["timestamp"] = datetime.utcnow().isoformat()
        quests["active"][quest_id] = quest_data
        self._save_quests(quests)
        return quest_id

    def complete_quest(self, quest_id: str, player_name: str | None = None) -> bool:
        """Move quest from active or missed to completed.

        If ``player_name`` is given, append the completion info to that
        player's state. This can later be expanded for richer tracking.
        """
        quests = self._load_quests()
        for status in ("active", "missed"):
            if quest_id in quests.get(status, {}):
                quests["completed"][quest_id] = quests[status].pop(quest_id)
                self._save_quests(quests)
                if player_name:
                    # append quest result to player's history
                    path = self._player_state_file(player_name)
                    self.initialize_player_state(player_name)
                    with open(path, "r", encoding="utf-8") as f:
                        state = json.load(f)
                    state.setdefault("quests", [])
                    state["quests"].append(
                        {
                            "id": quest_id,
                            "status": "completed",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=2)
                return True
        return False

    def miss_quest(self, quest_id: str) -> bool:
        """Move quest from active to missed."""
        quests = self._load_quests()
        if quest_id in quests.get("active", {}):
            quests["missed"][quest_id] = quests["active"].pop(quest_id)
            self._save_quests(quests)
            return True
        return False

    def log_event(self, event: str):
        events = self._load_json("events_log.json")
        event_id = str(uuid.uuid4())
        events[event_id] = {
            "description": event,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._save_json("events_log.json", events)
        return event_id

    def update_world_state(self, updates: Dict[str, Any]):
        state = self._load_json("world_state.json")
        state.update(updates)
        self._save_json("world_state.json", state)

    def add_item(self, item_data: Dict[str, Any]) -> str:
        items = self._load_json("items.json")
        item_id = str(uuid.uuid4())
        item_data["timestamp"] = datetime.utcnow().isoformat()
        items[item_id] = item_data
        self._save_json("items.json", items)
        return item_id

    def search_npcs(self, query: str) -> List[Dict[str, Any]]:
        npcs = self._load_json("npcs.json")
        return [v for v in npcs.values() if query.lower() in str(v).lower()]

    def search_items(self, query: str) -> List[Dict[str, Any]]:
        items = self._load_json("items.json")
        return [v for v in items.values() if query.lower() in str(v).lower()]

    def search_events(self, query: str) -> List[Dict[str, Any]]:
        """Return events containing the query string."""
        events = self._load_json("events_log.json")
        return [
            ev
            for ev in events.values()
            if query.lower() in str(ev.get("description", "")).lower()
        ]


# Placeholder for future web search capability

def search_web(query: str) -> str:
    """Placeholder for future web search implementation."""
    return ""
