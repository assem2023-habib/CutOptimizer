from enum import Enum

class SortType(Enum):
    SORT_BY_QUANTITY = "sort carpet by quantity"
    SORT_BY_WIDTH = "sort carpet by width"
    SORT_BY_HEIGHT= "sort carpet by height"

    @staticmethod
    def list():
        return [e.value for e in SortType]