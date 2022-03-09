import streamlit as st
import sys
sys.path.append("./apps")


from multiapp import MultiApp
from apps import (
    mov_kpis,
    portcall_kpis,
    animation,

)

st.set_page_config(layout="wide")

apps = MultiApp()

# Add all your application here
apps.add_app("Movement Times", mov_kpis.app)
apps.add_app("PortCall analysis", portcall_kpis.app)
apps.add_app("Animation", animation.app)

# The main app
apps.run()