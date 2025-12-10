import pandas as pd
from typing import List, Optional
from models.carpet import Carpet
from models.group_carpet import GroupCarpet


def _create_remaining_suggestion_sheet(remaining: List[Carpet], min_width, max_width, tolerance) -> pd.DataFrame:
    aggregated = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height, r.client_order)
            aggregated[key] = aggregated.get(key, 0) + int(r.rem_qty)

    rem_rows = []
    total_width = 0
    total_hieght = 0
    total_rem_qty = 0
    total_missing_min_width= 0
    total_missing_max_width= 0
    total_min_height_ref= 0
    total_max_height_ref= 0
    for (rid, w, h, co), q in aggregated.items():
        rem_rows.append({
            'معرف السجادة': rid,
            'أمر العميل': co,
            'العرض': w,
            'الطول': h,
            'الكمية المتبقية': q,
            'اقل عرض مجموعة': min_width - w,
            'أعلى عرض مجموعة': max_width - w,
            'اقل طول مرجعي': h * q - tolerance,
            'اكبر طول مرجعي': h * q + tolerance,
        })
        total_width+= w
        total_hieght+= h
        total_rem_qty+= q
        total_missing_min_width+= min_width - w
        total_missing_max_width+= max_width - w
        total_min_height_ref+=  h * q - tolerance
        total_max_height_ref+=  h * q + tolerance

    rem_rows.append({
        'معرف السجادة': '',
        'أمر العميل': '',
        'العرض': '',
        'الطول': '',
        'الكمية المتبقية': '',
        'اقل عرض مجموعة': '',
        'أعلى عرض مجموعة': '',
        'اقل طول مرجعي': '',
        'اكبر طول مرجعي': '',
    })

    rem_rows.append({
        'معرف السجادة': "المجموع",
        'أمر العميل': '',
        'العرض': total_width,
        'الطول': total_hieght,
        'الكمية المتبقية': total_rem_qty,
        'اقل عرض مجموعة': total_missing_min_width,
        'أعلى عرض مجموعة': total_missing_max_width,
        'اقل طول مرجعي': total_min_height_ref,
        'اكبر طول مرجعي': total_max_height_ref,
    })

    df = pd.DataFrame(rem_rows)

    return df


def _create_enhanset_remaining_suggestion_sheet(
        suggested_groups: Optional[List[List[GroupCarpet]]], 
        min_width, 
        max_width, 
        tolerance
        ) -> pd.DataFrame:
   
    rem_rows = []
    suggested_id= 0 
    total_width= 0
    total_height= 0
    total_carpet_used= 0
    total_carpet_rem= 0
    total_local_min_width= 0
    total_local_max_width= 0
    total_local_min_tolerance= 0
    total_local_max_tolerance= 0

    for carpte_groups in suggested_groups:
        suggested_id+= 1 
        for group in carpte_groups:
            local_min_width= min_width - group.total_width() if min_width - group.total_width() > 0 else 0
            local_max_width= max_width - group.total_width()
            local_min_tolerance= max(i.length_ref() for i in group.items) - tolerance
            local_max_tolerance= max(i.length_ref() for i in group.items) + tolerance

            total_width+= group.total_width()
            total_height+= group.total_height()
            total_carpet_used+= group.total_qty()
            total_carpet_rem+= group.total_rem_qty()
            total_local_min_width+= local_min_width
            total_local_max_width+= local_max_width
            total_local_min_tolerance+= local_min_tolerance
            total_local_max_tolerance+= local_max_tolerance

            for item in group.items:
                if item.repeated:
                    ref_lenth= 0
                    for rep in item.repeated:
                        ref_lenth+= rep.get('qty') * item.height
                        rem_rows.append({
                                'الاقتراح':f"الاقتراح_{suggested_id}",
                                'معرف السجادة': item.carpet_id,
                                'أمر العميل': rep.get('client_order'),
                                'العرض': item.width,
                                'الطول': item.height,
                                'الكمية المستخدمة':rep.get('qty'),
                                'الكمية المتبقية': rep.get('qty_rem'),
                                'اقل عرض مجموعة مسموح': local_min_width,
                                'أكبر عرض مجموعة مسموح': local_max_width,
                                'اقل طول مسار': local_min_tolerance,
                                'اكبر طول مسار': local_max_tolerance,
                            }
                        )
                else:
                    rem_rows.append({
                        'الاقتراح':f"الاقتراح_{suggested_id}",
                        'معرف السجادة': item.carpet_id,
                        'أمر العميل': item.client_order,
                        'العرض': item.width,
                        'الطول': item.height,
                        'الكمية المستخدمة':item.qty_used,
                        'الكمية المتبقية': item.qty_rem,
                        'اقل عرض مجموعة مسموح': local_min_width,
                        'أكبر عرض مجموعة مسموح': local_max_width,
                        'اقل طول مسار': local_min_tolerance,
                        'اكبر طول مسار': local_max_tolerance,
                    })
        rem_rows.append({
            'الاقتراح':'',
            'معرف السجادة': '',
            'أمر العميل': '',
            'العرض': '',
            'الطول': '',
            'الكمية المستخدمة': '',
            'الكمية المتبقية': '',
            'اقل عرض مجموعة مسموح': '',
            'أكبر عرض مجموعة مسموح': '',
            'اقل طول مسار': '',
            'اكبر طول مسار': '',
        })

    rem_rows.append({
        'الاقتراح':'المجموع',
        'معرف السجادة': '',
        'أمر العميل': '',
        'العرض': total_width,
        'الطول': total_height,
        'الكمية المستخدمة': total_carpet_used,
        'الكمية المتبقية': total_carpet_rem,
        'اقل عرض مجموعة مسموح': total_local_min_width,
        'أكبر عرض مجموعة مسموح': total_local_max_width,
        'اقل طول مسار': total_local_min_tolerance,
        'اكبر طول مسار': total_local_max_tolerance,
    })


    df = pd.DataFrame(rem_rows)

    return df


def _create_pair_complement_sheet(remaining: List[Carpet], min_width: int, max_width: int) -> pd.DataFrame:
    aggregated = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height, r.client_order)
            aggregated[key] = aggregated.get(key, 0) + int(r.rem_qty)

    rows = []
    total_original_width = 0
    total_complement_width = 0
    total_qty = 0

    for (rid, w, h, co), q in aggregated.items():
        comp_w = max(0, max_width - w)
        total_w = w + comp_w
        valid = (min_width <= total_w <= max_width)
        rows.append({
            'معرف السجادة': rid,
            'أمر العميل': co,
            'العرض الأصلي': w,
            'الطول الأصلي': h,
            'الكمية المتبقية': q,
            'عرض مكمل مقترح': comp_w,
            'طول مكمل مقترح': h,
            'كمية مكمل مقترحة': q,
            'العرض الإجمالي بعد الإكمال': total_w,
            'صالح ضمن الحدود': 'نعم' if valid else 'لا',
        })
        total_original_width += w
        total_complement_width += comp_w
        total_qty += q

    rows.append({
        'معرف السجادة': '',
        'أمر العميل': '',
        'العرض الأصلي': '',
        'الطول الأصلي': '',
        'الكمية المتبقية': '',
        'عرض مكمل مقترح': '',
        'طول مكمل مقترح': '',
        'كمية مكمل مقترحة': '',
        'العرض الإجمالي بعد الإكمال': '',
        'صالح ضمن الحدود': '',
    })

    rows.append({
        'معرف السجادة': 'المجموع',
        'أمر العميل': '',
        'العرض الأصلي': total_original_width,
        'الطول الأصلي': '',
        'الكمية المتبقية': total_qty,
        'عرض مكمل مقترح': total_complement_width,
        'طول مكمل مقترح': '',
        'كمية مكمل مقترحة': total_qty,
        'العرض الإجمالي بعد الإكمال': total_original_width + total_complement_width,
        'صالح ضمن الحدود': '',
    })

    return pd.DataFrame(rows)
