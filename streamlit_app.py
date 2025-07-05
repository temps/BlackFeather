import os
import json
import streamlit as st

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
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
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
            return json.load(f)
    return {"gold": 0, "inventory": [], "quests": []}


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

user_message = st.text_input("Message", "")
if st.button("Send") and user_message:
    st.session_state.history.append(f"Player: {user_message}")
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
        user_message,
    )
    response = get_response(prompt)
    st.session_state.history.append(f"Narrator: {response}")

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
    st.json(ps)

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

