import pandas as pd
from typing import List, Dict, Optional
from models.carpet import Carpet
from models.group_carpet import GroupCarpet


def _audit_sheet_table(
    carpet_id= '',
    client_order= '',
    width= '',
    height= '',
    original_qty= '',
    used_qty= '',
    rem_qty= '',
    difference= '',
    is_difference= '',
    ):
    return ({
            'معرف السجادة': carpet_id,
            'أمر العميل': client_order,
            'العرض': width,
            'الارتفاع': height,
            'الكمية الأصلية': original_qty,
            'الكمية المستخدمة': used_qty,
            'الكمية المتبقية': rem_qty,
            'فارق (المستخدم+المتبقي-الأصلي)': difference,
            'مطابق؟': is_difference,    
        })


def _create_audit_sheet(
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    originals: Optional[List[Carpet]] = None
) -> pd.DataFrame:
    used_totals: Dict[tuple, int] = {}

    def _accumulate_used(from_groups: Optional[List[GroupCarpet]]):
        if from_groups:
            for g in from_groups:
                for it in g.items:
                    if it.repeated:
                        for rep in it.repeated:
                            key = (rep.get("id"), it.width, it.height, rep.get("client_order"))
                            used_totals[key] = used_totals.get(key, 0) + int(rep.get("qty"))
                    else:
                        key = (it.carpet_id, it.width, it.height, it.client_order)
                        used_totals[key] = used_totals.get(key, 0) + int(it.qty_used)

    _accumulate_used(groups)

    remaining_totals: Dict[tuple, int] = {}
    for r in remaining:
        if r.repeated:
            for rep in r.repeated:
                if rep.get("qty_rem") > 0:
                    key = (rep.get("id"), r.width, r.height, rep.get("client_order"))
                    remaining_totals[key] = remaining_totals.get(key, 0) + int(rep.get("qty_rem"))
        else:
            if r.rem_qty > 0:
                key = (r.id, r.width, r.height, r.client_order)
                remaining_totals[key] = remaining_totals.get(key, 0) + int(r.rem_qty)

    original_totals: Dict[tuple, int] = {}
    if originals is not None:
        for r in originals:
            key = (r.id, r.width, r.height, r.client_order)
            original_totals[key] = original_totals.get(key, 0) + int(r.qty)
    else:
        all_keys = set(list(used_totals.keys()) + list(remaining_totals.keys()))
        for k in all_keys:
            original_totals[k] = used_totals.get(k, 0) + remaining_totals.get(k, 0)

    audit_rows = []
    all_keys = set(list(original_totals.keys()) + list(used_totals.keys()) + list(remaining_totals.keys()))

    total_width= 0
    total_height= 0
    total_original_qty= 0
    total_used_qty= 0
    total_rem_qty= 0
    total_diff_qty= 0

    for (rid, w, h, co) in sorted(all_keys, key=lambda x: (x[0] if x[0] is not None else -1, x[1], x[2])):
        key = (rid, w, h, co)
        orig = int(original_totals.get(key, 0))
        used = int(used_totals.get(key, 0))
        rem  = int(remaining_totals.get(key, 0))
        diff = used + rem - orig

        total_width+= w
        total_height+= h
        total_original_qty+= orig
        total_used_qty+= used
        total_rem_qty+= rem
        total_diff_qty+= diff

        audit_rows.append(
            _audit_sheet_table(
                rid,
                co,
                w,
                h,
                orig,
                used,
                rem,
                diff,
                '✅ نعم' if diff == 0 else '❌ لا'
            )
        )

    audit_rows.append(_audit_sheet_table())

    is_same= '❌ لا'
    if total_original_qty == total_used_qty + total_rem_qty:
        is_same= '✅ نعم'

    audit_rows.append(
        _audit_sheet_table(
            'المجموع',
            '',
            total_width,
            total_height,
            total_original_qty,
            total_used_qty,
            total_rem_qty,
            total_diff_qty,
            is_same
        )
    )
    df = pd.DataFrame(audit_rows)

    return df
