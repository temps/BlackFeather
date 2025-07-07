import json
from pathlib import Path
import sys
import BlackFeather.campaign_manager as campaign_manager
sys.modules.setdefault("campaign_manager", campaign_manager)
import BlackFeather.world_memory as world_memory
sys.modules.setdefault("world_memory", world_memory)
from BlackFeather.world_memory import WorldMemoryManager


def test_hidden_memory(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(world_memory, "CAMPAIGNS_DIR", tmp_path)
    wm = WorldMemoryManager("Arc Test", hidden=True)
    dm_file = Path(tmp_path) / "Arc Test" / "world_memory_dm.json"
    assert dm_file.exists()

    entry_id = wm.add_memory_entry({"type": "villain", "name": "Zara"})
    data = json.loads(dm_file.read_text())
    assert entry_id in data


def test_add_entry_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(world_memory, "CAMPAIGNS_DIR", tmp_path)
    wm = WorldMemoryManager("Arc Test")
    file_path = Path(tmp_path) / "Arc Test" / "world_memory.json"

    entry = {
        "type": "city",
        "name": "Haven",
        "description": "Port city",
        "tags": ["port", "trade"],
    }
    entry_id = wm.add_memory_entry(entry)
    data = json.loads(file_path.read_text())

    assert entry_id in data
    stored = data[entry_id]
    assert stored["id"] == entry_id
    assert stored["type"] == entry["type"]
    assert stored["name"] == entry["name"]
    assert stored["description"] == entry["description"]
    assert stored["tags"] == entry["tags"]
    assert stored["related_to"] == []
    assert "timestamp" in stored


def test_search_memory_type_filter(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(world_memory, "CAMPAIGNS_DIR", tmp_path)
    wm = WorldMemoryManager("Arc Test")

    id_city = wm.add_memory_entry({"type": "city", "name": "Haven"})
    id_faction = wm.add_memory_entry({"type": "faction", "name": "Haven Guard"})

    all_results = wm.search_memory("haven")
    city_results = wm.search_memory("haven", type_filter="city")
    faction_results = wm.search_memory("haven", type_filter="faction")

    assert {r["id"] for r in all_results} == {id_city, id_faction}
    assert [r["id"] for r in city_results] == [id_city]
    assert [r["id"] for r in faction_results] == [id_faction]


def test_link_entities(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(world_memory, "CAMPAIGNS_DIR", tmp_path)
    wm = WorldMemoryManager("Arc Test")
    file_path = Path(tmp_path) / "Arc Test" / "world_memory.json"

    id_a = wm.add_memory_entry({"type": "city", "name": "Alpha"})
    id_b = wm.add_memory_entry({"type": "city", "name": "Beta"})

    assert wm.link_entities(id_a, id_b, bidirectional=True)

    data = json.loads(file_path.read_text())
    assert id_b in data[id_a]["related_to"]
    assert id_a in data[id_b]["related_to"]
