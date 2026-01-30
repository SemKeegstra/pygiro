# External:
import numpy as np
import pandas as pd
import streamlit as st

# Internal:
import components.tables as tbl
import components.figures as plot
from components.tables import return_metrics, render_grid
from components.style import load_css
from components.lib import get_time_period

# Constants:
from components.constants import TIME_PERIODS, FIGURES

# ======================
# Initialization
# ======================

# Styling:
load_css()

# State Attributes:
acc = st.session_state["account"]

# Time Period:
min_date = acc.returns.TWR.index.min().date()
max_date = acc.returns.TWR.index.max().date()
if "active_manual_range" not in st.session_state:
    st.session_state["active_manual_range"] = (min_date, max_date)

# ======================
# Page Title
# ======================

st.set_page_config(page_title="PyGiro - Performance", layout="wide")
st.title("Performance Overview")

# ======================
# Settings
# ======================

settings = st.columns([2, 2, 2])
with settings[0]:
    # View Type - Button:
    view = st.selectbox("View:", options=[f for f in FIGURES])
with settings[1]:
    # Select Time Period - Button:
    period_option = st.selectbox("Select Time Period:", options=[p for p in TIME_PERIODS])
with settings[2]:
    # Manual Date Range - Button:
    manual_range = st.date_input("Manual Date Range:", value=st.session_state["active_manual_range"],
                                 min_value=min_date, max_value=max_date, disabled=(period_option != "Manual Period"))

# Format selection:
if period_option == "Manual Period":
    if len(manual_range) == 2:
        st.session_state["active_manual_range"] = pd.Timestamp(manual_range[0]), pd.Timestamp(manual_range[1])
    start_date, end_date = st.session_state["active_manual_range"]
else:
    start_date, end_date = get_time_period(option=period_option, index=acc.returns.index)

# ======================
# Performance Input
# ======================
data = acc.returns.TWR.loc[start_date:end_date] if view == "Returns" else acc.portfolio.loc[start_date:end_date]


# ======================
# Performance Figure
# ======================
figure, table = st.columns([3, 1], gap="large")
with figure:
    if view == "Returns":
        fig = plot.time_weighted_returns(returns=data)
        st.plotly_chart(fig, width="stretch")
    elif view == "Profit & Loss":
        fig = plot.profit_and_loss(portfolio=data)
        st.plotly_chart(fig, width="stretch")

# ======================
# Performance Metrics
# ======================
with table:
    if view == "Returns":
        st.subheader("Metrics")
        rows = tbl.return_metrics(returns=data)
        tbl.render_grid(rows, ncols=2)
    elif view == "Profit & Loss":
        st.subheader("Balance")
        rows = tbl.balance_metrics(portfolio=data, isins=acc.isins, currencies=acc.currencies)
        tbl.render_grid(rows, ncols=1)
