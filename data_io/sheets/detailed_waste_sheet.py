import pandas as pd
from typing import List
from models.group_carpet import GroupCarpet


def _detailed_waste_sheet_table(
        group_id= '',
        total_area= '',
        waste_value= '',
        waste_percentage= '',
    ):
    return ({
            'رقم القصة': group_id,
            'المساحة الكلية للعناصر': total_area,
            'قيمة الهادر': waste_value,
            'نسبة الهادر (%)': waste_percentage,
        })


def _generate_detailed_waste_sheet(
    groups: List[GroupCarpet],
) -> pd.DataFrame:
    
    summary = []
    
    total_groups_area = 0
    total_groups_waste = 0

    for g in groups:
        # 1. Calculate Total Area (Sum of L * W * Qty for all items)
        # item.area() returns width * height * qty_used
        group_total_area = g.total_area()
        
        # 2. Calculate Waste Value
        # Sum of (Max Path - Path Length) * Element Width
        # item.length_ref() returns height * qty_used (which is the path length)
        max_path = g.max_length_ref()
        group_waste_value = 0
        
        for item in g.items:
            path_diff = max_path - item.length_ref()
            path_waste = path_diff * item.width
            group_waste_value += path_waste
            
        # 3. Calculate Waste Percentage
        # (Waste Value / Total Area) * 100
        if group_total_area > 0:
            waste_pct = (group_waste_value / group_total_area) * 100
        else:
            waste_pct = 0

        summary.append(
            _detailed_waste_sheet_table(
                f'القصة_{g.group_id}',
                group_total_area,
                group_waste_value,
                round(waste_pct, 2)
            )
        )
        
        total_groups_area += group_total_area
        total_groups_waste += group_waste_value

    # Empty row
    summary.append(_detailed_waste_sheet_table())
    
    # Totals row
    total_pct = 0
    if total_groups_area > 0:
        total_pct = (total_groups_waste / total_groups_area) * 100
        
    summary.append(
        _detailed_waste_sheet_table(
            "المجموع",
            total_groups_area,
            total_groups_waste,
            round(total_pct, 2)
        )
    )

    df = pd.DataFrame(summary)

    return df
