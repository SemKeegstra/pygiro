# External:
import pandas as pd
from pandas.tseries.offsets import MonthBegin, MonthEnd

def get_time_period(option: str, index: pd.DatetimeIndex) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Returns the ``start`` and ``end`` date for the given time period ``option``.

    Notes
    -----
    1. Bounds are clipped to the available ``index`` range.

    Parameters
    ----------
    option : str
        User-specified time period option: Full Period, MTD, QTD, YTD, 1Y, PD, PMTD, PQTD, PYTD.

    index: DatetimeIndex
        Available observation dates (e.g. the portfolio dates).

    Returns
    -------
    tuple[pd.Timestamp, pd.Timestamp]
        The applicable ``start`` and ``end`` date.
    """
    # Initialize:
    min_date = index[0]
    max_date = end = index[-1]

    # Retrieve corresponding dates:
    if option == "Full Period":
        # Full Time Period:
        start = min_date
    elif option == "MTD":
        # Month-to-Date:
        start = pd.Timestamp(year=end.year, month=end.month, day=1)
    elif option == "QTD":
        # Quarter-to-Date:
        start = end.to_period('Q').to_timestamp()
    elif option == "YTD":
        # Year-to-Date:
        start = pd.Timestamp(year=end.year, month=1, day=1)
    elif option == "1Y":
        # 1 Year:
        start = end - pd.Timedelta(days=365)
    elif option == "PD":
        # Previous Day:
        start = end - pd.Timedelta(days=1)
    elif option == "PM":
        # Previous Month:
        start = end - MonthBegin(2)
        end = start + MonthEnd(1)
    elif option == "PQ":
        # Previous Quarter:
        start = (end - pd.DateOffset(months=3)).to_period('Q').to_timestamp()
        end = start + MonthEnd(3)
    elif option == "PY":
        # Previous Year:
        start = end - MonthBegin(13)
        end = start + MonthEnd(12)
    else:
        raise ValueError(f"Input Error: {option} is not a valid time period option.")

    return max(min_date, start), min(max_date, end)