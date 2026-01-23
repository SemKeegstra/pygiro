# External packages:
import pandas as pd
import yfinance as yf


def get_closing_prices(tickers: str | list[str], start: str | pd.Timestamp, end: str | pd.Timestamp) -> pd.DataFrame:
    """
    Retrieves daily closing prices for one or more ``tickers`` using the yahoo finance API.

    Parameters
    ----------
    tickers : str | list[str]
        The ticker(s) identifying the asset(s) of interest.

    start: str | pd.Timestamp
        The start date of the period.

    end: str | pd.Timestamp
        The end date of the period.

    Returns
    -------
    pd.DataFrame
        Multi-index DataFrame containing asset closing prices.
    """
    # Initialize:
    tickers = [tickers] if isinstance(tickers, str) else tickers

    # Retrieve closing prices:
    prices = yf.download(tickers=tickers, start=start, end=end, progress=False)["Close"]

    # Multi-index format:
    if prices.empty:
        raise ValueError("API Error: No pricing data obtained from server.")
    else:
        prices  = prices.rename_axis(index='date', columns='ticker').stack().to_frame('close')

    return prices