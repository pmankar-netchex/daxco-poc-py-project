def parse_currency_value(val):
    """
    Convert a currency string to a float value.

    Args:
        val (str or any): The value to parse, typically a string representing a currency amount (e.g., "$1,234.56").

    Returns:
        float: The parsed float value. Returns 0.0 if parsing fails or input is empty/invalid.

    Example:
        >>> parse_currency_value("$1,234.56")
        1234.56
    """
    try:
        # Remove dollar sign, commas, and whitespace
        s = str(val).replace('$', '').replace(',', '').strip()
        return float(s) if s else 0.0
    except Exception:
        # Return 0.0 if conversion fails
        return 0.0 