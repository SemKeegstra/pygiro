# Standard:
import requests

# External Packages:
import yfinance as yf

# Constants:
from ..utils.constants import FIGI_ENTRY_POINT

def get_listings(name: str) -> dict[str, dict[str, str]]:
    """
    Performs free-text search query at Yahoo Finance and retrieves all tradable listings matching the
    user-specified ``name``.

    Notes
    -----
    1. Stores the following metadata per ``ticker``:

        - ``name`` : Full name of listing.
        - ``exchange`` : Yahoo exchange symbol (e.g. AMS).
        - ``type`` : Asset type (e.g. ETF).
        - ``currency`` : Denominated currency (e.g. EUR).

    Parameters
    ----------
    name : str
        Name of the asset of interest (e.g. fund or ETF name).

    Returns
    -------
    dict
        Mapping from Yahoo ticker to basic listing metadata.
    """
    # Initialize:
    listings = dict()

    # Retrieve quoted listings:
    for quote in yf.Search(name).quotes:
        symbol = quote.get("symbol")
        if not symbol:
            continue
        else:
            listings[symbol] = dict(name=quote.get("longname", ""),
                                    exchange=quote.get("exchange", ""),
                                    type=quote.get("quoteType", ""),
                                    currency=yf.Ticker(symbol).fast_info.get("currency", ""))

    if not listings:
        raise LookupError(f"API Error: Failed to retrieve listings for {name}.")

    return listings

def get_tickers(isin: str) -> list:
    """
    Retrieves all exchange tickers associated with the given ``isin`` using the OpenFIGI mapping API.

    Notes
    -----
    1. The same ISIN may correspond to multiple tradable listings across different exchanges.
    2. Returned tickers are unique an ordered by first occurrence in the API response.

    Parameters
    ----------
    isin : str
        International Securities Identification Number (ISIN) of the asset.

    Returns
    -------
    list
        List of exchange-specific tickers associated with the ISIN.
    """
    # Initialize:
    tickers = dict()
    payload = [dict(idType="ID_ISIN", idValue=isin)]

    # Retrieve tickers:
    response = requests.post(FIGI_ENTRY_POINT, headers={"Content-Type": "application/json"}, json=payload)
    if (status := response.status_code) == 200:
        # Request succeeded:
        for obs in response.json()[0].get("data", []):
            tickers.setdefault(obs["ticker"], None)
    else:
        # Request failed:
        raise Exception(f"API Error: Failed to tickers for {isin} - status code: {status}")

    return list(tickers)