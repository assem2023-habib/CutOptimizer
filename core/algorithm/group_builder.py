from typing import List
from models.data_models import Carpet, GroupCarpet
from .dp_optimizer import DPOptimizer

def build_groups(
        carpets: List[Carpet],
        min_width: int,
        max_width: int,
        max_partner: int,
        tolerance: int
)-> List[GroupCarpet]:
    optimizer= DPOptimizer(
        carpets= carpets,
        min_width= min_width,
        max_width= max_width,
        tolerance= tolerance,
        max_partner= max_partner
    )

    groups= optimizer.optimize()
    return groups