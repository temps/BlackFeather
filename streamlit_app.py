import os
import json
import streamlit as st

from config import CONFIG

from campaign_manager import (
    CampaignManager,
    PlayerManager,
    PlayerCharacter,
    list_campaigns,
    delete_campaign,
)
from world_memory import WorldMemoryManager, ALLOWED_TYPES
from prompt_builder import build_prompt

# Handle API key presence detection
has_api_key = (
    "openai_api_key" in st.secrets
    or st.secrets.get("general", {}).get("openai_api_key")
    or os.getenv("OPENAI_API_KEY")
)
st.write("\U0001F512 OpenAI key loaded:", "\u2705" if has_api_key else "\u274C")


def get_response(prompt: str) -> str:
    """Return a response from OpenAI's chat API with graceful errors."""
    try:
        api_key = (
            st.secrets.get("openai_api_key")
            or st.secrets.get("general", {}).get("openai_api_key")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            st.error("Missing OpenAI API key.")
            return "\u26A0\ufe0f Missing API key."

        import openai

        openai.api_key = api_key
        messages = []
        if CONFIG.system_prompt:
            messages.append({"role": "system", "content": CONFIG.system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = openai.ChatCompletion.create(
            model=CONFIG.chat_model,
            messages=messages,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:  # pragma: no cover - depends on external API
        st.error(f"API Error: {e}")
        return f"\u274c API Error: {e}"


def initialize_state(campaign_name: str, player_name: str):
    """Load managers and ensure player state exists."""
    cm = CampaignManager(campaign_name)
    cm.initialize_player_state(player_name)
    pm = PlayerManager()
    character = pm.load_character(player_name)
    wm = WorldMemoryManager(campaign_name)
    st.session_state.campaign_manager = cm
    st.session_state.player_manager = pm
    st.session_state.world_memory = wm
    if character is None:
        st.session_state.character_missing = True
    else:
        st.session_state.character_missing = False
        st.session_state.character = character


def character_creation_form(default_name: str):
    """Display a form for new character creation."""
    pm: PlayerManager = st.session_state.player_manager
    with st.form("create_character"):
        st.write("Create a new character")
        name = st.text_input("Name", default_name)
        race = st.text_input("Race")
        char_class = st.text_input("Class")
        level = st.number_input("Level", min_value=1, step=1, value=1)
        background = st.text_input("Background")
        submitted = st.form_submit_button("Create")
        if submitted:
            pc = PlayerCharacter(
                name=name,
                race=race,
                character_class=char_class,
                level=int(level),
                background=background,
                attributes={},
            )
            os.makedirs(os.path.dirname(pm._player_file(name)), exist_ok=True)
            with open(pm._player_file(name), "w", encoding="utf-8") as f:
                json.dump(pc.to_dict(), f, indent=2)
            st.session_state.character = pc
            st.session_state.character_missing = False
            st.experimental_rerun()


def load_player_state(cm: CampaignManager, player_name: str) -> dict:
    path = cm._player_state_file(player_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Backwards compatibility for older saves with only gold
        if "platinum" not in data:
            data.setdefault("platinum", 0)
        if "silver" not in data:
            data.setdefault("silver", 0)
        if "copper" not in data:
            data.setdefault("copper", 0)
        if "gold" not in data:
            data.setdefault("gold", 0)
        if "inventory" not in data:
            data["inventory"] = []
        if "quests" not in data:
            data["quests"] = []
        return data
    return {
        "platinum": 0,
        "gold": 0,
        "silver": 0,
        "copper": 0,
        "inventory": [],
        "quests": [],
    }


def load_campaign_data(cm: CampaignManager) -> dict:
    return {
        "npcs": cm._load_json("npcs.json"),
        "quests": cm._load_json("quests.json"),
        "items": cm._load_json("items.json"),
        "events": cm._load_json("events_log.json"),
    }


st.title("TTRPG Chatbot")

with st.expander("Manage Campaigns"):
    campaigns = list_campaigns()
    if campaigns:
        selected = st.selectbox("Existing Campaigns", campaigns, key="campaign_select")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load", key="load_campaign_btn"):
                st.session_state.campaign_name = selected
                for key in ("campaign_manager", "player_manager", "world_memory"):
                    st.session_state.pop(key, None)
                st.session_state.history = []
                if st.session_state.get("player_name"):
                    initialize_state(selected, st.session_state["player_name"])
                st.experimental_rerun()
        with col2:
            if st.button("Delete", key="delete_campaign_btn"):
                delete_campaign(selected)
                if st.session_state.get("campaign_name") == selected:
                    for key in (
                        "campaign_manager",
                        "player_manager",
                        "world_memory",
                        "campaign_name",
                    ):
                        st.session_state.pop(key, None)
                st.experimental_rerun()
    else:
        st.write("No campaigns found.")

campaign_name = st.text_input(
    "Campaign Name",
    st.session_state.get("campaign_name", "demo"),
)
player_name = st.text_input("Player Name", st.session_state.get("player_name", ""))

if campaign_name and player_name and "campaign_manager" not in st.session_state:
    initialize_state(campaign_name, player_name)
    st.session_state.campaign_name = campaign_name
    st.session_state.player_name = player_name

if st.session_state.get("character_missing"):
    st.warning("Character not found. Please create one.")
    character_creation_form(player_name)
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []
if "user_message" not in st.session_state:
    st.session_state.user_message = ""

user_message = st.text_input("Message", st.session_state.user_message, key="msg_input")
if st.button("Send") and st.session_state.user_message:
    msg_to_send = st.session_state.user_message
    st.session_state.history.append(f"Player: {msg_to_send}")
    cm = st.session_state.campaign_manager
    wm = st.session_state.world_memory

    player_state = load_player_state(cm, player_name)
    character = st.session_state.character.to_dict() if hasattr(st.session_state.character, 'to_dict') else st.session_state.character
    player_data = {**character, **player_state}

    campaign_data = load_campaign_data(cm)
    world_mem = list(wm._load().values())

    prompt = build_prompt(
        player_name,
        player_data,
        campaign_data,
        world_mem,
        st.session_state.history,
        msg_to_send,
        CONFIG.system_prompt,
    )
    response = get_response(prompt)
    st.session_state.history.append(f"Narrator: {response}")
    st.session_state.user_message = ""

for line in st.session_state.history:
    if line.startswith("Player: "):
        msg = line.split(": ", 1)[1]
        st.markdown(f"\U0001F9D1 **{msg}**")
    elif line.startswith("Narrator: "):
        msg = line.split(": ", 1)[1]
        st.markdown(f"\U0001F4D6 *{msg}*")
    else:
        st.write(line)


if st.button("Save Chat Log"):
    os.makedirs("logs", exist_ok=True)
    log_name = f"{campaign_name}_{player_name}.json".replace(" ", "_")
    with open(os.path.join("logs", log_name), "w", encoding="utf-8") as f:
        json.dump(st.session_state.history, f, indent=2)
    st.success(f"Chat log saved to {log_name}")

st.header("Player Stats")
if "campaign_manager" in st.session_state:
    ps = load_player_state(st.session_state.campaign_manager, player_name)
    cols = st.columns(5)
    cols[0].metric("Platinum", ps.get("platinum", 0))
    cols[1].metric("Gold", ps.get("gold", 0))
    cols[2].metric("Silver", ps.get("silver", 0))
    cols[3].metric("Copper", ps.get("copper", 0))
    total_gold = ps.get("gold", 0) + ps.get("silver", 0) / 10 + ps.get("copper", 0) / 100 + ps.get("platinum", 0) * 10
    cols[4].metric("Total (g)", f"{total_gold:.2f}")

    with st.expander("Update Currency"):
        with st.form("update_currency"):
            delta_platinum = st.number_input("Platinum \u2795\u2796", value=0, step=1)
            delta_gold = st.number_input("Gold \u2795\u2796", value=0, step=1)
            delta_silver = st.number_input("Silver \u2795\u2796", value=0, step=1)
            delta_copper = st.number_input("Copper \u2795\u2796", value=0, step=1)
            submitted = st.form_submit_button("Apply")
            if submitted:
                new_state = {
                    "platinum": ps.get("platinum", 0) + int(delta_platinum),
                    "gold": ps.get("gold", 0) + int(delta_gold),
                    "silver": ps.get("silver", 0) + int(delta_silver),
                    "copper": ps.get("copper", 0) + int(delta_copper),
                }
                st.session_state.campaign_manager.update_player_state(player_name, new_state)
                st.experimental_rerun()

    st.subheader("Inventory")
    for idx, item in enumerate(ps.get("inventory", [])):
        if st.button(item, key=f"inv_{idx}"):
            st.session_state.user_message = item
            st.experimental_rerun()

st.header("World Memory Preview")
if "world_memory" in st.session_state:
    wm_data = list(st.session_state.world_memory._load().values())[:5]
    st.json(wm_data)

    with st.expander("Add World Memory Entry"):
        with st.form("add_memory"):
            mem_type = st.selectbox("Type", ALLOWED_TYPES)
            name = st.text_input("Name")
            desc = st.text_area("Description")
            tags = st.text_input("Tags (comma separated)")
            submitted = st.form_submit_button("Add")
            if submitted:
                wm = st.session_state.world_memory
                try:
                    wm.add_memory_entry(
                        {
                            "type": mem_type,
                            "name": name,
                            "description": desc,
                            "tags": [t.strip() for t in tags.split(',') if t.strip()],
                        }
                    )
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(str(e))

