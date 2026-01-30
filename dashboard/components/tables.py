# Standard:
from dataclasses import dataclass

# External:
import numpy as np
import pandas as pd
import streamlit as st

# Internal:
from pygiro.utils.config import *

@dataclass(frozen=True)
class TableElement:
    """
    Lightweight container representing a single metric displayed in a table or grid.

    Attributes
    ----------
    name : str
        Display name of the metric.

    value : str
        Pre-formatted metric value as a string.
    """
    name: str
    value: str

def _metric_to_string(value: float, kind: str, currency: str = "€") -> str:
    """
    Formats a numeric metric ``value`` as a user-friendly string.

    Parameters
    ----------
    value : float
        Raw metric value.

    kind : str
        Output format identifier:

        - ``"pct"`` : percentage
        - ``"int"`` : integer
        - ``"cur"`` : currency
        - otherwise : float with two decimals

    currency : str, default="€"
        Currency symbol, used if ``kind="cur"``.

    Returns
    -------
    str
        Formatted metric value.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    if kind == "pct":
        return f"{value:.2f}%"
    if kind == "int":
        return f"{int(round(value))}"
    if kind == "cur":
        sign = "-" if value < 0 else ""
        return f"{sign}{currency} {abs(value):,.2f}"
    return f"{value:.2f}"

def return_metrics(returns: pd.Series, ann_freq: int = 252) -> list[TableElement]:
    """
    Computes portfolio performance metrics from daily ``returns``.

    Notes
    -----
    1. Only business days are used; weekend observations are excluded.

    Parameters
    ----------
    returns : pd.Series
        Daily portfolio returns, indexed by date.

    ann_freq : int, default=252
        Number of periods within a year for annualization purposes.

    Returns
    -------
    list[TableElement]
        List of formatted performance metrics ready for display.
    """
    # Initialize:
    returns = returns[returns.index.weekday < 5].copy()

    # Compute metrics:
    metrics = []
    for metric in PERFORMANCE_METRICS:
        args = dict(ann_freq=ann_freq) if metric.annualized else dict()
        stat = metric.function(returns, **args) * metric.scale
        metrics.append(TableElement(name=metric.name, value=_metric_to_string(value=stat, kind=metric.format)))

    return metrics

def balance_metrics(portfolio: pd.DataFrame, isins: set, currencies: set) -> list[TableElement]:
    """
    Retrieves the current decomposition of the account balance and calculates the unrealized gains of the ``portfolio``.

    Notes
    -----
    1. Period P&L reflects unrealized gains accrued during the selected period and excludes gains prior to the start.

    Parameters
    ----------
    portfolio : pd.DataFrame
        Portfolio view of the Account class, indexed by (date, asset).

    isins : set
        Asset identifiers representing investable securities.

    currencies : set
        Currency identifiers representing cash positions.

    Returns
    -------
    list[TableElement]
        List of formatted balance metrics ready for display.
    """
    # Initialize:
    start = portfolio.loc[portfolio.index.get_level_values(0)[0]]
    end = portfolio.loc[portfolio.index.get_level_values(0)[-1]]
    start_idx, end_idx = start.index.isin(isins), end.index.isin(isins)

    # Retrieve balance decomposition:
    balance = end.value.sum()
    valuation = end[end_idx].value.sum()
    cash = end[end.index.isin(currencies)].value.sum()

    # Calculate P&L:
    v0, v1 = start.loc[start_idx].value.sum(), end.loc[end_idx].value.sum()
    cf = end.loc[end_idx].investment.sum() - start.loc[start_idx].investment.sum()
    gains = (v1 - v0) - cf

    # Formatting:
    metrics = [
        TableElement(name="Account", value=_metric_to_string(value=balance, kind="cur")),
        TableElement(name="Portfolio", value=_metric_to_string(value=valuation, kind="cur")),
        TableElement(name="Cash", value=_metric_to_string(value=cash, kind="cur")),
        TableElement(name="Period P&L", value=_metric_to_string(value=gains, kind="cur")),
    ]

    return metrics


def render_grid(metrics: list[TableElement], ncols: int = 2) -> None:
    """
    Renders a grid of performance ``metrics`` using Streamlit.

    Parameters
    ----------
    metrics : list[TableElement]
        List of formatted performance metrics ready for display.

    ncols : int, default=2
        Number of columns per row in the grid.
    """
    # Rows:
    for row in range(0, len(metrics), ncols):
        columns = st.columns(ncols, gap="medium")
        for col in range(ncols):
            idx = row + col
            if idx >= len(metrics):
                break
            metric = metrics[idx]
            with columns[col]:
                st.metric(metric.name, metric.value)