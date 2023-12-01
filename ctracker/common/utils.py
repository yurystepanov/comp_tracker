import regex as re
from typing import Tuple


def any_str_value_to_float(str_value: str) -> Tuple[float, bool]:
    """ Converts str value to float by removing all non digits characters and dots
        returns tuple(result, success)
        success = True if result was successfully converted
    """
    str_value = re.sub(r"[^\d\.]", "", str_value)
    res, success = 0, True

    try:
        res = float(str_value)
    except ValueError:
        success = False

    return res, success
