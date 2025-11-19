from enum import Enum

class GroupingMode(Enum):
    ALL_COMBINATIONS = "all combinations"
    NO_MAIN_REPEAT = "combinations rep exclude main"
    START_FROM_BIGGEST_QTY_WITH_NO_MAIN_REPEAT= "from big_qty rep exclude main"
    START_FROM_BIGGEST_QTY= "start from bigest qty"

    @classmethod
    def list(cls):
        return [mode.value for mode in cls]