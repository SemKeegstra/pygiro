# External:
import pandas as pd

# Constants:
from ..utils.constants import STATEMENT_COLS, NUMERIC_COLS


def _import_account_statement(path: str) -> pd.DataFrame:
    """
    Retrieves and formats a DEGIRO account statement.

    Notes
    -----
    1. Repairs split rows, parses numeric fields and formats timestamps.

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
    for idx, row in statement[statement.date.isna()].iterrows():
        statement.iloc[idx-1] += row.fillna("")
    statement.dropna(subset=["date"], inplace=True)

    # Date formatting:
    statement.index = pd.to_datetime(statement.pop("date") + " " + statement.pop("time"), format="%d-%m-%Y %H:%M")
    statement.sort_index(inplace=True)

    # Number parsing:
    statement[NUMERIC_COLS] = statement[NUMERIC_COLS].replace({",":"."}, regex=True).astype(float)

    return statement