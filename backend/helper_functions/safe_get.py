import pandas as pd

def safe_get(row, col):
    """
    Safely retrieve a value from a pandas Series or dictionary, returning an empty string if the value is missing or NaN.

    Args:
        row (dict or pandas.Series): The row to retrieve the value from.
        col (str): The column/key to look up.

    Returns:
        any: The value from the row for the given column, or an empty string if missing or NaN.

    Example:
        >>> safe_get({'a': 1, 'b': None}, 'b')
        ''
    """
    val = row.get(col, '')  # Get the value for the column, default to '' if not found
    return '' if pd.isna(val) else val  # Return '' if value is NaN, else return the value 