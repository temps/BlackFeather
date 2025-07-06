import json
from pathlib import Path

import sys
import BlackFeather.campaign_manager as campaign_manager
sys.modules.setdefault("campaign_manager", campaign_manager)
import BlackFeather.journal_manager as journal_manager
sys.modules.setdefault("journal_manager", journal_manager)
from BlackFeather.journal_manager import JournalManager


def test_journal_manager_basic(tmp_path, monkeypatch):
    monkeypatch.setattr(journal_manager, "CAMPAIGNS_DIR", tmp_path)
    jm = JournalManager("Summer Campaign", "Lia")
    journal_path = Path(tmp_path) / "summer_campaign" / "players" / "lia_journal.json"
    assert journal_path.exists()

    jm.add_item("Sword")
    jm.add_gold(30)
    jm.remove_gold(10)
    jm.add_event("Met NPC", title="Intro")

    data = jm.get_journal()
    assert data["gold"] == 20
    assert "Sword" in data["inventory"]
    assert data["events"][0]["title"] == "Intro"

    jm.remove_item("Sword")
    assert "Sword" not in jm.get_journal()["inventory"]

    jm.remove_gold(999)
    assert jm.get_journal()["gold"] == 0
