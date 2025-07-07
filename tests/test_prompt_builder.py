from BlackFeather import prompt_builder as pb


def test_summarize_player_basic():
    summary = pb.summarize_player({"name": "Lia", "race": "elf", "character_class": "wizard", "level": 3})
    assert "Lia is a level 3 elf wizard" in summary


def test_build_prompt_sections():
    prompt = pb.build_prompt(
        "Lia",
        {"name": "Lia", "race": "elf", "character_class": "wizard", "level": 3},
        {"quests": {"active": {}, "completed": {}, "missed": {}}, "npcs": {}, "items": {}, "events": {}},
        [],
        ["Hello"],
        "What now?",
    )
    assert "### Player Info" in prompt
    assert "### Campaign" in prompt
    assert "Player: What now?" in prompt
