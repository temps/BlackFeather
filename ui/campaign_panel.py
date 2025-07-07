import streamlit as st
from campaign_manager import list_campaigns, delete_campaign


def campaign_management_panel(initialize_state):
    """Render campaign management controls."""
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
