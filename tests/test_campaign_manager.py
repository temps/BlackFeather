import json
from pathlib import Path
import sys
import pytest
import BlackFeather.campaign_manager as campaign_manager
import BlackFeather.arc_manager as arc_manager

sys.modules.setdefault("campaign_manager", campaign_manager)
sys.modules.setdefault("arc_manager", arc_manager)


def _setup_campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", tmp_path)
    monkeypatch.setattr(campaign_manager, "PLAYERS_DIR", tmp_path / "players")
    monkeypatch.setattr(arc_manager, "ArcManager", lambda *a, **k: None)
    return campaign_manager.CampaignManager("TestCampaign")


def test_init_creates_default_files(tmp_path, monkeypatch):
    cm = _setup_campaign(tmp_path, monkeypatch)
    campaign_path = Path(tmp_path) / "TestCampaign"
    expected = ["version.json"] + campaign_manager.CampaignManager.DEFAULT_FILES
    for name in expected:
        assert (campaign_path / name).exists()
    assert (campaign_path / "players").is_dir()


def test_add_quest_unique_title(tmp_path, monkeypatch):
    cm = _setup_campaign(tmp_path, monkeypatch)
    cm.add_quest({"title": "Find Sword"})
    with pytest.raises(ValueError):
        cm.add_quest({"title": "Find Sword"})


def test_complete_quest_updates_player(tmp_path, monkeypatch):
    cm = _setup_campaign(tmp_path, monkeypatch)
    qid = cm.add_quest({"title": "Retrieve Gem"})
    assert cm.complete_quest(qid, player_name="Alice") is True
    quests = json.loads((Path(tmp_path) / "TestCampaign" / "quests.json").read_text())
    assert qid in quests["completed"]
    state_file = Path(tmp_path) / "TestCampaign" / "players" / "alice.json"
    data = json.loads(state_file.read_text())
    assert any(q["id"] == qid and q["status"] == "completed" for q in data["quests"])
