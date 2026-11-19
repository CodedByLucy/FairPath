import streamlit as st

import ui

st.set_page_config(page_title="FairPath", page_icon=":material/balance:", layout="wide")

# Pages and navigation
pages = [
    st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("views/apply.py", title="Apply", icon=":material/work:"),
    st.Page("views/admin.py", title="Admin", icon=":material/admin_panel_settings:"),
]
current = st.navigation(pages, position="hidden")
ui.load_css()
ui.nav(pages)
current.run()
