# Standard:
from collections import defaultdict

# External:
import pandas as pd

# Constants:
from ..utils.mappings import LINE_TYPES
from ..utils.constants import STATEMENT_COLS, NUMERIC_COLS

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


def import_account_statement(path: str) -> pd.DataFrame:
    """
    Retrieves and formats a DEGIRO account statement.

    Notes
    -----
    1. Repairs split rows, parses numeric fields, formats timestamps, classifies line types
       and extracts shares & prices from the description.

    Parameters
    ----------
    path : str
        Location of the DEGIRO account statement.

    Returns
    -------
    pd.DataFrame
        Cleaned account statement indexed by transaction time.
    """
    # Initialize:
    statement = pd.read_csv(path, sep=",", engine="c").set_axis(STATEMENT_COLS, axis=1)

    # Handle extended rows:
    for idx, line in statement[statement.date.isna()].iterrows():
        statement.iloc[idx-1] += line.fillna("")
    statement.dropna(subset=["date"], inplace=True)

    # Date formatting:
    statement.index = pd.to_datetime(statement.date + " " + statement.pop("time"), format="%d-%m-%Y %H:%M")
    statement.date = pd.to_datetime(statement.date, format="%d-%m-%Y")
    statement.sort_index(inplace=True)

    # Number parsing:
    statement[NUMERIC_COLS] = statement[NUMERIC_COLS].replace({",":"."}, regex=True).astype(float)

    # Type classification:
    statement["type"] = pd.Categorical(statement.apply(_classify_line, axis=1), categories=LINE_TYPES.keys())

    # Share extraction:
    statement['shares'] = statement.description.str.extract(r"(?:Koop|Verkoop)\s+(\d+)", expand=False).astype(float)
    statement.loc[statement["type"] == "sell", "shares"] *= -1

    # Price extraction:
    statement['price'] = statement.description.str.extract(r"@\s*([\d.,]+)", expand=False).str.replace(",", ".").astype(float)

    return statement[statement.type != 'other']

def get_portfolio(statement: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a daily end-of-day portfolio overview from a DEGIRO account statement.

    Notes
    -----
    1. The portfolio is defined as a multi-index DataFrame (date, asset).

    Parameters
    ----------
    statement : pd.DataFrame
        DEGIRO account statement.

    Returns
    -------
    pd.DataFrame
        Daily portfolio.
    """
    # Initialize:
    portfolio = dict()
    holdings = defaultdict(float)

    # Construct portfolio:
    for date, frame in statement.groupby("date"):
        for _ , line in frame.iterrows():
            # Adjust balance
            holdings[line.currency] += line.amount
            # Adjust shares (if needed):
            if line.type in {"buy", "sell"}:
                holdings[line.ISIN] += line.shares
        portfolio[date] = holdings.copy()

    # Multi-Index format:
    portfolio = pd.DataFrame.from_records(((d, a, v) for d, h in portfolio.items() for a, v in h.items()),
                                          columns=["date", "asset", "holding"]).set_index(["date", "asset"])

    # Daily frequency:
    period = pd.date_range(statement.date.iloc[0], pd.Timestamp.today(), freq="D", name="date")
    portfolio = portfolio.unstack(level=1).reindex(period).ffill().stack(future_stack=True)

    return portfolio[portfolio.holding != 0.0].dropna()
