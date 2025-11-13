from enum import Enum

class GroupingMode(Enum):
    SAME_GROUP_FIRST = "same carpet group first"
    SAME_GROUP_LAST = "same carpet group last"

    @classmethod
    def list(cls):
        return [mode.value for mode in cls]