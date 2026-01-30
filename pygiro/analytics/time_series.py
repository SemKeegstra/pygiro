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


def nw_std(series: pd.Series, ann_freq: int = 1, ddof: int = 1) -> float:
    """
    Computes the (annualized) Newey-West Standard Deviation of a time-series.

    Notes
    -----
    1. Uses the Bartlett kernel (Newey-West, 1987) with equal denominator (T - ddof) across lags.
    2. The Newey-West estimator: NW = 1 / (T - ddof) × ∑_{ℓ=0}^L κ_ℓ × ∑_{t=ℓ}^T (rₜ - μ)(rₜ₋ₗ - μ)

          -    κ₀ = 1, and κ_ℓ = 2(1 - ℓ / (L + 1)) for ℓ > 0 (Bartlett weights)
          -    μ = mean of the series
          -    L = ceil(4 * (T / 100)^(2/9)) = truncation lag
          -    T = number of observations

    References
    ----------
    1. Newey, W.K., West, K.D. (1987). A Simple, Positive Semi-definite, Heteroskedasticity and Autocorrelation
       Consistent Covariance Matrix.
    2. Bali, T.G., Engle, R.F., Murray, S. (2016). Empirical Asset Pricing: The Cross Section of Stock Returns.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    ann_freq : int, default=1
        Number of periods within a year for annualization purposes.

    ddof : int, default=1
        Delta degrees of freedom used in variance calculation.

    Returns
    -------
    float
        (Annualized) Newey-West Standard Deviation
    """
    # Initialize:
    T = len(series)
    mean = series.mean()
    resid = series - mean

    # Automatic lag selection:
    L = int(np.ceil(4 * (T / 100) ** (2 / 9)))

    # Calculate Newey-West Variance:
    nw_var = 0.0
    for l in range(0, L + 1):
        weight = 2 * (1 - l / (L + 1)) if l != 0 else 1.0
        for t in range(l, T):
            nw_var += weight * resid.iloc[t] * resid.iloc[t - l]

    return ((nw_var / (T - ddof)) * ann_freq) ** 0.5


def downdev(series: pd.Series, ann_freq: int = 1) -> float:
    """
    Computes the (annualized) downside deviation of a time-series.

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
        (Annualized) Downside Deviation
    """
    if len(series) < 1:
        return np.nan
    else:
        return np.sqrt((series[series < 0] ** 2).sum() / (len(series) - 1)) * np.sqrt(ann_freq)


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


def tstat(series: pd.Series) -> float:
    """
    Computes the standard t-statistic of a time-series.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    Returns
    -------
    float
        Standard t-statistic
    """
    return series.mean() / series.std(ddof=1) * (len(series) ** 0.5) if len(series) > 0 else np.nan


def nw_tstat(series: pd.Series, ddof: int = 1) -> float:
    """
    Computes the Newey-West t-Statistic of a time-series.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).
    ddof : int, default=1
        Delta degrees of freedom used in variance calculation.

    Returns
    -------
    float
        Newey-West t-Statistic
    """
    return series.mean() / nw_std(series, ann_freq=1, ddof=ddof) * (len(series) ** 0.5)

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

def avg_drawdown(series: pd.Series) -> float:
    """
    Computes the geometric average drawdown of a time-series.

    Parameters
    ----------
    series : pd.Series
        Time-series of interest (e.g. period returns).

    Returns
    -------
    float
        Average Drawdown
    """
    # Calculate geometric cumulative product:
    cumulative_series = (1 + series).cumprod()

    # Calculate the drawdown over time:
    peak = cumulative_series.cummax()
    drawdown = (cumulative_series - peak) / peak

    # Group individual drawdowns:
    mask = drawdown != 0
    groups = mask.ne(mask.shift()).cumsum()
    drawdowns = [g for _, g in drawdown.groupby(groups) if (g.values != 0).all() and len(g) > 1]

    return np.mean([d.min() for d in drawdowns]) if drawdowns else 0.0