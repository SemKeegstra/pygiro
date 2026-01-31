# Standard:
from pathlib import Path

# External:
import pandas as pd
import streamlit as st

# Internal:
from components.style import load_css
from pygiro.degiro.account import Account
from pygiro.api.assets import get_listings


# ======================
# Initialization
# ======================
load_css()
app_dir = Path(__file__).resolve().parents[1]

# ======================
# Page Title
# ======================

st.set_page_config(page_title="PyGiro - Account Loader", layout="wide")
st.image(app_dir / "dashboard" / "assets" / "png" / "logo_alternative.png", width=250)
st.write("Please upload your DEGIRO account statement CSV here:")

# ======================
# File Loader
# ======================

# Retrieve file:
file = st.file_uploader("Account statement (CSV)", type=["csv"], accept_multiple_files=False)
if file is not None:
    # Import raw account statement:
    statement = pd.read_csv(file, sep=",", engine="c")

    # Retrieve isin-ticker options:
    options = dict()
    for isin in set(statement.ISIN.dropna()):
        if isin != 'NLFLATEXACNT':
            options[isin] = get_listings(statement[statement.ISIN == isin].iloc[0].Product)

    # ======================
    # Ticker Selection
    # ======================

    st.divider()
    st.subheader("Select Tickers")

    selected: dict[str, str] = {}
    for isin in options:
        tickers = list(options[isin].keys())
        cols = st.columns([1, 2])
        cols[0].markdown(f"`{isin}`")
        selected[cols[1].selectbox(label=f"{isin}_TICKER", options=tickers, key=isin, label_visibility="collapsed")] = isin

    # ======================
    # Proceed
    # ======================

    st.divider()
    col1, col2 = st.columns([1, 5])
    with col1:
        proceed = st.button("Proceed", type="primary", use_container_width=True)
        if proceed:
            # Construct account:
            account = Account(file=statement, mapping=selected)
            account.compute_returns()

            # Next page:
            st.session_state["dir"] = app_dir
            st.session_state["account"] = account
            st.switch_page("pages/performance.py")