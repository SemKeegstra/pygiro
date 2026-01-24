# Standard:
import requests

# External packages:
import pandas as pd
import yfinance as yf

# Constants:
from ..utils.constants import EXR_ENTRY_POINT
from ..utils.mappings import PANDAS_FREQ_MAPPING as FREQUENCY

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
        raise LookupError("API Error: Failed to retrieve price data.")
    else:
        prices  = prices.rename_axis(index='date', columns='ticker').stack().to_frame('close')

    return prices

def _get_ecb_rate(quote: str, start: str, end: str, freq: str, var: str) -> pd.DataFrame:
    """
    Performs API call to the database of the European Central Bank (ECB) and retrieves the EUR/``quote`` exchange rate.

    Parameters
    ----------
    quote : str
        ISO 4217 code of the quote currency (e.g. USD).

    start: str
        The start date of the period.

    end: str
        The end date of the period.

    freq: str, default="D"
        Frequency at which the exchange rate is measured:

            - ``"D"`` : Daily
            - ``"M"`` : Monthly
            - ``"Q"`` : Quarterly
            - ``"A"`` : Annual

    var: str, default="A"
        The time-series variation of the measurement:

            - ``"A"`` : Average
            - ``"E"`` : End-of-Period (not applicable to daily)

    Returns
    -------
    pd.DataFrame
        Time-series of the exchange rate.
    """
    # Initialize:
    url = EXR_ENTRY_POINT + f"{freq}.{quote}.EUR.SP00.{var}?startPeriod={start}&endPeriod={end}"

    # Retrieve foreign exchange rate:
    response = requests.get(url, headers={"Accept": "application/json"})
    if (status := response.status_code) == 200:
        # Request succeeded:
        data = response.json()
        # Retrieve rates & corresponding dates:
        obs = data['dataSets'][0]['series']['0:0:0:0:0']['observations']
        rates = [obs[key][0] for key in obs.keys()]
        dates = [date['id'] for date in data['structure']['dimensions']['observation'][0]['values']]
    else:
        # Request failed:
        raise Exception(f"API Error: Failed to retrieve exchange rates - status code: {status}")

    return pd.DataFrame(rates, index=pd.to_datetime(dates))

def get_exchange_rate(base: str, quote: str, start: str, end: str, freq: str = "D",
                      var: str = "A") -> pd.DataFrame:
    """
    Retrieves the foreign exchange rates (FX) of ``base``/``quote`` from ``start`` till ``end`` for a specified
    frequency from the European Central Bank (ECB) database.

    Notes
    -----
    1. The FX rate represents the value of 1 unit of the base currency expressed in the quote currency.

    Parameters
    ----------
    base : str
        ISO 4217 code of the base currency (e.g. EUR).

    quote : str
        ISO 4217 code of the quote currency (e.g. USD).

    start: str
        The start date of the period (ISO 8601 format: "YYYY-MM-DD").

    end: str
        The end date of the period (ISO 8601 format: "YYYY-MM-DD").

    freq: str, default="D"
        Frequency at which the exchange rate is measured:
        - ``"D"`` : Daily
        - ``"M"`` : Monthly
        - ``"Q"`` : Quarterly
        - ``"A"`` : Annual

    var: str, default="A"
        The time-series variation of the measurement:
        - ``"A"`` : Average
        - ``"E"`` : End-of-Period (not applicable to daily)

    Returns
    -------
    pd.DataFrame
        Time-series of the requested exchange rate.
    """
    # Input evaluation:
    if freq == "D" and var == "E":
        raise ValueError("Input Error: end-of-period <var> not applicable for daily <freq>.")

    # Initialize:
    period = pd.date_range(start, end, freq=FREQUENCY[freq])

    # Retrieve exchange rate:
    if base == quote:
        fx = pd.DataFrame({0:1.0}, index=period)
    elif base == "EUR":
        fx = _get_ecb_rate(quote=quote, start=start, end=end, freq=freq, var=var)
    elif quote == "EUR":
        fx = 1 / _get_ecb_rate(quote=base, start=start, end=end, freq=freq, var=var)
    else:
        eur_base = _get_ecb_rate(quote=base, start=start, end=end, freq=freq, var=var)
        eur_quote = _get_ecb_rate(quote=quote, start=start, end=end, freq=freq, var=var)
        fx = (1 / eur_base) * eur_quote

    return fx.reindex(period).ffill().rename(columns={0: f'{base}/{quote}'})