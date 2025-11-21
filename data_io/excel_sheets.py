import pandas as pd
from typing import List, Dict, Optional, Tuple
from models.carpet import Carpet
from models.group_carpet import GroupCarpet

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
    total_path= 0
    group_id= 0
    for g in groups:
        group_id+= 1
        path_num= 0
        for it in g.items:
            path_num+= 1
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


def _create_group_summary_sheet(
    groups: List[GroupCarpet],
) -> pd.DataFrame:
    """إنشاء ورقة ملخص المجموعات مع الإحصائيات."""
    summary = []
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
                g.total_area(),
                g.total_qty(),
                types_count,
                g.total_area() / 10000,
            )
        )
        total_width+= g.total_width()
        total_height+= g.max_height()
        total_area+= g.total_area()
        items_count+= types_count
        total_qty_used+= g.total_qty()
        total_area_div+= g.total_area() / 10000

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


def _create_remaining_sheet(remaining: List[Carpet]) -> pd.DataFrame:
    aggregated = {}
    for r in remaining:
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
                    key = (it.carpet_id, it.width, it.height, it.client_order)
                    used_totals[key] = used_totals.get(key, 0) + int(it.qty_used)

    _accumulate_used(groups)

    remaining_totals: Dict[tuple, int] = {}
    for r in remaining:
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
        orig = int(original_totals.get((rid, w, h), 0))
        used = int(used_totals.get((rid, w, h), 0))
        rem = int(remaining_totals.get((rid, w, h), 0))
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
    group_id= 0

    for g in groups:
        group_id+= 1
        sumPathLoss= 0

        for item in g.items:
            sumPathLoss += g.max_length_ref() - item.length_ref()

        wasteWidth = max_width - g.total_width()
        pathLoss = g.max_length_ref() - g.min_length_ref()

        summary.append({
            'رقم القصة': f'القصة_{group_id}',
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
        'المساحة الإجمالية': total_area,
        'الكمية المستخدمة الكلية': total_qty_used,
        'عدد أنواع السجاد': carpet_count,
         'المساحة الإجمالية_2' : total_area_2,
        })

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

def _waste_sheet_table(
        group_id= '',
        total_width= '',
        waste_width= '',
        max_length_ref= '',
        result_1= '',
        path_loss= '',
        result_2= '',
        sum_path_loss= '',
    ):
    return ({
            'رقم القصة': group_id,
            'العرض الإجمالي': total_width,
            'الهادر في العرض':  waste_width,
            'اطول مسار': max_length_ref,
            'نتيجة الضرب': result_1,
            'الهادر في المسارات': path_loss,
            'نتيجة الجمع': result_2,
            'مجموع هادرالمسارات في المجموعة': sum_path_loss,
        })