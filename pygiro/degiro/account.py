# Standard:
from collections import defaultdict

# External:
import pandas as pd

# Internal:
from ..api.assets import get_listings
from ..api.prices import get_closing_prices, get_exchange_rate

# Constants:
from ..utils.mappings import LINE_TYPES
from ..utils.constants import STATEMENT_COLS, NUMERIC_COLS


class Account:
    """
    Represents a DEGIRO brokerage account.

    Attributes
    ----------
    statement : pd.DataFrame
        Formatted DEGIRO account statement indexed by transaction time.

    portfolio : pd.DataFrame
        Daily end-of-day portfolio holdings.

    isins : set[str]
        Set of unique ISINs present in the account.

    currencies : set[str]
        Set of currencies present in the account.

    tickers : dict[str, str]
        The used mapping from Yahoo ticker symbol to ISIN.
    """
    def __init__(self, file: str | pd.DataFrame, mapping: dict[str, str] | None = None):
        """
        Initializes a brokerage ``Account`` from a DEGIRO account statement.

        Notes
        -----
        1. The account statement can be downloaded from the DEGIRO website or app via:
           - Inbox → Account Statement → Export → CSV.
           - Ensure the start date covers the full investment period of interest.
        2. During initialization, the account statement is formatted, asset identifiers are extracted, and a daily
           end-of-day portfolio is constructed.
        3. Missing ticker-to-ISIN mappings are resolved automatically where possible.

        Parameters
        -----------
        file: str | pd.DataFrame
            Path to a DEGIRO account statement CSV file or a raw account statement ``DataFrame``.

        mapping: dict[str, str] | None
            Optional user-specified mapping from Yahoo ticker symbol to ISIN.
        """
        # Initialize:
        self.file: pd.DataFrame = self._read_file(path=file) if isinstance(file, str) else file

        # Account statement:
        self.statement: pd.DataFrame = self._format_account_statement(file=self.file)
        self.isins: set[str] = set(self.statement.ISIN.dropna())
        self.currencies: set[str] = set(self.statement.currency.dropna())
        self.tickers: dict[str, str] = self._complete_ticker_mapping(mapping=mapping)

        # Investment portfolio:
        self.portfolio: pd.DataFrame = self._built_portfolio()
        self._add_prices()
        self._compute_valuation()

    @staticmethod
    def _read_file(path: str) -> pd.DataFrame:
        """
        Retrieves the raw DEGIRO account statement from the user-specified location.

        Parameters
        ----------
        path: str
            Location of the DEGIRO account statement csv file.

        Returns
        -------
        pd.DataFrame
            The raw account statement.
        """
        return pd.read_csv(path, sep=",", engine="c")

    @staticmethod
    def _classify_line(line: pd.Series) -> str:
        """
        Classifies a single account statement line based on its description.

        Parameters
        ----------
        line : pd.Series
            Line from the account statement.

        Returns
        -------
        str
            Line type identifier (e.g. buy, sell, deposit, cost).
        """
        # Initialize:
        description = str(line.description).lower()

        for line_type, keywords in LINE_TYPES.items():
            if any(keyword in description for keyword in keywords):
                return line_type

        return "other"

    def _format_account_statement(self, file: pd.DataFrame) -> pd.DataFrame:
        """
        Formats a DEGIRO account statement.

        Notes
        -----
        1. Repairs split rows, parses numeric fields, formats timestamps, classifies line types
           and extracts shares & prices from the description.

        Parameters
        ----------
        file : pd.DataFrame
            The raw account statement.

        Returns
        -------
        pd.DataFrame
            Cleaned account statement indexed by transaction time.
        """
        # Initialize:
        statement =  file.set_axis(STATEMENT_COLS, axis=1)

        # Handle extended rows:
        for idx, line in statement[statement.date.isna()].iterrows():
            statement.iloc[idx - 1] += line.fillna("")
        statement.dropna(subset=["date"], inplace=True)

        # Date formatting:
        statement.index = pd.to_datetime(statement.date + " " + statement.pop("time"), format="%d-%m-%Y %H:%M")
        statement.date = pd.to_datetime(statement.date, format="%d-%m-%Y")
        statement.sort_index(inplace=True)

        # Number parsing:
        statement[NUMERIC_COLS] = statement[NUMERIC_COLS].replace({",": "."}, regex=True).astype(float)

        # Type classification:
        statement["type"] = pd.Categorical(statement.apply(self._classify_line, axis=1), categories=LINE_TYPES.keys())

        # Share extraction:
        statement['shares'] = statement.description.str.extract(r"(?:Koop|Verkoop)\s+(\d+)", expand=False).astype(float)
        statement.loc[statement["type"] == "sell", "shares"] *= -1

        # Price extraction:
        statement['price'] = statement.description.str.extract(r"@\s*([\d.,]+)", expand=False).str.replace(",",".").astype(float)

        return statement[statement.type != 'other']

    def _complete_ticker_mapping(self, mapping: dict[str, str] | None) -> dict[str, str]:
        """
        Completes the user-specified ticker-to-ISIN ``mapping`` for all assets present in the account statement.

        Notes
        -----
        1. For ISINs not provided by the user, candidate tickers are retrieved via ``api.assets.get_listings()``.
        2. The first ticker with matching currency is selected.
        3. Tickers in question are Yahoo ticker symbols.

        Parameters
        ----------
        mapping: dict[str, str] | None
            Optional ticker-to-ISIN mapping.

        Returns
        -------
        dict[str,str]
            Completed mapping from Ticker symbol to ISIN.
        """
        # Initialize:
        mapping = dict() if mapping is None else mapping

        # Add missing tickers:
        for isin in self.isins - set(mapping.values()):
            asset = self.statement[self.statement.ISIN == isin].iloc[0]
            currency = asset["currency"]
            for ticker in (tickers := get_listings(name=asset["name"])):
                # Currency matching:
                if (tickers[ticker]["currency"] == currency) and (ticker not in mapping):
                    mapping[ticker] = isin
                    break

        return mapping

    def _built_portfolio(self) -> pd.DataFrame:
        """
        Builds a daily end-of-day ``portfolio`` overview from the formatted DEGIRO account statement.

        Notes
        -----
        1. The portfolio is defined as a multi-index DataFrame (date, asset).
        2. End date is set to yesterday to support the retrieval of closing prices.
        3. Tracks asset holdings and total invested value.

        Returns
        -------
        pd.DataFrame
            Daily portfolio.
        """
        # Initialize:
        holdings, current_holdings = dict(), defaultdict(float)
        investments, current_investment = dict(), defaultdict(float)

        # Construct portfolio:
        for date, frame in self.statement.groupby("date"):
            for _, line in frame.iterrows():
                # Adjust balance
                current_holdings[line.currency] += line.amount
                current_investment[line.currency] += line.amount
                # Adjust shares (if needed):
                if line.type in {"buy", "sell"}:
                    current_holdings[line.ISIN] += line.shares
                    current_investment[line.ISIN] -= line.amount
            holdings[date] = current_holdings.copy()
            investments[date] = current_investment.copy()

        # Multi-Index format:
        holdings = pd.DataFrame.from_records(((d, a, v) for d, h in holdings.items() for a, v in h.items()),
                                             columns=["date", "asset", "holding"]).set_index(["date", "asset"])
        investments = pd.DataFrame.from_records(((d, a, v) for d, h in investments.items() for a, v in h.items()),
                                                columns=["date", "asset", "investment"]).set_index(["date", "asset"])

        # Merge data:
        portfolio = holdings.join(investments, how="outer")

        # Daily frequency:
        period = pd.date_range(self.statement.date.iloc[0], pd.Timestamp.today() - pd.Timedelta(days=1), freq="D", name="date")
        portfolio = portfolio.unstack(level=1).reindex(period).ffill().stack(future_stack=True)

        return portfolio[portfolio.holding != 0.0].dropna()

    def _add_prices(self):
        """
        Adds daily prices to the ``portfolio`` attribute as column ``"close"``.

        Notes
        -----
        1. For investable assets, closing prices are retrieved via ``api.assets.get_closing_prices()``.
        2. For currencies, exchange rates are retrieved via ``api.assets.get_exchange_rate()``.
        """
        # Initialize:
        frames: list[pd.DataFrame] = []

        # Period:
        dates = self.portfolio.index.get_level_values("date")
        start, end = str(dates[0].date()), str(dates[-1].date())

        # Retrieve closing prices for financial assets:
        close = get_closing_prices(tickers=list(self.tickers), start=start, end=end, ffill=True).reset_index()
        close = close.assign(asset=lambda df: df.ticker.map(self.tickers)).drop(columns=["ticker"])
        frames.append(close.set_index(["date", "asset"]).sort_index())

        # Retrieve FX rates for currencies:
        for curr in sorted(self.currencies):
            fx = get_exchange_rate(base=curr, quote="EUR", start=start, end=end)
            fx = fx.rename(columns={fx.columns[0]: "close"}).assign(asset=curr).reset_index(names="date")
            frames.append(fx.set_index(["date", "asset"]).sort_index())

        # Merge prices onto portfolio:
        merged = pd.concat(frames).sort_index()
        self.portfolio = self.portfolio.join(merged.reindex(self.portfolio.index), how="left")

    def _compute_valuation(self):
        """
        Adds valuation of assets to the ``portfolio`` attribute as column ``"value"``.

        Notes
        -----
        1. ``value`` = ``holding`` * ``close``
        2. Values are expressed in EUR:
           - Currency holdings are converted via EUR exchange rates.
           - Asset prices are converted implicitly via FX-adjusted ``close``.
        """
        self.portfolio["value"] = self.portfolio.holding * self.portfolio.close