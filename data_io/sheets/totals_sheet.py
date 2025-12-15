import pandas as pd
from typing import List, Optional

from pandas._libs.groupby import group_max
from models.carpet import Carpet
from models.group_carpet import GroupCarpet


def _create_totals_sheet(
    original_groups: Optional[List[Carpet]],
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    max_width: Optional[int] = None,
) -> pd.DataFrame:
    total_order_quantity = _calculate_total_order_quantity(original_groups, groups)
    total_remaining_quantity = _calculate_total_remaining_quantity(remaining)
    total_produced_quantity = _calculate_total_produced_quantity(groups)
    total_waste_quantity = _calculate_total_waste_quantity(groups, max_width)

    waste_percentage = (
        f"{round((total_waste_quantity / total_produced_quantity) * 100, 2):.2f}%"
        if total_produced_quantity > 0 and total_waste_quantity > 0
        else "0.00%"
    )

    totals_row = {
        "": "",
        "كمية الطلبية": total_order_quantity,
        "الكمية المتبقية": total_remaining_quantity,
        "الكمية المنتجة": total_produced_quantity,
        "كمية الهادر": total_waste_quantity,
        "نسبة الهادر": waste_percentage,
    }

    return pd.DataFrame([totals_row])


def _calculate_total_order_quantity(
    original_groups: Optional[List[Carpet]],
    groups: List[GroupCarpet],
) -> int:
    total = 0
    if original_groups:
        for carpet in original_groups:
            total += carpet.area() * getattr(carpet, "qty", 0)
        return total

    for group in groups or []:
        for item in group.items:
            units = getattr(item, "qty_used", 0) + getattr(item, "qty_rem", 0)
            total += (item.width * item.height) * units

    return total


def _calculate_total_remaining_quantity(remaining: List[Carpet]) -> int:
    total = 0
    for carpet in remaining or []:
        if carpet.repeated:
            for rep in carpet.repeated:
                qty = int(rep.get("qty_rem", 0) or 0)
                if qty > 0:
                    total += carpet.area() * qty
        else:
            if carpet.rem_qty > 0:
                total += carpet.area() * carpet.rem_qty
    return total


def _calculate_total_produced_quantity(groups: List[GroupCarpet]) -> int:
    total = 0
    for group in groups or []:
        for item in group.items:
            total += item.area()
    return total


def _calculate_total_waste_quantity(
    groups: List[GroupCarpet],
    max_width: Optional[int],
) -> int:
    if not groups or max_width is None:
        return 0

    total_waste = 0

    for group in groups:
        if not group.items:
            continue

        group_max_length = group.max_length_ref()
        sum_path_loss = 0

        for item in group.items:
            sum_path_loss += (group_max_length - item.length_ref()) * item.width

        sum_path_loss += (max_width - group.total_width()) * group_max_length
        total_waste += sum_path_loss

    return total_waste
