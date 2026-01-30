# External:
import numpy as np
import pandas as pd

def total_return(series: pd.Series) -> float:
    """
    Computes the total geometric return of a time-series.

    Notes
    -----
    1. Assumes that the time-series is denoted in decimals.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    Returns
    -------
    float
        Total Geometric Return
    """
    return (1.0 + series).prod() - 1.0


def mean(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) arithmetic mean of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annualized) Arithmetic Mean
    """
    return series.mean() * ann_freq


def median(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) median of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annual) Median
    """
    return series.median() * ann_freq


def cagr(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the Compound Annual Growth Rate (CAGR) of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        CAGR.
    """
    return (1 + series).prod() ** (ann_freq / len(series)) - 1 if len(series) > 0 else np.nan


def std(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) standard deviation of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annualized) Standard Deviation
    """
    return series.std(ddof=1) * np.sqrt(ann_freq)


def sharpe(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) Sharpe Ratio of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annualized) Sharpe Ratio
    """
    return series.mean() / series.std(ddof=1) * np.sqrt(ann_freq)


def sortino(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) Sortino Ratio of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annualized) Sortino Ratio
    """
    if len(series) < 1 or len(series[series < 0]) == 0:
        return np.nan
    else:
        return series.mean() / np.sqrt((series[series < 0] ** 2).sum() / (len(series) - 1)) * np.sqrt(ann_freq)


def calmar(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) Calmar Ratio of a time-series.

    Notes
    -----
    1. Default ``ann_freq`` = 1, so if not specified, no annualization is performed.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    Returns
    -------
    float
        (Annualized) Calmar Ratio
    """
    return cagr(series, ann_freq) / abs(max_drawdown(series))


def max_drawdown(series: pd.Series) -> float:
    """
    Computes the geometric maximum drawdown of a time-series.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    Returns
    -------
    float
        Maximum Drawdown
    """
    # Calculate geometric cumulative product:
    cumulative_series = (1 + series).cumprod()

    # Calculate the drawdown over time:
    peak = cumulative_series.cummax()
    max_drawdown = ((cumulative_series - peak) / peak).min()

    return max_drawdown if max_drawdown != 0 else np.nan