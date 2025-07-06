# BlackFeather
Black Feather Custom is Chatbot for DMs or Roleplay. Train a model (or use prompt engineering) to act as a recurring NPC or companion in a TTRPG or fantasy game

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
