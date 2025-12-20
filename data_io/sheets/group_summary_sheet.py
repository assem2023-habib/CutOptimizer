import pandas as pd
from typing import List
from models.group_carpet import GroupCarpet
from core.config.config_manager import ConfigManager

def _summary_sheet_table(
        group_id= '',
        total_width= '',
        path_count= '',
        max_height= '',
        total_area= '',
        total_qty_used= '',
        carpet_count= '',
        total_area_2= '',
    ):
    return ({
        'رقم القصة': group_id,
        'العرض الإجمالي': total_width,
        'عدد المسارات': path_count,
        'أقصى ارتفاع': max_height,
        'المساحة الإجمالية (cm²)': total_area,
        'الكمية المستخدمة الكلية': total_qty_used,
        'عدد أنواع السجاد': carpet_count,
         'إجمالي المساحة (cm²)': total_area_2,
        })


def _create_group_summary_sheet(
    groups: List[GroupCarpet],
) -> pd.DataFrame:
    """إنشاء ورقة ملخص المجموعات مع الإحصائيات."""
    summary = []
    
    pair_mode = str(ConfigManager.get_value("pair_mode", "B")).upper()
    multiplier = 2 if pair_mode == "B" else 1
    
    total_width= 0
    total_height= 0
    total_area= 0
    items_count= 0
    total_qty_used= 0
    total_area_div= 0
    group_id= 0
    for g in groups:
        group_id+= 1
        types_count = len(g.items)
        summary.append(
            _summary_sheet_table(
                f'القصة_{group_id}',
                g.total_width(),
                len(g.items),
                g.max_height(),
                g.total_area() * multiplier,
                g.total_qty() * multiplier,
                types_count,
                g.total_area() * multiplier,
            )
        )
        total_width+= g.total_width()
        total_height+= g.max_height()
        total_area+= g.total_area() * multiplier
        items_count+= types_count
        total_qty_used+= g.total_qty() * multiplier
        total_area_div+= g.total_area() * multiplier

    summary.append(_summary_sheet_table())
    
    summary.append(
        _summary_sheet_table(
            "المجموع",
            total_width,
            len(groups),
            total_height,
            total_area,
            total_qty_used,
            items_count,
            total_area_div
        )
    )

    df = pd.DataFrame(summary)

    return df
