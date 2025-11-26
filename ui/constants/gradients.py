"""
Gradient color definitions for the application.
This module centralizes all gradient styles to avoid duplication.
"""

# Gradient definitions as a list of tuples: (name, gradient_style)
GRADIENTS = [
    ("أزرق سماوي (افتراضي)", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #E0F7FA)"),
    ("ليلي غامق", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e)"),
    ("غروب الشمس", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #ff9966, stop:1 #ff5e62)"),
    ("غابة خضراء", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #134E5E, stop:1 #71B280)"),
    ("بنفسجي ملكي", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2E3192, stop:1 #1BFFFF)"),
    ("رمادي عصري", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345)")
]

# Helper function to get gradient style by index
def get_gradient_style(index: int) -> str:
    """
    Get gradient style by index.
    Returns default gradient if index is out of range.
    """
    if 0 <= index < len(GRADIENTS):
        return GRADIENTS[index][1]
    return GRADIENTS[0][1]  # Default to first gradient

# Helper function to get gradient name by index
def get_gradient_name(index: int) -> str:
    """
    Get gradient name by index.
    Returns default gradient name if index is out of range.
    """
    if 0 <= index < len(GRADIENTS):
        return GRADIENTS[index][0]
    return GRADIENTS[0][0]  # Default to first gradient
