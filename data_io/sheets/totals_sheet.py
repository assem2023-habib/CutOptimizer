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
    raw_originals: Optional[List[Carpet]] = None,
) -> pd.DataFrame:
    pair_mode = str(ConfigManager.get_value("pair_mode")).upper()
    multiplier = 2 if pair_mode == "A" else 1
    
    # 1. حساب كمية الطلبية من الملف الأصلي الخام
    total_order_quantity = _calculate_total_order_quantity_raw(raw_originals)
    
    # 2. حساب الكمية المنتجة من المجموعات
    total_produced_quantity_raw = _calculate_total_produced_quantity_from_groups(groups)
    total_produced_quantity = total_produced_quantity_raw * multiplier
    
    # 3. حساب الكمية المتبقية
    # إذا كان زوجي: كمية الطلبية - (الكمية المنتجة * 2)
    # إذا كان فردي: كمية الطلبية - الكمية المنتجة
    total_remaining_quantity = total_order_quantity - total_produced_quantity
    
    # 4. حساب الهادر
    total_waste_quantity_raw = _calculate_total_waste_quantity_from_paths(groups, max_width)
    total_waste_quantity = total_waste_quantity_raw * multiplier

    # 5. حساب نسبة الإنتاج (المتبقي / الكلي * 100) حسب الطلب
    production_percentage = (
        f"{round((total_remaining_quantity / total_order_quantity) * 100, 2):.2f}%"
        if total_order_quantity > 0
        else "0.00%"
    )

    # 6. حساب نسبة الهادر (الهادر / المنتجة * 100)
    waste_percentage = (
        f"{round((total_waste_quantity / total_produced_quantity) * 100, 2):.2f}%"
        if total_produced_quantity > 0
        else "0.00%"
    )

    totals_row = {
        "":"",
        "كمية الطلبية (cm²)": total_order_quantity,
        "الكمية المتبقية (cm²)": total_remaining_quantity,
        "الكمية المنتجة (cm²)": total_produced_quantity,
        "كمية الهادر (cm²)": total_waste_quantity,
        "نسبة الهادر": waste_percentage,
        "نسبة الإنتاج": production_percentage,
    }

    return pd.DataFrame([totals_row])


def _calculate_total_order_quantity_raw(raw_originals: Optional[List[Carpet]]) -> int:
    total = 0
    if raw_originals:
        for carpet in raw_originals:
            # الطول * الكمية * العرض
            total += carpet.height * carpet.qty * carpet.width
    return total


def _calculate_total_produced_quantity_from_groups(groups: List[GroupCarpet]) -> int:
    total_produced = 0
    for group in groups:
        for item in group.items:
            if item.repeated:
                for rep in item.repeated:
                    # الطول * الكمية المستخدمة * العرض
                    qty = int(rep.get("qty", 0))
                    total_produced += item.height * qty * item.width
            else:
                # الطول * الكمية المستخدمة * العرض
                total_produced += item.height * item.qty_used * item.width
    return total_produced


def _calculate_total_waste_quantity_from_paths(
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
        waste_width = (max_width - group.total_width()) * group_max_length
        
        sum_path_loss = 0
        for item in group.items:
            sum_path_loss += (group_max_length - item.length_ref()) * item.width
            
        total_waste += (sum_path_loss + waste_width)

    return total_waste
