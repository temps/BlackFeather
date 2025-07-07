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
