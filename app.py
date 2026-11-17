
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
import html

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. SESSION STATE
# =========================================================

DEFAULTS = {
    "dashboard_entered": False,
    "loan_data_bytes": None,
    "loan_sheet": None,
    "main_navigation": "Summary"
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# 3. THEME COLORS
# =========================================================

NAVY = "#38285F"
BLUE = "#62508F"
ORANGE = "#F2B900"
GREEN = "#35AE69"
PURPLE = "#7763A8"
RED = "#E47D83"

TEXT = "#242033"
MUTED = "#92909D"
BORDER = "#ECEAF1"
PAGE_BG = "#F1EFF6"

STATUS_COLORS = {
    "Disbursed": GREEN,
    "Approved": BLUE,
    "Under Review": ORANGE,
    "Pending": PURPLE,
    "Rejected": RED
}

# =========================================================
# 4. GLOBAL CSS
# =========================================================

st.markdown(
    f"""
    <style>
    :root {{
        --jr-purple: #38285F;
        --jr-purple-light: #62508F;
        --jr-lavender: #F1EFF6;
        --jr-text: #242033;
        --jr-muted: #92909D;
        --jr-border: #ECEAF1;
    }}

    .stApp {{
        background: var(--jr-lavender);
        color: var(--jr-text);
    }}

    [data-testid="stHeader"] {{
        background: transparent;
        height: 2.4rem;
    }}

    [data-testid="stToolbar"] {{ right: 1rem; }}

    .block-container {{
        padding-top: 1.45rem;
        padding-bottom: 2rem;
        max-width: 1680px;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #38285F 0%, #493878 68%, #38285F 100%);
        border-right: 0;
        min-width: 245px;
