import os
import json
import streamlit as st

from campaign_manager import CampaignManager, PlayerManager
from world_memory import WorldMemoryManager
from prompt_builder import build_prompt


def get_response(prompt: str) -> str:
    """Return a response from OpenAI's chat API."""
    import openai

    api_key = st.secrets.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Missing OpenAI API key."
    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message["content"].strip()


def initialize_state(campaign_name: str, player_name: str):
    """Load managers and ensure player state exists."""
    cm = CampaignManager(campaign_name)
    cm.initialize_player_state(player_name)
    pm = PlayerManager()
    character = pm.load_character(player_name)
    if character is None:
        character = pm.create_character()
    wm = WorldMemoryManager(campaign_name)
    st.session_state.campaign_manager = cm
    st.session_state.player_manager = pm
    st.session_state.world_memory = wm
    st.session_state.character = character


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

campaign_name = st.text_input("Campaign Name", st.session_state.get("campaign_name", "demo"))
player_name = st.text_input("Player Name", st.session_state.get("player_name", ""))

if campaign_name and player_name and "campaign_manager" not in st.session_state:
    initialize_state(campaign_name, player_name)
    st.session_state.campaign_name = campaign_name
    st.session_state.player_name = player_name

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
    st.write(line)

st.header("Player Stats")
if "campaign_manager" in st.session_state:
    ps = load_player_state(st.session_state.campaign_manager, player_name)
    st.json(ps)

st.header("World Memory Preview")
if "world_memory" in st.session_state:
    wm_data = list(st.session_state.world_memory._load().values())[:5]
    st.json(wm_data)
