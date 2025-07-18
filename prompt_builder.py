"""Utilities to build conversation prompts for the TTRPG chatbot."""

from typing import Any, Dict, List


def summarize_player(player_data: Dict[str, Any]) -> str:
    """Return a short summary describing the player."""
    name = player_data.get("name", "Unknown")
    race = player_data.get("race", "unknown race")
    char_class = player_data.get("character_class", "adventurer")
    level = player_data.get("level", 1)
    background = player_data.get("background", "")
    platinum = player_data.get(
        "platinum", player_data.get("state", {}).get("platinum", 0)
    )
    gold = player_data.get("gold", player_data.get("state", {}).get("gold", 0))
    silver = player_data.get(
        "silver", player_data.get("state", {}).get("silver", 0)
    )
    copper = player_data.get(
        "copper", player_data.get("state", {}).get("copper", 0)
    )
    inventory = player_data.get("inventory", [])
    if isinstance(inventory, dict):
        inventory = list(inventory.values())
    items = ", ".join(str(i) for i in inventory[:3])
    if len(inventory) > 3:
        items += f", and {len(inventory) - 3} more"
    parts = [
        f"{name} is a level {level} {race} {char_class}",
    ]
    if background:
        parts.append(f"from {background}")
    summary = " ".join(parts) + "."
    total_gold = gold + silver / 10 + copper / 100 + platinum * 10
    if total_gold or items:
        currency_parts = []
        if platinum:
            currency_parts.append(f"{platinum} platinum")
        if gold:
            currency_parts.append(f"{gold} gold")
        if silver:
            currency_parts.append(f"{silver} silver")
        if copper:
            currency_parts.append(f"{copper} copper")
        if currency_parts:
            summary += " They have " + ", ".join(currency_parts)
            summary += f" (worth {total_gold:.2f} gold)"
        if items:
            summary += f" and carry {items}"
        summary += "."
    return summary


def summarize_campaign(campaign_data: Dict[str, Any]) -> str:
    """Return a concise summary of the campaign."""
    quests = campaign_data.get("quests", {})
    active = len(quests.get("active", {}))
    completed = len(quests.get("completed", {}))
    npc_count = len(campaign_data.get("npcs", {}))
    events = campaign_data.get("events", {})
    last_event = ""
    if events:
        last_key = sorted(events.keys())[-1]
        last_event = events[last_key].get("description", "")
    summary = (
        f"The party knows {npc_count} NPCs. "
        f"There are {active} active quests and {completed} completed."
    )
    if last_event:
        summary += f" Recent event: {last_event}."
    return summary


def summarize_world(world_memory: List[Dict[str, Any]]) -> str:
    """Summarize notable world memory entries."""
    if not world_memory:
        return "No notable world facts are recorded yet."
    names = [entry.get("name") for entry in world_memory[:5] if entry.get("name")]
    listed = ", ".join(names)
    summary = f"Notable entries include: {listed}."
    return summary


def truncate_history(history: List[str], limit: int = 15) -> List[str]:
    """Return only the last ``limit`` lines of conversation history."""
    return history[-limit:]


def build_prompt(
    player_name: str,
    player_data: Dict[str, Any],
    campaign_data: Dict[str, Any],
    world_memory: List[Dict[str, Any]],
    conversation_history: List[str],
    current_input: str,
    system_prompt: str | None = None,
) -> str:
    """Build a text prompt for the chatbot."""
    player_summary = summarize_player(player_data)
    campaign_summary = summarize_campaign(campaign_data)
    world_summary = summarize_world(world_memory)
    history = truncate_history(conversation_history)

    intro = system_prompt or f"You are the narrator guiding {player_name} on their adventures."
    lines = [
        intro,
        "\n### Player Info",
        player_summary,
        "\n### Campaign",
        campaign_summary,
        "\n### World Memory",
        world_summary,
        "\n### Recent Conversation",
        *history,
        f"Player: {current_input}",
    ]
    return "\n".join(lines)
