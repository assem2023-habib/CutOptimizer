import copy
from typing import List
from models.group_carpet import GroupCarpet
from models.carpet import Carpet
from core.grouping_algorithm import build_groups
from core.Enums.grouping_mode import GroupingMode
from core.Enums.sort_type import SortType


def generate_suggestions(
        remaining: List[Carpet],
        min_width: int,
        max_width: int,
        tolerance: int,
        selected_mode: GroupingMode ,
        selected_sort_type: SortType ,
        path_length_limit: int = 0,
        step: int= 10,    
    )->List[List[GroupCarpet]]:

    suggestions: List[List[GroupCarpet]]= []

    # Filter for carpets that actually have remaining quantity
    active_remaining = [c for c in remaining if c.rem_qty > 0]
    
    if not active_remaining:
        return []

    min_remaining_width= min(c.width for c in active_remaining)
    work_copy= [copy.deepcopy(c) for c in remaining]

    current_min= min_width
    current_max= max_width

    while current_max > min_remaining_width:
        carpets_for_run= [copy.deepcopy(c) for c in work_copy]

        groups= build_groups(
            carpets= carpets_for_run,
            min_width= current_min,
            max_width= current_max,
            max_partner= 9,
            tolerance= tolerance,
            path_length_limit= path_length_limit,
            selected_mode= selected_mode,
            selected_sort_type= selected_sort_type,
        )
        if groups and not groups in suggestions:
            suggestions.append(groups)

        current_min -= step
        current_max -= step

        if current_min < 0:
            current_min = 0
    return suggestions