import json
from pathlib import Path
import sys
import BlackFeather.campaign_manager as campaign_manager
sys.modules.setdefault("campaign_manager", campaign_manager)
import BlackFeather.world_memory as world_memory
sys.modules.setdefault("world_memory", world_memory)
import BlackFeather.arc_manager as arc_module
sys.modules.setdefault("arc_manager", arc_module)
from BlackFeather.arc_manager import ArcManager


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(world_memory, "CAMPAIGNS_DIR", tmp_path)
    real_am = arc_module.ArcManager
    monkeypatch.setattr(arc_module, "ArcManager", lambda *a, **k: None)
    try:
        instance = real_am("ArcTest")
    finally:
        monkeypatch.setattr(arc_module, "ArcManager", real_am)
    return instance


def test_arc_manager_creates_villain(tmp_path, monkeypatch):
    am = _setup(tmp_path, monkeypatch)
    dm_file = Path(tmp_path) / "ArcTest" / "world_memory_dm.json"
    data = json.loads(dm_file.read_text())
    assert len(data) == 1
    villain = next(iter(data.values()))
    assert villain["type"] == "villain"


def test_progress_villain_logs_event(tmp_path, monkeypatch):
    am = _setup(tmp_path, monkeypatch)
    am.progress_villain("steals the gem")
    dm_file = Path(tmp_path) / "ArcTest" / "world_memory_dm.json"
    data = json.loads(dm_file.read_text())
    villain = next(iter(data.values()))
    assert "steals the gem" in villain["description"]
    events = json.loads((Path(tmp_path) / "ArcTest" / "events_dm_log.json").read_text())
    assert any("steals the gem" in e["description"] for e in events.values())
