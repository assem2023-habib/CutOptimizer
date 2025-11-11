import pandas as pd
from typing import List, Dict, Optional, Tuple
from models.data_models import Carpet, GroupCarpet, CarpetUsed

# =============================================================================
# DATA CREATION FUNCTIONS - دوال إنشاء البيانات للصفحات
# =============================================================================

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
    for g in groups:
        for it in g.items:
            rows.append({
                'رقم القصة': f'القصة_{g.group_id}',
                'معرف السجاد': it.carpet_id,
                'العرض': it.width,
                'الطول': it.height,
                'الكمية المستخدمة': it.qty_used,
                'الطول الاجمالي للسجادة': it.length_ref(),
                'الكمية الاصلية' : it.qty_used + it.qty_rem,
                'الكمية المتبقية': it.qty_rem
            })
            total_qty+= it.qty_used + it.qty_rem
            total_qty_rem+= it.qty_rem

        total_width+= g.total_width()
        total_height+= g.total_height()
        total_qty_used+= g.total_qty()
        total_length_ref+= g.total_length_ref()

    rows.append({
        'رقم القصة': '',
        'معرف السجاد': '',
        'العرض': '',
        'الطول': '',
        'الكمية المستخدمة': '',
        'الطول الاجمالي للسجادة': '',
        'الكمية الاصلية' : '',
        'الكمية المتبقية': ''
    })
    
    rows.append({
        'رقم القصة': 'المجموع  ',
        'معرف السجاد': '',
        'العرض': total_width,
        'الطول': total_height,
        'الكمية المستخدمة': total_qty_used,
        'الطول الاجمالي للسجادة': total_length_ref,
        'الكمية الاصلية' : total_qty,
        'الكمية المتبقية': total_qty_rem
    })

    df = pd.DataFrame(rows)

    return df


def _create_group_summary_sheet(
    groups: List[GroupCarpet],
) -> pd.DataFrame:
    """إنشاء ورقة ملخص المجموعات مع الإحصائيات."""
    summary = []
    total_width= 0
    total_hieght= 0
    total_area= 0
    items_count= 0
    total_qty_used= 0
    total_area_div= 0
    for g in groups:
        types_count = len(g.items)
        summary.append({
            'رقم القصة': f'القصة_{g.group_id}',
            'العرض الإجمالي': g.total_width(),
            'أقصى ارتفاع': g.max_height(),
            'المساحة الإجمالية': g.total_area(),
            'الكمية المستخدمة الكلية': g.total_qty(),
            'عدد أنواع السجاد': types_count,
             'المساحة الإجمالية_2' :g.total_area() / 10000,
        })
        total_width+= g.total_width()
        total_hieght+= g.max_height()
        total_area+= g.total_area()
        items_count+= types_count
        total_qty_used+= g.total_qty()
        total_area_div+= g.total_area() / 10000

    summary.append({
        'رقم القصة': '',
        'العرض الإجمالي': '',
        'أقصى ارتفاع': '',
        'المساحة الإجمالية': '',
        'الكمية المستخدمة الكلية': '',
        'عدد أنواع السجاد': '',
        'المساحة الإجمالية_2':'',
    })
    
    summary.append({
        'رقم القصة': "المجموع",
        'العرض الإجمالي': total_width,
        'أقصى ارتفاع': total_hieght,
        'المساحة الإجمالية': total_area,
        'الكمية المستخدمة الكلية': total_qty_used,
        'عدد أنواع السجاد': items_count,
         'المساحة الإجمالية_2':total_area_div,
    })

    df = pd.DataFrame(summary)

    return df


def _create_remaining_sheet(remaining: List[Carpet]) -> pd.DataFrame:
    aggregated = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height)
            aggregated[key] = aggregated.get(key, 0) + int(r.rem_qty)

    rem_rows = []
    total_width = 0
    total_hieght = 0
    total_rem_qty = 0
    for (rid, w, h), q in aggregated.items():
        rem_rows.append({
            'معرف السجادة': rid,
            'العرض': w,
            'الطول': h,
            'الكمية المتبقية': q,
        })
        total_width+= w
        total_hieght+= h
        total_rem_qty+= q

    rem_rows.append({
        'معرف السجادة': '',
        'العرض': '',
        'الطول': '',
        'الكمية المتبقية': '',
    })

    rem_rows.append({
        'معرف السجادة': "المجموع",
        'العرض': total_width,
        'الطول': total_hieght,
        'الكمية المتبقية': total_rem_qty,
    })

    df = pd.DataFrame(rem_rows)

    return df


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
                    key = (it.carpet_id, it.width, it.height)
                    used_totals[key] = used_totals.get(key, 0) + int(it.qty_used)

    _accumulate_used(groups)

    remaining_totals: Dict[tuple, int] = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height)
            remaining_totals[key] = remaining_totals.get(key, 0) + int(r.rem_qty)

    original_totals: Dict[tuple, int] = {}
    if originals is not None:
        for r in originals:
            key = (r.id, r.width, r.height)
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
    tota_diff_qty= 0

    for (rid, w, h) in sorted(all_keys, key=lambda x: (x[0] if x[0] is not None else -1, x[1], x[2])):
        orig = int(original_totals.get((rid, w, h), 0))
        used = int(used_totals.get((rid, w, h), 0))
        rem = int(remaining_totals.get((rid, w, h), 0))
        diff = used + rem - orig

        total_width+= w
        total_height+= h
        total_original_qty+= orig
        total_used_qty+= used
        total_rem_qty+= rem
        tota_diff_qty+= diff

        audit_rows.append({
            'معرف السجادة': rid,
            'العرض': w,
            'الارتفاع': h,
            'الكمية الأصلية': orig,
            'الكمية المستخدمة': used,
            'الكمية المتبقية': rem,
            'فارق (المستخدم+المتبقي-الأصلي)': diff,
            'مطابق؟': '✅ نعم' if diff == 0 else '❌ لا'    
        })

    audit_rows.append({
        'معرف السجادة': '',
        'العرض': '',
        'الارتفاع': '',
        'الكمية الأصلية': '',
        'الكمية المستخدمة': '',
        'الكمية المتبقية': '',
        'فارق (المستخدم+المتبقي-الأصلي)': '',
        'مطابق؟': '' 
    })

    is_same= '❌ لا'
    if total_original_qty == total_used_qty + total_rem_qty:
        is_same= '✅ نعم'
    audit_rows.append({
        'معرف السجادة': "المجموع",
        'العرض': total_width,
        'الارتفاع': total_height,
        'الكمية الأصلية': total_original_qty,
        'الكمية المستخدمة': total_used_qty,
        'الكمية المتبقية': total_rem_qty,
        'فارق (المستخدم+المتبقي-الأصلي)': tota_diff_qty,
        'مطابق؟': is_same 
    })
    df = pd.DataFrame(audit_rows)

    return df


def _generate_waste_sheet(
    groups: List[GroupCarpet],
    max_width: int,
) -> pd.DataFrame:
    
    summary = []
    total_width= 0
    total_wasteWidth= 0
    total_pathLoss= 0
    total_maxPath= 0
    total_waste_maxPath= 0
    total_sumPathLoss= 0
    total_result= 0

    for g in groups:
        sumPathLoss= 0

        for item in g.items:
            sumPathLoss += g.max_length_ref() - item.length_ref()

        wasteWidth = max_width - g.total_width()
        pathLoss = g.max_length_ref() - g.min_length_ref()

        summary.append({
            'رقم القصة': f'القصة_{g.group_id}',
            'العرض الإجمالي': g.total_width(),
            'الهادر في العرض':  wasteWidth,
            'اطول مسار': g.max_length_ref(),
            'نتيجة الضرب': wasteWidth * g.max_length_ref(),
            'الهادر في المسارات': pathLoss,
            'نتيجة الجمع': wasteWidth * g.max_length_ref() + pathLoss,
            'مجموع هادرالمسارات في المجموعة': sumPathLoss,
        })

        total_width+= g.total_width()
        total_wasteWidth+= wasteWidth
        total_waste_maxPath+= wasteWidth * g.max_length_ref()
        total_pathLoss+= pathLoss
        total_sumPathLoss+= sumPathLoss
        total_result+= pathLoss * wasteWidth
        total_maxPath+= g.max_length_ref()

    summary.append({
        'رقم القصة': '',
        'العرض الإجمالي': '',
        'الهادر في العرض':  '',
        'اطول مسار': '',
        'نتيجة الضرب': '',
        'الهادر في المسارات': '',
        'نتيجة الجمع':'',
        'مجموع هادرالمسارات في المجموعة': '',
    })
    
    summary.append({
        'رقم القصة': "المجموع",
        'العرض الإجمالي': total_width,
        'الهادر في العرض':  total_wasteWidth,
        'اطول مسار': total_maxPath,
        'نتيجة الضرب': total_waste_maxPath,
        'الهادر في المسارات': total_pathLoss,
        'نتيجة الجمع': total_result,
        'مجموع هادرالمسارات في المجموعة': total_sumPathLoss,
    })

    df = pd.DataFrame(summary)

    return df
