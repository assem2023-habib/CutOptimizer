"""
وحدة كتابة ملفات Excel
=====================

هذه الوحدة تحتوي على الدوال المسؤولة عن كتابة النتائج إلى ملفات Excel
بشكل منظم ومفصل مع إحصائيات شاملة.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name


def write_output_excel(
    path: str,
    groups: List[Group],
    remaining: List[Rectangle],
    remainder_groups: Optional[List[Group]] = None,
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None,
    originals: Optional[List[Rectangle]] = None,
    enhanced_remainder_groups: Optional[List[Group]] = None
) -> None:
    """
    كتابة النتائج إلى ملف Excel مع تقارير مفصلة.
    
    هذه الدالة تنشئ ملف Excel يحتوي على عدة أوراق:
    - تفاصيل المجموعات: تفاصيل كل مجموعة مع تصنيفها
    - ملخص المجموعات: إحصائيات شاملة للمجموعات
    - السجاد المتبقي: العناصر التي لم يتم استخدامها
    - ملخص الواجهة: ملخص مبسط للعرض
    - الإجماليات: مقارنة قبل وبعد العملية
    - اقتراحات تشكيل مجموعات: اقتراحات لتجميع البواقي
    - إحصائيات المجموعات الإضافية: إحصائيات المجموعات المحسنة
    - تدقيق الكميات: فحص دقيق للكميات
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel المراد كتابته
    groups : List[Group]
        المجموعات الأصلية
    remaining : List[Rectangle]
        العناصر المتبقية
    remainder_groups : Optional[List[Group]]
        مجموعات البواقي العادية
    min_width : Optional[int]
        الحد الأدنى للعرض
    max_width : Optional[int]
        الحد الأقصى للعرض
    tolerance_length : Optional[int]
        حدود السماحية للطول
    originals : Optional[List[Rectangle]]
        العناصر الأصلية للتدقيق
    enhanced_remainder_groups : Optional[List[Group]]
        المجموعات الإضافية المحسنة من البواقي
        
    أمثلة:
    -------
    >>> write_output_excel(
    >>>     "results.xlsx",
    >>>     groups=original_groups,
    >>>     remaining=remaining_items,
    >>>     enhanced_remainder_groups=enhanced_groups
    >>> )
    """
    # إنشاء ورقة تفاصيل المجموعات
    df1 = _create_group_details_sheet(groups, remainder_groups, enhanced_remainder_groups)
    
    # إنشاء ورقة ملخص المجموعات
    df2 = _create_group_summary_sheet(groups, remainder_groups, enhanced_remainder_groups)
    
    # إنشاء ورقة السجاد المتبقي
    df3 = _create_remaining_sheet(remaining)
    
    # إنشاء ورقة ملخص الواجهة
    df4 = _create_ui_summary_sheet(groups, remainder_groups, enhanced_remainder_groups)
    
    # إنشاء ورقة الإجماليات
    totals_df = _create_totals_sheet(groups, remaining, remainder_groups, enhanced_remainder_groups)
    
    # إنشاء ورقة اقتراحات التشكيل
    df_sugg = _create_suggestions_sheet(remaining, min_width, max_width, tolerance_length)
    
    # إنشاء ورقة إحصائيات المجموعات الإضافية
    df_enhanced_stats = _create_enhanced_stats_sheet(enhanced_remainder_groups)
    
    # إنشاء ورقة التدقيق
    df_audit = _create_audit_sheet(groups, remaining, remainder_groups, enhanced_remainder_groups, originals)
    
    # كتابة جميع الأوراق إلى الملف
    _write_all_sheets_to_excel(
        path, df1, df2, df3, df4, totals_df, df_sugg, df_enhanced_stats, df_audit
    )


def _create_group_details_sheet(
    groups: List[Group],
    remainder_groups: Optional[List[Group]],
    enhanced_remainder_groups: Optional[List[Group]]
) -> pd.DataFrame:
    """إنشاء ورقة تفاصيل المجموعات مع تصنيفها."""
    rows = []
    
    # المجموعات الأصلية
    for g in groups:
        for it in g.items:
            rows.append({
                'رقم المجموعة': f'المجموعة_{g.id}',
                'نوع المجموعة': 'أصلية',
                'معرف السجاد': it.rect_id,
                'العرض': it.width,
                'الطول': it.length,
                'الكمية المستخدمة': it.used_qty,
                'الطول الاجمالي للسجادة': it.length * it.used_qty,
                'الكمية الأصلية': it.original_qty
            })
    
    # مجموعات البواقي العادية
    if remainder_groups:
        for g in remainder_groups:
            for it in g.items:
                rows.append({
                    'رقم المجموعة': f'المجموعة_{g.id}',
                    'نوع المجموعة': 'بواقي عادية',
                    'معرف السجاد': it.rect_id,
                    'العرض': it.width,
                    'الطول': it.length,
                    'الكمية المستخدمة': it.used_qty,
                    'الطول الاجمالي للسجادة': it.length * it.used_qty,
                    'الكمية الأصلية': it.original_qty
                })
    
    # المجموعات الإضافية المحسنة
    if enhanced_remainder_groups:
        for g in enhanced_remainder_groups:
            for it in g.items:
                rows.append({
                    'رقم المجموعة': f'المجموعة_{g.id}',
                    'نوع المجموعة': 'بواقي محسنة',
                    'معرف السجاد': it.rect_id,
                    'العرض': it.width,
                    'الطول': it.length,
                    'الكمية المستخدمة': it.used_qty,
                    'الطول الاجمالي للسجادة': it.length * it.used_qty,
                    'الكمية الأصلية': it.original_qty
                })
    
    return pd.DataFrame(rows)


def _create_group_summary_sheet(
    groups: List[Group],
    remainder_groups: Optional[List[Group]],
    enhanced_remainder_groups: Optional[List[Group]]
) -> pd.DataFrame:
    """إنشاء ورقة ملخص المجموعات مع الإحصائيات."""
    summary = []
    
    # المجموعات الأصلية
    for g in groups:
        types_count = len(g.items)
        area = sum(it.width * it.length * it.used_qty for it in g.items)
        summary.append({
            'رقم المجموعة': f'المجموعة_{g.id}',
            'نوع المجموعة': 'أصلية',
            'العرض الإجمالي': g.total_width(),
            'الطول الإجمالي المرجعي (التقريبي)': g.ref_length(),
            'المساحة الإجمالية': area,
            'عدد أنواع السجاد': types_count,
        })
    
    # مجموعات البواقي العادية
    if remainder_groups:
        for g in remainder_groups:
            types_count = len(g.items)
            area = sum(it.width * it.length * it.used_qty for it in g.items)
            summary.append({
                'رقم المجموعة': f'المجموعة_{g.id}',
                'نوع المجموعة': 'بواقي عادية',
                'العرض الإجمالي': g.total_width(),
                'الطول الإجمالي المرجعي (التقريبي)': g.ref_length(),
                'المساحة الإجمالية': area,
                'عدد أنواع السجاد': types_count,
            })
    
    # المجموعات الإضافية المحسنة
    if enhanced_remainder_groups:
        for g in enhanced_remainder_groups:
            types_count = len(g.items)
            area = sum(it.width * it.length * it.used_qty for it in g.items)
            summary.append({
                'رقم المجموعة': f'المجموعة_{g.id}',
                'نوع المجموعة': 'بواقي محسنة',
                'العرض الإجمالي': g.total_width(),
                'الطول الإجمالي المرجعي (التقريبي)': g.ref_length(),
                'المساحة الإجمالية': area,
                'عدد أنواع السجاد': types_count,
            })
    
    return pd.DataFrame(summary)


def _create_remaining_sheet(remaining: List[Rectangle]) -> pd.DataFrame:
    """إنشاء ورقة السجاد المتبقي مع تجميع العناصر المتطابقة."""
    # تجميع العناصر المتطابقة حسب المعرف والعرض والطول
    aggregated = {}
    for r in remaining:
        key = (r.id, r.width, r.length)
        aggregated[key] = aggregated.get(key, 0) + int(r.qty)
    
    # إنشاء صفوف البيانات
    rem_rows = []
    for (rid, w, l), q in aggregated.items():
        rem_rows.append({
            'معرف السجادة': rid,
            'العرض': w,
            'الطول': l,
            'الكمية المتبقية': q,
        })
    
    df = pd.DataFrame(rem_rows)
    
    # تجميع البيانات وتنظيمها
    if not df.empty:
        df = (
            df
            .groupby(['معرف السجادة', 'العرض', 'الطول'], as_index=False)['الكمية المتبقية']
            .sum()
            .sort_values(by=['معرف السجادة', 'العرض', 'الطول'])
        )
    
    # إضافة عمود الملاحظات
    if 'ملاحظة' not in df.columns:
        df['ملاحظة'] = ''
    
    return df


def _create_ui_summary_sheet(
    groups: List[Group],
    remainder_groups: Optional[List[Group]],
    enhanced_remainder_groups: Optional[List[Group]]
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
            'نوع المجموعة': 'أصلية'
        })
    
    # مجموعات البواقي العادية
    if remainder_groups:
        for g in remainder_groups:
            ui_rows.append({
                'عدد الأنواع': len(g.items),
                'الطول المرجعي': g.ref_length(),
                'العرض الإجمالي': g.total_width(),
                'رقم المجموعة': f'المجموعة_{g.id}',
                'نوع المجموعة': 'بواقي عادية'
            })
    
    # المجموعات الإضافية المحسنة
    if enhanced_remainder_groups:
        for g in enhanced_remainder_groups:
            ui_rows.append({
                'عدد الأنواع': len(g.items),
                'الطول المرجعي': g.ref_length(),
                'العرض الإجمالي': g.total_width(),
                'رقم المجموعة': f'المجموعة_{g.id}',
                'نوع المجموعة': 'بواقي محسنة'
            })
    
    return pd.DataFrame(ui_rows)


def _create_totals_sheet(
    groups: List[Group],
    remaining: List[Rectangle],
    remainder_groups: Optional[List[Group]],
    enhanced_remainder_groups: Optional[List[Group]]
) -> pd.DataFrame:
    """إنشاء ورقة الإجماليات مع مقارنة قبل وبعد العملية."""
    # حساب الإجمالي قبل العملية
    total_before = 0
    for g in groups:
        for it in g.items:
            total_before += it.width * it.length * it.original_qty
    
    # حساب الإجمالي بعد العملية (المتبقي فقط)
    total_after = 0
    for r in remaining:
        total_after += r.width * r.length * r.qty
    
    return pd.DataFrame([{
        "الإجمالي قبل العملية": total_before,
        "الإجمالي بعد العملية": total_after,
        "المستهلك": total_before - total_after
    }])


def _create_suggestions_sheet(
    remaining: List[Rectangle],
    min_width: Optional[int],
    max_width: Optional[int],
    tolerance_length: Optional[int]
) -> pd.DataFrame:
    """إنشاء ورقة اقتراحات تشكيل المجموعات."""
    from .excel_io import generate_partner_suggestions
    
    # استخدام القيم الافتراضية إذا لم يتم تحديدها
    eff_min_width = 370 if min_width is None else int(min_width)
    eff_max_width = 400 if max_width is None else int(max_width)
    eff_tolerance = 100 if tolerance_length is None else int(tolerance_length)
    
    # توليد الاقتراحات
    suggestions = generate_partner_suggestions(remaining, eff_min_width, eff_max_width, eff_tolerance)
    return pd.DataFrame(suggestions)


def _create_enhanced_stats_sheet(enhanced_remainder_groups: Optional[List[Group]]) -> pd.DataFrame:
    """إنشاء ورقة إحصائيات المجموعات الإضافية."""
    if not enhanced_remainder_groups:
        return pd.DataFrame()
    
    enhanced_stats = []
    for g in enhanced_remainder_groups:
        enhanced_stats.append({
            'رقم المجموعة': f'المجموعة_{g.id}',
            'عدد العناصر': len(g.items),
            'العرض الإجمالي': g.total_width(),
            'الطول المرجعي': g.ref_length(),
            'المساحة الإجمالية': sum(it.width * it.length * it.used_qty for it in g.items),
            'نوع المجموعة': 'بواقي محسنة'
        })
    
    return pd.DataFrame(enhanced_stats)


def _create_audit_sheet(
    groups: List[Group],
    remaining: List[Rectangle],
    remainder_groups: Optional[List[Group]],
    enhanced_remainder_groups: Optional[List[Group]],
    originals: Optional[List[Rectangle]]
) -> pd.DataFrame:
    """إنشاء ورقة تدقيق الكميات."""
    # تجميع المستخدم من جميع المجموعات
    used_totals: Dict[tuple, int] = {}
    
    def _accumulate_used(from_groups: List[Group]):
        for g in from_groups or []:
            for it in g.items:
                key = (it.rect_id, it.width, it.length)
                used_totals[key] = used_totals.get(key, 0) + int(it.used_qty)
    
    _accumulate_used(groups)
    _accumulate_used(remainder_groups or [])
    _accumulate_used(enhanced_remainder_groups or [])
    
    # تجميع المتبقي
    remaining_totals: Dict[tuple, int] = {}
    for r in remaining:
        key = (r.id, r.width, r.length)
        remaining_totals[key] = remaining_totals.get(key, 0) + int(r.qty)
    
    # تجميع الأصلي
    original_totals: Dict[tuple, int] = {}
    if originals is not None:
        for r in originals:
            key = (r.id, r.width, r.length)
            original_totals[key] = original_totals.get(key, 0) + int(r.qty)
    else:
        # استنتاج الأصلي من المستخدم + المتبقي
        all_keys = set(list(used_totals.keys()) + list(remaining_totals.keys()))
        for k in all_keys:
            original_totals[k] = used_totals.get(k, 0) + remaining_totals.get(k, 0)
    
    # بناء جدول التدقيق
    audit_rows = []
    all_keys = set(list(original_totals.keys()) + list(used_totals.keys()) + list(remaining_totals.keys()))
    for (rid, w, l) in sorted(all_keys, key=lambda x: (x[0] if x[0] is not None else -1, x[1], x[2])):
        orig = int(original_totals.get((rid, w, l), 0))
        used = int(used_totals.get((rid, w, l), 0))
        rem = int(remaining_totals.get((rid, w, l), 0))
        diff = used + rem - orig
        audit_rows.append({
            'معرف السجادة': rid,
            'العرض': w,
            'الطول': l,
            'الكمية الأصلية': orig,
            'الكمية المستخدمة': used,
            'الكمية المتبقية': rem,
            'فارق (المستخدم+المتبقي-الأصلي)': diff,
            'مطابق؟': 'نعم' if diff == 0 else 'لا'
        })
    
    return pd.DataFrame(audit_rows)


def _write_all_sheets_to_excel(
    path: str,
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df3: pd.DataFrame,
    df4: pd.DataFrame,
    totals_df: pd.DataFrame,
    df_sugg: pd.DataFrame,
    df_enhanced_stats: pd.DataFrame,
    df_audit: pd.DataFrame
) -> None:
    """كتابة جميع الأوراق إلى ملف Excel."""
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        # ورقة تفاصيل المجموعات
        df1.to_excel(writer, sheet_name='تفاصيل المجموعات', index=False)
        _append_totals_row(writer, 'تفاصيل المجموعات', df1)
        
        # ورقة ملخص المجموعات
        df2.to_excel(writer, sheet_name='ملخص المجموعات', index=False)
        _append_totals_row(writer, 'ملخص المجموعات', df2)
        
        # ورقة السجاد المتبقي
        df3.to_excel(writer, sheet_name='السجاد المتبقي', index=False)
        _append_totals_row(writer, 'السجاد المتبقي', df3)
        
        # ورقة ملخص الواجهة
        df4.to_excel(writer, sheet_name='ملخص الواجهة', index=False)
        _append_totals_row(writer, 'ملخص الواجهة', df4)
        
        # ورقة الإجماليات
        totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)
        
        # ورقة اقتراحات تشكيل المجموعات
        df_sugg.to_excel(writer, sheet_name='اقتراحات تشكيل مجموعات', index=False)
        
        # ورقة إحصائيات المجموعات الإضافية
        if not df_enhanced_stats.empty:
            df_enhanced_stats.to_excel(writer, sheet_name='إحصائيات المجموعات الإضافية', index=False)
            _append_totals_row(writer, 'إحصائيات المجموعات الإضافية', df_enhanced_stats)
        
        # ورقة التدقيق
        if not df_audit.empty:
            df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)
            _append_totals_row(writer, 'تدقيق الكميات', df_audit)


def _append_totals_row(writer, sheet_name: str, df: pd.DataFrame) -> None:
    """
    إضافة صف الإجماليات في نهاية الورقة.
    
    هذه الدالة تضيف صف "المجموع" في نهاية الورقة مع حساب مجموع
    الأعمدة الرقمية فقط.
    """
    ws = writer.sheets[sheet_name]
    nrows, ncols = df.shape
    totals_row_idx = nrows + 1  # فهرس الصف التالي للبيانات
    
    # كتابة تسمية "المجموع" في العمود الأول
    ws.write(totals_row_idx, 0, 'المجموع')
    
    # محاولة وضع التسمية في عمود "ملاحظة" إن وُجد
    try:
        if 'ملاحظة' in df.columns:
            note_col_idx = df.columns.get_loc('ملاحظة')
            ws.write(totals_row_idx, note_col_idx, 'المجموع')
    except Exception:
        pass
    
    # حساب المجموع للأعمدة الرقمية
    for col_idx, col_name in enumerate(df.columns):
        if is_numeric_dtype(df[col_name]):
            col_letter = xl_col_to_name(col_idx)
            # نطاق البيانات من الصف 2 إلى الصف nrows+1 في Excel (1-based)
            formula = f"=SUM({col_letter}2:{col_letter}{nrows+1})"
            ws.write_formula(totals_row_idx, col_idx, formula)
