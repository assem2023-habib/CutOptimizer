from typing import Tuple, Optional
from models.data_models import Rectangle 

def validate_config(min_w: int, max_w: int, tol: int) ->Tuple[bool, Optional[str]]:
    """
    This function validates the configuration settings for grouping.

    Args:
        min_w (int): The minimum allowed total width.
        max_w (int): The maximum allowed total width.
        tol (int): The allowed tolerance for total length.

    Returns:
        Tuple[bool, Optional[str]]:
            - True, None  → if the configuration is valid.
            - False, "Error message" → if there is an issue.
    """
    if min_w <= 0 or max_w <= 0:
        return False, "min_width and max_width must be positive."
    if min_w >max_w:
        return False, "min_width cannot be greater than max_width."
    if tol < 0:
        return False, "tolerance must be non-negative."
    return True, None

def validate_carpets(carpets: list[Rectangle])->list[str]:
    # Define a function `validate_carpets` that takes a list of Rectangle objects 
    # and returns a list of error messages (strings) if any validation rules are broken.
    errors = []
    for c in carpets:
        if c.width <= 0:
            errors.append(f"Carpet id {c.id}: width <= 0")
        if c.length <=0:
            errors.append(f"Carpet id {c.id}: length <= 0")
        if c.qty < 0:
            errors.append(f"Carpet id {c.id}: qty < 0")
    return errors