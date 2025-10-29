import pandas as pd
from typing import List, Dict, Optional, Tuple
from models.data_models import Carpet, GroupCarpet, CarpetUsed

# =============================================================================
# DATA CREATION FUNCTIONS - دوال إنشاء البيانات للصفحات
# =============================================================================

def _create_group_details_sheet(
    groups: List[GroupCarpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None
) -> pd.DataFrame:
    rows = []
    for g in groups:
        for it in g.items:
            rows.append({
                'رقم المجموعة': f'المجموعة_{g.group_id}',
                'معرف السجاد': it.carpet_id,
                'العرض': it.width,
                'الطول': it.height,
                'الكمية المستخدمة': it.qty_used,
                'الطول الاجمالي للسجادة': it.length_ref(),
                    'الكمية الاصلية' : it.original_qty,
                'الكمية المتبقية': it.qty_rem
            })

    # إنشاء DataFrame
    df = pd.DataFrame(rows)

    return df


def _create_group_summary_sheet(
    groups: List[GroupCarpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None
) -> pd.DataFrame:
    """إنشاء ورقة ملخص المجموعات مع الإحصائيات."""
    summary = []
    # المجموعات الأصلية
    for g in groups:
        types_count = len(g.items)
        area = sum(it.width * it.length * it.used_qty for it in g.items)
        summary.append({
            'رقم المجموعة': f'المجموعة_{g.group_id}',
                'العرض الإجمالي': g.total_width(),
                'أقصى ارتفاع': g.total_height(),
                'المساحة الإجمالية': g.total_area(),
                'الكمية المستخدمة الكلية': g.total_qty(),
                'عدد أنواع السجاد': len(g.items),
        })

    # إنشاء DataFrame
    df = pd.DataFrame(summary)

    return df


def _create_remaining_sheet(remaining: List[Carpet]) -> pd.DataFrame:
    """إنشاء ورقة السجاد المتبقي مع تجميع العناصر المتطابقة."""
    # تجميع العناصر المتطابقة حسب المعرف والعرض والطول
    aggregated = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height)
            aggregated[key] = aggregated.get(key, 0) + int(r.rem_qty)

    # إنشاء صفوف البيانات
    rem_rows = []
    for (rid, w, h), q in aggregated.items():
        rem_rows.append({
            'معرف السجادة': rid,
            'العرض': w,
            'الطول': h,
            'الكمية المتبقية': q,
        })

    df = pd.DataFrame(rem_rows)

    # تجميع البيانات وتنظيمها
    if not df.empty:
        df = df.sort_values(by=['الارتفاع', 'العرض', 'معرف السجادة'])

    return df


def _create_totals_sheet(
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None
) -> pd.DataFrame:
    """إنشاء ورقة الإجماليات مع مقارنة قبل وبعد العملية."""
    # حساب الإجمالي قبل العملية
    total_original = 0
    all_groups = [groups]
    if remainder_groups:
        all_groups.append(remainder_groups)
    if enhanced_remainder_groups:
        all_groups.append(enhanced_remainder_groups)

    for group_list in all_groups:
        for g in group_list:
            for it in g.items:
                original_qty = it.qty_used + it.qty_rem
                total_original += it.width * it.height * original_qty
    total_used = 0
    for group_list in all_groups:
        for g in group_list:
            total_used += g.total_area()

    total_remaining = 0
    for r in remaining:
        total_remaining += r.width * r.height * r.rem_qty

    return pd.DataFrame([{
        "الإجمالي الأصلي (cm²)": total_original,
        "المستهلك (cm²)": total_used,
        "المتبقي (cm²)": total_remaining,
        "نسبة الاستهلاك (%)": round(total_used / total_original * 100, 2) if total_original > 0 else 0
    }])


def _create_audit_sheet(
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None,
    originals: Optional[List[Carpet]] = None
) -> pd.DataFrame:
    """إنشاء ورقة تدقيق الكميات."""
    # تجميع المستخدم من جميع المجموعات
    used_totals: Dict[tuple, int] = {}

    def _accumulate_used(from_groups: Optional[List[GroupCarpet]]):
        if from_groups:
            for g in from_groups:
                for it in g.items:
                    key = (it.carpet_id, it.width, it.height)
                    used_totals[key] = used_totals.get(key, 0) + int(it.qty_used)

    _accumulate_used(groups)
    _accumulate_used(remainder_groups)
    _accumulate_used(enhanced_remainder_groups)

    # تجميع المتبقي
    remaining_totals: Dict[tuple, int] = {}
    for r in remaining:
        if r.rem_qty > 0:
            key = (r.id, r.width, r.height)
            remaining_totals[key] = remaining_totals.get(key, 0) + int(r.rem_qty)

    # تجميع الأصلي
    original_totals: Dict[tuple, int] = {}
    if originals is not None:
        for r in originals:
            key = (r.id, r.width, r.height)
            original_totals[key] = original_totals.get(key, 0) + int(r.qty)
    else:
        # استنتاج الأصلي من المستخدم + المتبقي
        all_keys = set(list(used_totals.keys()) + list(remaining_totals.keys()))
        for k in all_keys:
            original_totals[k] = used_totals.get(k, 0) + remaining_totals.get(k, 0)

    # بناء جدول التدقيق
    audit_rows = []
    all_keys = set(list(original_totals.keys()) + list(used_totals.keys()) + list(remaining_totals.keys()))
    for (rid, w, h) in sorted(all_keys, key=lambda x: (x[0] if x[0] is not None else -1, x[1], x[2])):
        orig = int(original_totals.get((rid, w, h), 0))
        used = int(used_totals.get((rid, w, h), 0))
        rem = int(remaining_totals.get((rid, w, h), 0))
        diff = used + rem - orig
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

    # إنشاء DataFrame
    df = pd.DataFrame(audit_rows)

    return df


def _create_enhanced_stats_sheet(enhanced_remainder_groups: Optional[List[GroupCarpet]]) -> pd.DataFrame:
    """إنشاء ورقة إحصائيات المجموعات الإضافية."""
    if not enhanced_remainder_groups:
        # إنشاء DataFrame فارغ مع رؤوس الأعمدة حتى لو لم تكن هناك بيانات
        return pd.DataFrame(columns=[
            'رقم المجموعة', 'عدد العناصر', 'العرض الإجمالي', 
            'أقصى ارتفاع', 'المساحة الإجمالية'
        ])

    enhanced_stats = []
    for g in enhanced_remainder_groups:
        enhanced_stats.append({
            'رقم المجموعة': f'المجموعة_{g.group_id}',
            'عدد العناصر': len(g.items),
            'العرض الإجمالي': g.total_width(),
            'أقصى ارتفاع': g.total_height(),
            'المساحة الإجمالية': g.total_area(),
        })

    # إنشاء DataFrame
    df = pd.DataFrame(enhanced_stats)

    return df


def _create_ui_summary_sheet(
    groups: List[GroupCarpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None
) -> pd.DataFrame:
    """إنشاء ورقة ملخص الواجهة مع تصنيف المجموعات."""
    ui_rows = []
    # المجموعات الأصلية
    for g in groups:
        ui_rows.append({
            'عدد الأنواع': len(g.items),
            'الطول المرجعي': g.ref_length(),
            'العرض الإجمالي': g.total_width(),
            'رقم المجموعة': f'المجموعة_{g.id}',
        })

    # إنشاء DataFrame
    df = pd.DataFrame(ui_rows)

    return df


# def _create_optimized_remainder_groups_sheet(
#     remaining: List[Carpet],
#     min_width: Optional[int] = None,
#     max_width: Optional[int] = None,
#     tolerance_length: Optional[int] = None
# ) -> pd.DataFrame:


def _create_suggestions_sheet(
    remaining: List[Carpet],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None
) -> pd.DataFrame:
    """
    إنشاء ورقة اقتراحات تشكيل المجموعات من المتبقيات.
    
    ملاحظة: هذه دالة مبسطة - يمكن تطويرها لاحقاً بخوارزميات أكثر تعقيداً
    """
  
    eff_min_width = 370 if min_width is None else int(min_width)
    eff_max_width = 400 if max_width is None else int(max_width)
    eff_tolerance = 0 if tolerance_length is None else int(tolerance_length)

    rows = []
    
    # تحليل بسيط للمتبقيات
    if remaining:
        remaining_with_qty = [r for r in remaining if r.rem_qty > 0]
        
        if remaining_with_qty:
            for i, r in enumerate(remaining_with_qty[:10]):  # أول 10 عناصر
                rows.append({
                    'رقم الاقتراح': i + 1,
                    'معرف السجادة': r.id,
                    'العرض': r.width,
                    'الارتفاع': r.height,
                    'الكمية المتبقية': r.rem_qty,
                    'الاقتراح': f'يمكن دمجها مع سجادات عرض {eff_max_width - r.width} أو أقل',
                    'ملاحظات': 'تحتاج تحليل يدوي'
                })

    if not rows:
        rows.append({
            'رقم الاقتراح': 0,
            'معرف السجادة': 'N/A',
            'العرض': 0,
            'الارتفاع': 0,
            'الكمية المتبقية': 0,
            'الاقتراح': 'لا توجد متبقيات كافية للاقتراحات',
            'ملاحظات': 'N/A'
        })

    return pd.DataFrame(rows)


def _create_size_suggestions_sheet(
    remaining: List[Carpet],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None
) -> pd.DataFrame:
    """
    إنشاء ورقة اقتراحات المقاسات المطلوبة للبواقي.
    """
    data = []

    if remaining:
        for rect in remaining:
            if rect.rem_qty > 0:
                data.append({
                    'المقاس الحالي': f"{rect.width}x{rect.height}",
                    'الكمية': rect.rem_qty,
                    'الطول الإجمالي': rect.height * rect.rem_qty,
                    'نوع الاقتراح': 'تحليل',
                    'العرض المطلوب': f"{min_width}-{max_width}" if min_width and max_width else 'غير محدد',
                    'الاقتراح': f"مقاس متاح للتحليل",
                    'الكفاءة': 'متوسطة'
                })

    # إذا لم توجد بيانات، إنشاء صف واحد فقط
    if not data:
        data.append({
            'المقاس الحالي': 'لا توجد بيانات',
            'الكمية': 0,
            'الطول الإجمالي': 0,
            'نوع الاقتراح': 'غير متاح',
            'العرض المطلوب': 'غير متاح',
            'الاقتراح': 'لا توجد اقتراحات',
            'الكفاءة': 'غير متاح'
        })

    # إنشاء DataFrame
    df = pd.DataFrame(data)

    return df
