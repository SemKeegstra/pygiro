# External:
import pandas as pd

# Constants:
from ..utils.constants import *

def _classify_line(line: pd.Series) -> str:
    """
    Classifies a single account statement line based on its description.

    Parameters
    ----------
    line : str
        Line from the account statement.

    Returns
    -------
    str
        Line type identifier (e.g. buy, sell, deposit, cost).
    """
    # Initialize:
    description = str(line.description).lower()

    # Classification:
    if any(txt in description for txt in DEPOSITS):
        return "deposit"
    elif any(txt in description for txt in WITHDRAWALS):
        return "withdrawal"
    elif any(txt in description for txt in FX):
        return "fx"
    elif any(txt in description for txt in COSTS):
        return "cost"
    elif any(txt in description for txt in DIVIDENDS):
        return "dividend"
    elif any(txt in description for txt in INTEREST):
        return "interest"
    elif any(txt in description for txt in REBATE):
        return "rebate"
    elif any(txt in description for txt in SELL):
        return "sell"
    elif any(txt in description for txt in BUY):
        return "buy"

    return "other"


def _import_account_statement(path: str) -> pd.DataFrame:
    """
    Retrieves and formats a DEGIRO account statement.

    Notes
    -----
    1. Repairs split rows, parses numeric fields, formats timestamps, and classifies line types.

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
    statement.index = pd.to_datetime(statement.pop("date") + " " + statement.pop("time"), format="%d-%m-%Y %H:%M")
    statement.sort_index(inplace=True)

    # Number parsing:
    statement[NUMERIC_COLS] = statement[NUMERIC_COLS].replace({",":"."}, regex=True).astype(float)

    # Type classification:
    statement["type"] = pd.Categorical(statement.apply(_classify_line, axis=1), categories=LINE_TYPES)

    return statement