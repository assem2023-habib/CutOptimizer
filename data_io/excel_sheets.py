"""
وحدة إنشاء صفحات Excel
========================

هذه الوحدة تحتوي على الدوال المسؤولة عن إنشاء البيانات لكل صفحة في ملف Excel
بشكل منظم ومفصل مع إحصائيات شاملة.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem

# =============================================================================
# DATA CREATION FUNCTIONS - دوال إنشاء البيانات للصفحات
# =============================================================================

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

    # إنشاء DataFrame
    df = pd.DataFrame(rows)

    return df


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
            'الكمية المستخدمة الكلية': g.total_used_qty(),
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
                'الكمية المستخدمة الكلية': g.total_used_qty(),
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
                'الكمية المستخدمة الكلية': g.total_used_qty(),
                'عدد أنواع السجاد': types_count,
            })

    # إنشاء DataFrame
    df = pd.DataFrame(summary)

    return df


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

    return df


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

    # إنشاء DataFrame
    df = pd.DataFrame(audit_rows)

    return df


def _create_enhanced_stats_sheet(enhanced_remainder_groups: Optional[List[Group]]) -> pd.DataFrame:
    """إنشاء ورقة إحصائيات المجموعات الإضافية."""
    if not enhanced_remainder_groups:
        # إنشاء DataFrame فارغ مع رؤوس الأعمدة حتى لو لم تكن هناك بيانات
        return pd.DataFrame(columns=['رقم المجموعة', 'عدد العناصر', 'العرض الإجمالي', 'الطول المرجعي', 'المساحة الإجمالية', 'نوع المجموعة'])

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

    # إنشاء DataFrame
    df = pd.DataFrame(enhanced_stats)

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

    # إنشاء DataFrame
    df = pd.DataFrame(ui_rows)

    return df


def _create_optimized_remainder_groups_sheet(
    remaining: List[Rectangle],
    originals: Optional[List[Rectangle]],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None
) -> pd.DataFrame:
    """
    إنشاء ورقة اقتراحات تشكيل المجموعات المحسنة من المتبقيات.

    هذه الدالة تشكل مجموعات من المتبقيات، ثم تقترح عناصر إضافية من الأصليات.

    ملاحظات مهمة:
    - العرض الكلي = مجموع عرض كل نوع (مرة واحدة فقط، بغض النظر عن الكمية)
    - tolerance_ref لكل عنصر = length * qty
    - الشرط: abs(tolerance_ref1 - tolerance_ref2) <= tolerance_length

    المعاملات:
    -----------
    remaining : List[Rectangle]
        العناصر المتبقية.
    originals : Optional[List[Rectangle]]
        العناصر الأصلية للاقتراحات.
    min_width : Optional[int]
        الحد الأدنى للعرض (افتراضي 370).
    max_width : Optional[int]
        الحد الأقصى للعرض (افتراضي 400).
    tolerance_length : Optional[int]
        سماحية الطول (افتراضي 100).

    الإرجاع:
    --------
    pd.DataFrame: الورقة الجديدة.
    """
    # تعيين القيم الافتراضية
    eff_min_width = 370 if min_width is None else int(min_width)
    eff_max_width = 400 if max_width is None else int(max_width)
    eff_tolerance = 100 if tolerance_length is None else int(tolerance_length)

    # نسخ البيانات لتجنب التعديل
    remaining_copy = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining]
    originals_copy = [Rectangle(o.id, o.width, o.length, o.qty) for o in originals] if originals else []

    # قائمة للصفوف
    rows = []
    group_id = 1

    # تجميع المتبقيات حسب المعرف
    remaining_dict: Dict[Tuple[int, int, int], int] = {}
    for r in remaining_copy:
        key = (r.id, r.width, r.length)
        remaining_dict[key] = remaining_dict.get(key, 0) + r.qty

    # خوارزمية تشكيل المجموعات (Greedy مع تحسين)
    iteration = 0
    max_iterations = 1000

    while remaining_dict and iteration < max_iterations:
        iteration += 1
        group_items = []
        current_width = 0
        ref_length_value = None  # الطول المرجعي (من أول عنصر)

        # فرز المتبقيات حسب العرض تنازلياً (لاستغلال العرض أولاً)
        sorted_remaining = sorted(remaining_dict.items(),
                                 key=lambda x: (x[0][1], x[0][2]),
                                 reverse=True)

        # اختيار العنصر الأول (الأعرض)
        first_added = False
        for key, qty in sorted_remaining[:]:
            if qty <= 0:
                if key in remaining_dict:
                    del remaining_dict[key]
                continue

            rect_id, w, l = key

            # التحقق من العرض
            if current_width + w > eff_max_width:
                continue

            if not first_added:
                # أول عنصر: نحاول أخذ أكبر كمية ممكنة
                max_qty = min(qty, (eff_max_width - current_width) // w) if w > 0 else qty

                for test_qty in range(max_qty, 0, -1):
                    ref_length_value = l * test_qty

                    # إضافة العنصر الأول
                    group_items.append((key, test_qty))
                    current_width += w  # العرض يُحسب مرة واحدة فقط
                    remaining_dict[key] -= test_qty
                    if remaining_dict[key] <= 0:
                        del remaining_dict[key]
                    first_added = True
                    break

                if first_added:
                    break

        if not first_added or ref_length_value is None:
            break

        # إضافة عناصر إضافية (شركاء)
        partners_added = True
        max_partners = 10

        while partners_added and current_width < eff_max_width and len(group_items) < max_partners:
            partners_added = False
            best_partner = None
            best_qty = 0
            best_new_width = current_width

            # البحث عن أفضل شريك
            for key, qty in list(remaining_dict.items()):
                if qty <= 0:
                    continue

                rect_id, w, l = key

                # التحقق من العرض
                new_width = current_width + w
                if new_width > eff_max_width:
                    continue

                # البحث عن أعظم كمية تحقق tolerance
                if l <= 0:
                    continue

                ideal_qty = ref_length_value / l
                search_range = max(3, int(ideal_qty * 0.2))

                for test_qty in range(max(1, int(ideal_qty - search_range)),
                                     min(int(ideal_qty + search_range) + 1, qty + 1)):
                    if test_qty <= 0 or test_qty > qty:
                        continue

                    tolerance_ref = l * test_qty
                    diff = abs(tolerance_ref - ref_length_value)

                    if diff <= eff_tolerance:
                        # عنصر مقبول: نفضل الذي يعطي أكبر عرض
                        if new_width > best_new_width or (new_width == best_new_width and test_qty > best_qty):
                            best_partner = key
                            best_qty = test_qty
                            best_new_width = new_width
                        break

            if best_partner:
                group_items.append((best_partner, best_qty))
                current_width = best_new_width
                remaining_dict[best_partner] -= best_qty
                if remaining_dict[best_partner] <= 0:
                    del remaining_dict[best_partner]
                partners_added = True

        # التحقق من صلاحية المجموعة
        if not group_items or current_width < eff_min_width:
            # مجموعة غير صالحة
            break

        # التحقق من وجود عنصرين مختلفين على الأقل
        unique_ids = set(item[0][0] for item in group_items)
        if len(unique_ids) < 2:
            # مجموعة من عنصر واحد - ممنوعة
            break

        # حساب الكفاءة
        efficiency = (current_width / eff_max_width) * 100 if eff_max_width > 0 else 0

        # اقتراح عناصر إضافية
        suggestions = _suggest_additional_items(
            group_items,
            originals_copy,
            eff_min_width,
            eff_max_width,
            current_width,
            ref_length_value,
            eff_tolerance
        )

        # إضافة الصف للورقة
        items_str = ', '.join([f"ID:{k[0]} ({k[1]}x{k[2]}) qty:{q}" for k, q in group_items])
        rows.append({
            'رقم المجموعة': f'مجموعة_{group_id}',
            'العناصر المستخدمة': items_str,
            'العرض الإجمالي': current_width,
            'الطول المرجعي': ref_length_value,
            'الكفاءة (%)': round(efficiency, 2),
            'الاقتراحات الإضافية': ', '.join(suggestions) if suggestions else 'لا توجد اقتراحات',
            'ملاحظات': 'مجموعة صالحة'
        })
        group_id += 1

    # إنشاء DataFrame
    df = pd.DataFrame(rows)

    # إضافة صف فارغ في حالة عدم وجود بيانات
    if df.empty:
        df = pd.DataFrame([{
            'رقم المجموعة': 'لا توجد مجموعات محسنة',
            'العناصر المستخدمة': 'لا توجد بيانات',
            'العرض الإجمالي': 0,
            'الطول المرجعي': 0,
            'الكفاءة (%)': 0,
            'الاقتراحات الإضافية': 'لا توجد اقتراحات',
            'ملاحظات': 'لا توجد بيانات متاحة للتحسين'
        }])

    return df


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


def _create_size_suggestions_sheet(
    remaining: List[Rectangle],
    min_width: Optional[int],
    max_width: Optional[int],
    tolerance_length: Optional[int]
) -> pd.DataFrame:
    """
    إنشاء ورقة اقتراحات المقاسات المطلوبة للبواقي

    هذه الورقة تحتوي على اقتراحات للمقاسات المطلوبة لتشكيل مجموعات جديدة
    من البواقي وفقاً للشروط المحددة
    """
    # إنشاء DataFrame بسيط وآمن
    data = []

    if remaining and min_width and max_width and tolerance_length:
        for rect in remaining:
            if rect.qty > 0:
                data.append({
                    'المقاس الحالي': f"{rect.width}x{rect.length}",
                    'الكمية': rect.qty,
                    'الطول الإجمالي': rect.length * rect.qty,
                    'نوع الاقتراح': 'تحليل',
                    'العرض المطلوب': f"{min_width}-{max_width}",
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


def _suggest_additional_items(
    group_items: List[Tuple],
    originals: List[Rectangle],
    min_width: int,
    max_width: int,
    current_width: int,
    ref_length_value: int,
    tolerance: int
) -> List[str]:
    """
    اقتراح عناصر إضافية لإكمال المجموعة بناءً على البيانات الموجودة.

    يتحقق من:
    1. العرض المتبقي
    2. شرط tolerance
    3. الكمية المتاحة

    المعاملات:
    -----------
    group_items : List[Tuple]
        العناصر الحالية في المجموعة
    originals : List[Rectangle]
        العناصر الأصلية المتاحة
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    current_width : int
        العرض الحالي للمجموعة
    ref_length_value : int
        الطول المرجعي للمجموعة
    tolerance : int
        السماحية المسموحة

    الإرجاع:
    --------
    List[str]: قائمة الاقتراحات
    """
    suggestions = []
    remaining_width = max_width - current_width

    if remaining_width <= 0:
        return suggestions

    # تجميع العناصر المقترحة حسب الأولوية
    candidates = []

    for orig in originals:
        if orig.qty <= 0 or orig.width > remaining_width:
            continue

        # حساب الكمية المثالية لتحقيق tolerance
        if orig.length <= 0:
            continue

        ideal_qty = ref_length_value / orig.length
        search_range = max(2, int(ideal_qty * 0.2))

        for qty in range(max(1, int(ideal_qty - search_range)),
                        min(int(ideal_qty + search_range) + 1, orig.qty + 1)):
            if qty <= 0 or qty > orig.qty:
                continue

            tolerance_ref = orig.length * qty
            diff = abs(tolerance_ref - ref_length_value)

            if diff <= tolerance:
                # عنصر مقترح صالح
                new_width = current_width + orig.width
                priority = new_width  # نفضل الذي يملأ العرض أكثر

                candidates.append({
                    'id': orig.id,
                    'width': orig.width,
                    'length': orig.length,
                    'qty': qty,
                    'new_width': new_width,
                    'diff': diff,
                    'priority': priority
                })
                break

    # ترتيب حسب الأولوية (أكبر عرض أولاً، ثم أقل فرق tolerance)
    candidates.sort(key=lambda x: (-x['priority'], x['diff']))

    # أخذ أفضل 3 اقتراحات
    for cand in candidates[:3]:
        suggestions.append(
            f"ID:{cand['id']} ({cand['width']}x{cand['length']}) qty:{cand['qty']} "
            f"→ عرض كلي:{cand['new_width']}"
        )

    return suggestions
