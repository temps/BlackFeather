import os
import json
import streamlit as st


def player_stats_panel(player_name, load_player_state):
    """Display player stats, currency update form, and inventory."""
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
