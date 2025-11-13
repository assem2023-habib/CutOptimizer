from enum import Enum

class GroupingMode(Enum):
    ALL_COMBINATIONS = "all combinations (allow repetition and main)"
    NO_MAIN_REPEAT = "combinations with repetition (exclude main)"
    # PRIORITY_BY_QTY = "priority by quantity (respect width)"

    @classmethod
    def list(cls):
        return [mode.value for mode in cls]