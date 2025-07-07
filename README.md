# BlackFeather
Black Feather Custom is Chatbot for DMs or Roleplay. Train a model (or use prompt engineering) to act as a recurring NPC or companion in a TTRPG or fantasy game

## Setup

Install the required packages with pip:

```bash
pip install -r requirements.txt
```

Launch the interface with:

```bash
streamlit run streamlit_app.py
```

## Currency Tracking

The Streamlit interface now includes an **Update Currency** panel under the
player stats. Use the form to add or subtract platinum, gold, silver or copper.
Negative values remove coins, while positive values add them.

## Player Journal

The `JournalManager` stores notes for each character within a campaign. A journal keeps track of:

- NPC names encountered
- Quest titles
- Logged events
- Requested images or other references
- Inventory items, gold and experience
  - including add/remove helpers

Use the journal to persist information even when chat history is truncated. The
journal file lives under each campaign's `players` directory and is named after
the character with a `_journal.json` suffix.

```python
from journal_manager import JournalManager

jm = JournalManager("summer_campaign", "Lia")
jm.add_gold(50)
jm.add_item("Magic sword")
# remove an item and log an event
jm.remove_item("Old dagger")
jm.add_event("Lia married the prince", title="Wedding")
```

## Campaigns

Each campaign lives in the `campaigns/` folder and stores its own NPCs, quests, items and event log as JSON files. Player state is kept in a `players/` subdirectory so you can manage multiple characters per campaign. Use the **Manage Campaigns** panel in the UI to create, load or delete campaigns.

## Running the Streamlit App Locally

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide your OpenAI key using the `OPENAI_API_KEY` environment variable or by adding `openai_api_key` to `st.secrets`.
3. Launch the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on deploying the app to Streamlit Cloud and Heroku.


## Running Tests

Execute the test suite with:

```bash
pytest
```

## Story Arc Features

Campaigns now automatically create a hidden villain entry and DM event log. Use
``ArcManager`` to inspect or advance the antagonist's agenda without revealing
details to the player. ``WorldMemoryManager`` accepts ``hidden=True`` to store
DM-only information and supports ``villain`` and ``plot`` entity types. Quest
titles must be unique when added via ``CampaignManager.add_quest``.
