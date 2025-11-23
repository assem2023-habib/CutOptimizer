import pandas as pd
from typing import List
from models.carpet import Carpet


def _remaining_sheet_table(
        carpet_id= '',
        client_order= '',
        width= '',
        height= '',
        qty_rem= '',
    ):
    return ({
            'معرف السجادة': carpet_id,
            'أمر العيل': client_order,
            'العرض': width,
            'الطول': height,
            'الكمية المتبقية': qty_rem,
        })


def _create_remaining_sheet(remaining: List[Carpet]) -> pd.DataFrame:
    aggregated = {}
    for r in remaining:
        if r.rem_qty > 0:
            if r.repeated:
                for rep in r.repeated:
                    if rep.get("qty_rem") > 0:
                        key = (rep.get("id"), r.width, r.height, rep.get("client_order"))
                        aggregated[key] = aggregated.get(key, 0) + int(rep.get("qty_rem"))
            else:
                if r.rem_qty > 0:
                    key = (r.id, r.width, r.height, r.client_order)
                    aggregated[key] = aggregated.get(key, 0) + int(r.rem_qty)

    rem_rows = []
    total_width = 0
    total_hieght = 0
    total_rem_qty = 0
    for (rid, w, h, co), q in aggregated.items():
        rem_rows.append(
            _remaining_sheet_table(
                rid,
                co,
                w,
                h,
                q
            )
        )
        total_width+= w
        total_hieght+= h
        total_rem_qty+= q

    rem_rows.append(_remaining_sheet_table())

    rem_rows.append(
        _remaining_sheet_table(
            'المجموع',
            '',
            total_width,
            total_hieght,
            total_rem_qty
        )
    )

    df = pd.DataFrame(rem_rows)

    return df
