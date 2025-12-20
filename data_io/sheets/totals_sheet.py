import pandas as pd
from typing import List, Optional

from pandas._libs.groupby import group_max
from models.carpet import Carpet
from models.group_carpet import GroupCarpet
from core.config.config_manager import ConfigManager


def _create_totals_sheet(
    original_groups: Optional[List[Carpet]],
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    max_width: Optional[int] = None,
) -> pd.DataFrame:
    pair_mode = str(ConfigManager.get_value("pair_mode")).upper()
    multiplier = 2 if pair_mode == "A" else 1
    
    total_order_quantity = _calculate_total_order_quantity(original_groups)
    total_remaining_quantity = _calculate_total_remaining_quantity(remaining) * multiplier
    total_produced_quantity = _calculate_total_produced_quantity(total_order_quantity, total_remaining_quantity)
    total_waste_quantity = _calculate_total_waste_quantity(groups, max_width) * multiplier

    waste_percentage = (
        f"{round((total_waste_quantity / total_produced_quantity) * 100, 2):.2f}%"
        if total_produced_quantity > 0 and total_waste_quantity > 0
        else "0.00%"
    )

    totals_row = {
        "": "",
        "كمية الطلبية (cm²)": total_order_quantity,
        "الكمية المتبقية (cm²)": total_remaining_quantity,
        "الكمية المنتجة (cm²)": total_produced_quantity,
        "كمية الهادر (cm²)": total_waste_quantity,
        "نسبة الهادر": waste_percentage,
    }

    return pd.DataFrame([totals_row])


def _calculate_total_order_quantity(
    original_groups: Optional[List[Carpet]],
) -> int:
    total = 0
    if original_groups:
        for carpet in original_groups:
            qty_original = getattr(carpet, "qty_original_before_pair_mode", getattr(carpet, "qty", 0))
            total += carpet.area() * qty_original
        return total

    return total


def _calculate_total_remaining_quantity(remaining: List[Carpet]) -> int:
    total = 0
    for carpet in remaining or []:
        qty_rem= carpet.rem_qty
        if qty_rem > 0:
            total += carpet.area() * qty_rem
                
    return total


def _calculate_total_produced_quantity(total_quantity, remainig) -> int:
    total = total_quantity - remainig  
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
        waste_with= (max_width - group.total_width()) * group_max_length
        for item in group.items:
            sum_path_loss += (group_max_length - item.length_ref()) * item.width
            
        sum_path_loss += waste_with
        total_waste += sum_path_loss

    return total_waste
