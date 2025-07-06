import json
import journal_manager
import campaign_manager

import pytest


@pytest.fixture()
def jm(tmp_path, monkeypatch):
    camp_dir = tmp_path / "campaigns"
    monkeypatch.setattr(campaign_manager, "CAMPAIGNS_DIR", str(camp_dir), raising=False)
    monkeypatch.setattr(journal_manager, "CAMPAIGNS_DIR", str(camp_dir), raising=False)
    return journal_manager.JournalManager("test", "Alice")


def load_journal(jm):
    with open(jm.path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_inventory_updates(jm):
    jm.add_item("Sword")
    data = load_journal(jm)
    assert "Sword" in data.get("inventory", [])

    jm.remove_item("Sword")
    data = load_journal(jm)
    assert "Sword" not in data.get("inventory", [])


def test_gold_never_negative(jm):
    jm.add_gold(10)
    data = load_journal(jm)
    assert data["gold"] == 10

    jm.remove_gold(15)
    data = load_journal(jm)
    assert data["gold"] == 0

    jm.update_gold(-5)
    data = load_journal(jm)
    assert data["gold"] == 0
