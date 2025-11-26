import pandas as pd
from typing import List
from models.group_carpet import GroupCarpet


def _detals_sheet_table(
        group_id= '',
        client_order= '',
        carpet_id= '',
        width= '',
        height= '',
        path_num= '',
        qty_used= '',
        path_length= '',
        original_qty= '',
        qty_rem= '',
    ):
    return ({
        'امر العميل': client_order,
        'رقم القصة': group_id,
        'رقم المسار': path_num,
        'العرض': width,
        'الطول': height,
        'الكمية المستخدمة': qty_used,
        'طول المسار': path_length,
        'الكمية الاصلية' : original_qty,
        'الكمية المتبقية': qty_rem,
        'معرف السجاد': carpet_id,
        })


def _create_group_details_sheet(
    groups: List[GroupCarpet],
) -> pd.DataFrame:
    rows = []
    total_width= 0
    total_height= 0
    total_qty_used= 0
    total_length_ref= 0
    total_qty= 0
    total_qty_rem= 0
    total_path= 0
    group_id= 0
    for g in groups:
        group_id+= 1
        path_num= 0
        for it in g.items:
            path_num+= 1
            if it.repeated:
                ref_lenth= 0
                for rep in it.repeated:
                    ref_lenth+= rep.get('qty') * it.height
                    rows.append(
                        _detals_sheet_table(
                            f'القصة_{group_id}',
                            rep.get('client_order'),
                            it.carpet_id,
                            it.width,
                            it.height,
                            f"المسار_{path_num}",
                            rep.get('qty'),
                            ref_lenth,
                            rep.get("qty_original"),
                            rep.get("qty_rem")
                        )
                    )
            else:
                rows.append(
                    _detals_sheet_table(
                        f'القصة_{group_id}',
                        it.client_order,
                        it.carpet_id,
                        it.width,
                        it.height,
                        f"المسار_{path_num}",
                        it.qty_used,
                        it.length_ref(),
                        it.qty_used + it.qty_rem,
                        it.qty_rem
                    )
                )

            rows.append(
                _detals_sheet_table()
            )
            total_qty+= it.qty_used + it.qty_rem
            total_qty_rem+= it.qty_rem
            total_path += path_num

        total_width+= g.total_width()
        total_height+= g.total_height()
        total_qty_used+= g.total_qty()
        total_length_ref+= g.total_length_ref()

    rows.append(
        _detals_sheet_table()
    )
    rows.append(
        _detals_sheet_table(
            '',
            'المجموع',
            '',
            total_width,
            total_height,
            '',
            total_qty_used,
            total_length_ref,
            total_qty,
            total_qty_rem,
        )
    )

    df = pd.DataFrame(rows)

    return df
