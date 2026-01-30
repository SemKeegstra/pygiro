# External:
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def time_weighted_returns(returns: pd.Series) -> go.Figure:
    """
    Plots the cumulative time-weighted ``return`` of the portfolio over time.

    Notes
    -----
    1. The return series is extended with a synthetic initial observation that starts at 0%.

    Parameters
    ----------
    returns : pd.Series
        Daily time-weighted returns, indexed by date.

    Returns
    -------
    Figure
        Interactive line chart of cumulative time-weighted returns in percent.
    """
    # Initialize (add leading zero):
    base = returns.index.min() - pd.Timedelta(days=1)
    twr = pd.concat([pd.Series([0.0], index=[base]), returns])

    # Calculate cumulative return:
    cum_ret = ((1 + twr).cumprod() - 1) * 100

    # Set figure:
    fig = px.line(x=cum_ret.index,
                  y=cum_ret.values,
                  labels=dict(x="Date", y="Cumulative Returns (in %)"),
                  title="Time-Weighted Returns")

    # Formatting:
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))

    return fig

def profit_and_loss(portfolio: pd.DataFrame) -> go.Figure:
    """
    Plots the unrealized profit and loss of the ``portfolio`` over time.

    Notes
    -----
    1. The P&L is computed relative to the initial invested capital s.t. the first observation is normalized to zero.

    Parameters
    ----------
    portfolio: pd.DataFrame
        Portfolio view from the Account class, indexed by (date, asset).

    Returns
    -------
    Figure
        Interactive line chart of unrealized P&L in EUR.
    """
    # Initialize:
    initial_capital = portfolio.loc[portfolio.index.get_level_values(0)[0]].sum()
    capital = portfolio.groupby(level=0).sum().sub(initial_capital)

    # Calculate P&L:
    profit = capital.value - capital.investment

    # Set figure:
    fig = px.line(x=profit.index,
                  y=profit.values,
                  labels=dict(x="Date", y="P&L (in EUR)"),
                  title="Unrealized Gains")

    # Formatting:
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))

    return fig