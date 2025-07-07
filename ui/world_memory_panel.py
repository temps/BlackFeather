import streamlit as st
from world_memory import ALLOWED_TYPES


def world_memory_panel():
    """Render world memory preview and add-entry form."""
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
