from enum import Enum

class GroupingMode(Enum):
    ALL_COMBINATIONS = "all combinations"
    NO_MAIN_REPEAT = "combinations rep exclude main"

    @classmethod
    def list(cls):
        return [mode.value for mode in cls]