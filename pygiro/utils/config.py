# External:
from typing import Callable
from dataclasses import dataclass

# Internal:
import pygiro.analytics.time_series as ts

@dataclass
class MetricConfig:
    """
    Container used to structure return-based performance metrics.

    Parameters
    ----------
    name : str
        The full name of the metric (e.g. 'Mean', 'Median', 'Sharpe Ratio').

    function : callable
        The corresponding function that computes the metric.

    format : str
        Type of statistic (options: "pct", "num", "int").

    scale : float, default=1
        The scaling factor.

    annualized : bool, default=False
        Whether the metric should be annualized.
    """
    # Data Class Attributes:
    name: str
    function: Callable
    format: str
    scale: int = 1
    annualized: bool = False

"""
----------------------------------------------------------------------------------------------------
Performance Metrics Configurations
----------------------------------------------------------------------------------------------------
"""
PERFORMANCE_METRICS = [
    MetricConfig(name='Total Return', function=ts.total_return, annualized=False, scale=100, format="pct"),
    MetricConfig(name='CAGR', function=ts.cagr, annualized=True, scale=100, format="pct"),
    MetricConfig(name='Mean (ann.)', function=ts.mean, annualized=True, scale=100, format="pct"),
    MetricConfig(name='Volatility (ann.)', function=ts.std, annualized=True, scale=100, format="pct"),
    MetricConfig(name='Sharpe', function=ts.sharpe, annualized=True, format="num"),
    MetricConfig(name='Sortino', function=ts.sortino, annualized=True, format="num"),
    MetricConfig(name='Calmar', function=ts.calmar, annualized=True, format="num"),
    MetricConfig(name='Max Drawdown', function=ts.max_drawdown, scale=100, format="pct"),
]