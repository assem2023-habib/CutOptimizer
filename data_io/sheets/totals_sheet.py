import pandas as pd
from typing import List
from models.carpet import Carpet
from models.group_carpet import GroupCarpet


def _create_totals_sheet(
    original_groups: List[Carpet],
    groups: List[GroupCarpet],
    remaining: List[Carpet],
) -> pd.DataFrame:
    total_original = 0
    if original_groups:
        for carpet in original_groups:
            total_original += carpet.area() * carpet.qty
    else:
        for group in groups:
            for carpet in group.items:
                total_original += carpet.area() * (carpet.qty_used + carpet.qty_rem)

    total_remaining = 0
    for carpet in remaining:
        total_remaining += carpet.area() * carpet.rem_qty

    total_used = total_original - total_remaining

    rem_rows = [{
        "":"",
        "الإجمالي الأصلي (cm²)": total_original,
        "المستهلك (cm²)": total_used,
        "المتبقي (cm²)": total_remaining,
        "نسبة الاستهلاك (%)": (total_used / total_original * 100) if total_original > 0 else 0
    }]

    df = pd.DataFrame(rem_rows)

    return df
