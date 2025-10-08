import copy
import pandas as pd
from typing import  List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
import os
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name
from collections import defaultdict
import math
import random

def read_input_excel(path: str, sheet_name = 0) -> List[Rectangle]:
    """
    Read Excel that has (width, length, qty) in first 3 columns.
    If file has header row with strings, we try to detect numeric columns; otherwise we read header = None.
    """
    # Try reading without header first
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx":
            engine = "openpyxl"
        elif ext == ".xls":
            engine = "xlrd"
        else:
            # Try openpyxl first for unknown extensions
            engine = "openpyxl"
        
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine=engine)
    except Exception as e:
        # Fallback: try without specifying engine
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        except Exception as e2:
            raise Exception(f"فشل في قراءة الملف: {e2}")

    carpets = []
    for idx, row in df.iterrows():
        try:
            w = int(row[0])
            l = int(row[1])
            q = int(row[2])
        except Exception:
            # skip invalid rows
            continue
        carpets.append(Rectangle(idx+1, w, l ,q))
    return carpets


# def write_output_excel(path: str, groups: List[Group], remaining: List[Rectangle]):
def write_output_excel(path: str,
                       groups: List[Group],
                       remaining: List[Rectangle],
                       remainder_groups: Optional[List[Group]] = None,
                       min_width: Optional[int] = None,
                       max_width: Optional[int] = None,
                       tolerance_length: Optional[int] = None,
                       originals: Optional[List[Rectangle]] = None,
                       enhanced_remainder_groups: Optional[List[Group]] = None):
    # sheet1: group details (original groups + remainder groups + enhanced remainder groups)
    row = []
    
    # المجموعات الأصلية
    for g in groups:
        for it in g.items:
            row.append({
                'رقم المجموعة' : f'المجموعة_{g.id}',
                'نوع المجموعة' : 'أصلية',
                'معرف السجاد' : it.rect_id,
                'العرض' : it.width,
                'الطول' : it.length,
                'الكمية المستخدمة' : it.used_qty,
                'الطول الاجمالي للسجادة' : it.length * it.used_qty,
                'الكمية الأصلية' : it.original_qty
            })
    
    # مجموعات البواقي العادية
    if remainder_groups:
        for g in remainder_groups:
            for it in g.items:
                row.append({
                    'رقم المجموعة' : f'المجموعة_{g.id}',
                    'نوع المجموعة' : 'بواقي عادية',
                    'معرف السجاد' : it.rect_id,
                    'العرض' : it.width,
                    'الطول' : it.length,
                    'الكمية المستخدمة' : it.used_qty,
                    'الطول الاجمالي للسجادة' : it.length * it.used_qty,
                    'الكمية الأصلية' : it.original_qty
                })
    
    # المجموعات الإضافية المحسنة من البواقي
    if enhanced_remainder_groups:
        for g in enhanced_remainder_groups:
            for it in g.items:
                row.append({
                    'رقم المجموعة' : f'المجموعة_{g.id}',
                    'نوع المجموعة' : 'بواقي محسنة',
                    'معرف السجاد' : it.rect_id,
                    'العرض' : it.width,
                    'الطول' : it.length,
                    'الكمية المستخدمة' : it.used_qty,
                    'الطول الاجمالي للسجادة' : it.length * it.used_qty,
                    'الكمية الأصلية' : it.original_qty
                })
    
    df1 = pd.DataFrame(row)

    # #sheet2: summary (detailed metrics) - includes all group types
    summary = []
    
    # المجموعات الأصلية
    for g in groups:
        types_count = len(g.items)
        area = sum(it.width * it.length * it.used_qty for it in g.items)
        summary.append({
            'رقم المجموعة' : f'المجموعة_{g.id}',
            'نوع المجموعة' : 'أصلية',
            'العرض الإجمالي' : g.total_width(),
            'الطول الإجمالي المرجعي (التقريبي)'  : g.ref_length(),
            'المساحة الإجمالية' : area,
            'عدد أنواع السجاد' : types_count,
        })
    
    # مجموعات البواقي العادية
    if remainder_groups:
        for g in remainder_groups:
            types_count = len(g.items)
            area = sum(it.width * it.length * it.used_qty for it in g.items)
            summary.append({
                'رقم المجموعة' : f'المجموعة_{g.id}',
                'نوع المجموعة' : 'بواقي عادية',
                'العرض الإجمالي' : g.total_width(),
                'الطول الإجمالي المرجعي (التقريبي)'  : g.ref_length(),
                'المساحة الإجمالية' : area,
                'عدد أنواع السجاد' : types_count,
            })
    
    # المجموعات الإضافية المحسنة
    if enhanced_remainder_groups:
        for g in enhanced_remainder_groups:
            types_count = len(g.items)
            area = sum(it.width * it.length * it.used_qty for it in g.items)
            summary.append({
                'رقم المجموعة' : f'المجموعة_{g.id}',
                'نوع المجموعة' : 'بواقي محسنة',
                'العرض الإجمالي' : g.total_width(),
                'الطول الإجمالي المرجعي (التقريبي)'  : g.ref_length(),
                'المساحة الإجمالية' : area,
                'عدد أنواع السجاد' : types_count,
            })
    
    df2 = pd.DataFrame(summary)

    # sheet3: remaining (deduplicated by id,width,length)
    aggregated = {}
    for r in remaining:
        key = (r.id, r.width, r.length)
        aggregated[key] = aggregated.get(key, 0) + int(r.qty)
    rem_rows = []
    for (rid, w, l), q in aggregated.items():
        rem_rows.append({
            'معرف السجادة' : rid,
            'العرض' : w,
            'الطول' : l,
            'الكمية المتبقية' : q,
        })
    df3 = pd.DataFrame(rem_rows)
    if not df3.empty:
        df3 = (
            df3
            .groupby(['معرف السجادة', 'العرض', 'الطول'], as_index=False)['الكمية المتبقية']
            .sum()
            .sort_values(by=['معرف السجادة', 'العرض', 'الطول'])
        )
    # أضف عمود "ملاحظة" حتى يظهر نص "المجموع" بجوار صف الإجماليات
    if 'ملاحظة' not in df3.columns:
        df3['ملاحظة'] = ''

    # sheet4: UI-like summary (mirrors the on-screen table order and labels) - includes all group types
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
    
    df4 = pd.DataFrame(ui_rows)

    def _append_totals_row(writer, sheet_name: str, df: pd.DataFrame):
        """Append a totals row at the end of the sheet, summing numeric columns only."""
        ws = writer.sheets[sheet_name]
        nrows, ncols = df.shape
        totals_row_idx = nrows + 1  # 0-based index in Excel where header at row 0, data rows start at 1
        # Label cell in first column
        ws.write(totals_row_idx, 0, 'المجموع')
        # محاولة وضع الكلمة في عمود 'ملاحظة' إن وُجد لزيادة الوضوح
        try:
            if 'ملاحظة' in df.columns:
                note_col_idx = df.columns.get_loc('ملاحظة')
                ws.write(totals_row_idx, note_col_idx, 'المجموع')
        except Exception:
            pass
        for col_idx, col_name in enumerate(df.columns):
            if is_numeric_dtype(df[col_name]):
                col_letter = xl_col_to_name(col_idx)
                # Data range is from row 2 to row nrows+1 in Excel (1-based)
                formula = f"=SUM({col_letter}2:{col_letter}{nrows+1})"
                ws.write_formula(totals_row_idx, col_idx, formula)
        
    # ---------------------------
    #  حساب الإجماليات
    # ---------------------------
    # إجمالي قبل العملية (من كل القطع الأصلية)
    total_before = 0
    for g in groups:
        for it in g.items:
            total_before += it.width * it.length * it.original_qty

    # إجمالي بعد العملية (المتبقي فقط)
    total_after = 0
    for (rid, w, l), q in aggregated.items():
        total_after += w * l * q

    totals_df = pd.DataFrame([{
        "الإجمالي قبل العملية": total_before,
        "الإجمالي بعد العملية": total_after,
        "المستهلك": total_before - total_after
    }])

    # توليد اقتراحات التشكيل باستخدام القيم الممررة من الواجهة إن وُجدت
    eff_min_width = 370 if min_width is None else int(min_width)
    eff_max_width = 400 if max_width is None else int(max_width)
    eff_tolerance = 100 if tolerance_length is None else int(tolerance_length)

     # 1) اقتراحات تحليلية (كما كانت سابقًا)
    suggestions = generate_partner_suggestions(remaining, eff_min_width, eff_max_width, eff_tolerance)
    df_sugg = pd.DataFrame(suggestions)

    # تدقيق: تحقق أن (المستخدم + المتبقي) = الأصلي لكل عنصر
    # 1) تجميع المستخدم من جميع المجموعات
    used_totals: Dict[tuple, int] = {}
    def _accumulate_used(from_groups: List[Group]):
        for g in from_groups or []:
            for it in g.items:
                key = (it.rect_id, it.width, it.length)
                used_totals[key] = used_totals.get(key, 0) + int(it.used_qty)
    _accumulate_used(groups)
    _accumulate_used(remainder_groups or [])
    _accumulate_used(enhanced_remainder_groups or [])

    # 2) تجميع المتبقي (افتراضيًا aggregated أعلاه)
    remaining_totals: Dict[tuple, int] = dict(aggregated)

    # 3) تجميع الأصلي من مدخلات caller إن وُجدت، وإلا نفترض الأصلي = المستخدم + المتبقي
    original_totals: Dict[tuple, int] = {}
    if originals is not None:
        for r in originals:
            key = (r.id, r.width, r.length)
            original_totals[key] = original_totals.get(key, 0) + int(r.qty)
    else:
        # fallback: استنتاج الأصلي من المستخدم + المتبقي
        all_keys = set(list(used_totals.keys()) + list(remaining_totals.keys()))
        for k in all_keys:
            original_totals[k] = used_totals.get(k, 0) + remaining_totals.get(k, 0)

    # 4) بناء جدول التدقيق
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
    df_audit = pd.DataFrame(audit_rows)
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='تفاصيل المجموعات', index= False)
        _append_totals_row(writer, 'تفاصيل المجموعات', df1)

        df2.to_excel(writer, sheet_name='ملخص المجموعات', index= False)
        _append_totals_row(writer, 'ملخص المجموعات', df2)

        df3.to_excel(writer, sheet_name='السجاد المتبقي', index= False)
        _append_totals_row(writer, 'السجاد المتبقي', df3)

        df4.to_excel(writer, sheet_name='ملخص الواجهة', index= False)
        _append_totals_row(writer, 'ملخص الواجهة', df4)

        # الورقة الجديدة
        totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)
        
        # الشيت الجديد: اقتراحات تشكيل مجموعات
        df_sugg.to_excel(writer, sheet_name='اقتراحات تشكيل مجموعات', index=False)
        
        # شيت إحصائيات المجموعات الإضافية
        if enhanced_remainder_groups:
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
            df_enhanced_stats = pd.DataFrame(enhanced_stats)
            df_enhanced_stats.to_excel(writer, sheet_name='إحصائيات المجموعات الإضافية', index=False)
            _append_totals_row(writer, 'إحصائيات المجموعات الإضافية', df_enhanced_stats)
        
        # شيت التدقيق
        if not df_audit.empty:
            df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)
            _append_totals_row(writer, 'تدقيق الكميات', df_audit)

        
# ---------- generate partner suggestions ----------
def generate_partner_suggestions(remaining: List[Rectangle],
                                 min_width: int,
                                 max_width: int,
                                 tolerance_length: int) -> List[Dict]:
    """
    اقتراحات أذكى:
    - تقترح أفضل توليفة سريعة لكل عنصر أساسي: شريك واحد أو أكثر (بتكرارات) لإكمال نطاق العرض.
    - تراعي الكميات المتاحة وتقلّص المطلوب وفق المتاح.
    - تحسب الفروقات القصوى في إجمالي الأطوال داخل التوليفة.
    - تعرض توصية مختصرة وسجل تفصيلي للأصناف المقترحة بكمياتها.
    """
    # فهرس العناصر المتاحة حسب العرض ثم حسب id
    by_width: Dict[int, List[Rectangle]] = {}
    for r in remaining:
        if r.qty <= 0:
            continue
        by_width.setdefault(r.width, []).append(r)
    all_widths_desc = sorted(by_width.keys(), reverse=True)

    def lengths_within(items: List[Tuple[int,int,int]], ref_total: int) -> Tuple[bool, int]:
        # items: list of (length, used_qty_per_type_total, rect_id)
        totals = [l * q for (l, q, _) in items]
        if not totals:
            return True, 0
        mx = max(totals); mn = min(totals)
        return (mx - mn) <= tolerance_length and all(abs(t - ref_total) <= tolerance_length for t in totals), mx - mn

    suggestions: List[Dict] = []
    for primary in remaining:
        if primary.qty <= 0:
            continue
        p_w, p_l, p_q = primary.width, primary.length, primary.qty
        ref_total = p_l * p_q

        # حالة منفردة
        best_rows: List[Dict] = []
        if min_width <= p_w <= max_width:
            best_rows.append({
                'معرف الأساسي': primary.id,
                'عرض الأساسي': p_w,
                'طول الأساسي': p_l,
                'كمية الأساسي المتبقية': p_q,
                'توصية مختصرة': 'يمكن منفرداً',
                'العرض المقترح الكلي': p_w,
                'أقصى فرق أطوال داخل التوليفة': 0,
                'تفصيل التوليفة': f"{primary.id}x1"
            })

        # شريك واحد مثالي
        min_rem = max(min_width - p_w, 0)
        max_rem = max_width - p_w
        for w in all_widths_desc:
            if w < min_rem or w > max_rem:
                continue
            for cand in by_width[w]:
                if cand.id == primary.id:
                    continue
                desired = max(1, int(round(ref_total / cand.length)))
                take = min(desired, cand.qty)
                cand_total = cand.length * take
                diff = abs(cand_total - ref_total)
                if diff <= tolerance_length:
                    ok, mx_span = lengths_within([(p_l, p_q, primary.id), (cand.length, take, cand.id)], ref_total)
                    if ok:
                        best_rows.append({
                            'معرف الأساسي': primary.id,
                            'عرض الأساسي': p_w,
                            'طول الأساسي': p_l,
                            'كمية الأساسي المتبقية': p_q,
                            'توصية مختصرة': f"شريك {cand.id} بعدد {take}",
                            'العرض المقترح الكلي': p_w + cand.width,
                            'أقصى فرق أطوال داخل التوليفة': mx_span,
                            'تفصيل التوليفة': f"{primary.id}x{p_q} + {cand.id}x{take}"
                        })

        # أكثر من شريك بطريقة جشعة: ابدأ من الأعـرض وانزل، واسمح بتكرار الشريك
        # نبني التوليفة حتى نصل لأقرب عرض ≥ min_width دون تجاوز max_width
        current_width = p_w
        items_combo: List[Tuple[int,int,int,int,int]] = []  # (id,width,length,qty_used,available_after)
        remaining_cap: Dict[int, int] = {r.id: r.qty for r in remaining}
        # نحتاج مطابقة إجمالي الأطوال لكل نوع مع مرجع primary ضمن tolerance
        for w in all_widths_desc:
            if current_width >= min_width:
                break
            # لا تتجاوز الحافة العليا
            if current_width + w > max_width:
                continue
            for cand in by_width[w]:
                if cand.id == primary.id:
                    continue
                avail = remaining_cap.get(cand.id, 0)
                if avail <= 0:
                    continue
                desired_per_block = max(1, int(round(ref_total / cand.length)))
                # كم بلوك يمكن أخذه بدون تجاوز العرض والأعداد
                while avail >= desired_per_block and current_width + w <= max_width and current_width < min_width:
                    # تحقق الطول
                    cand_total = cand.length * desired_per_block
                    if abs(cand_total - ref_total) > tolerance_length:
                        break
                    items_combo.append((cand.id, cand.width, cand.length, desired_per_block, avail - desired_per_block))
                    avail -= desired_per_block
                    remaining_cap[cand.id] = avail
                    current_width += w
                    if current_width >= min_width:
                        break
        if current_width >= min_width and current_width <= max_width and items_combo:
            ok, mx_span = lengths_within([(p_l, p_q, primary.id)] + [(l, q, _id) for (_id, w, l, q, _) in items_combo], ref_total)
            if ok:
                detail = "+ ".join([f"{primary.id}x{p_q}"] + [f"{_id}x{q}" for (_id, w, l, q, _) in items_combo])
                best_rows.append({
                    'معرف الأساسي': primary.id,
                    'عرض الأساسي': p_w,
                    'طول الأساسي': p_l,
                    'كمية الأساسي المتبقية': p_q,
                    'توصية مختصرة': 'توليفة متعددة الشركاء (جشعة)',
                    'العرض المقترح الكلي': current_width,
                    'أقصى فرق أطوال داخل التوليفة': mx_span,
                    'تفصيل التوليفة': detail
                })

        # إذا لم نجد أي توليفة، قدّم توصية افتراضية بما يلزم من عرض وكميات تقريبية
        if not best_rows:
            min_rem = max(min_width - p_w, 0)
            max_rem = max_width - p_w
            best_rows.append({
                'معرف الأساسي': primary.id,
                'عرض الأساسي': p_w,
                'طول الأساسي': p_l,
                'كمية الأساسي المتبقية': p_q,
                'توصية مختصرة': f"وفّر عرض ضمن {min_rem}-{max_rem}",
                'العرض المقترح الكلي': p_w,
                'أقصى فرق أطوال داخل التوليفة': None,
                'تفصيل التوليفة': f"مرشح بطول {p_l} وبعدد ≈ {p_q}"
            })

        # اجمع أفضل الصفوف لهذا الأساسي ضمن النتائج العامة
        suggestions.extend(best_rows)

    return suggestions

from typing import List, Dict, Tuple, Optional
import copy
import math


def regroup_residuals_advanced(residuals: List[Dict], min_width: int, max_width: int, tolerance: int,
                               max_depth: int = 6) -> Tuple[List[Dict], List[Dict]]:
    """
    خوارزمية متقدمة لإعادة تجميع البواقي (residuals) وفق الوصف الذي أعطيته:

    الفرضيات على عناصر `residuals`:
      - كل عنصر عبارة عن dict يحتوي على المفاتيحات التالية على الأقل:
        - 'id'      : معرف العنصر
        - 'width'   : العرض لكل قطعة
        - 'length'  : الطول لكل قطعة
        - 'remaining': الكمية المتبقية من هذا النوع
      - إذا لم يوجد مفتاح 'original' فسيتم إضافته تلقائيًا بقيمة 'remaining' في بداية التنفيذ

    المنطق العام (مبسّط):
      1. نرتب العناصر تنازليًا بحسب العرض.
      2. نختار كـ "قاعدة" العنصر الأعرض المتوفر (مع ضمان أن عرض القطعة الأولى <= max_width).
      3. نجرب استخدام أكبر كمية ممكنة من القاعدة (لكن لا تتجاوز حدود العرض). لكل كمية
         نُحاول إضافة عناصر أخرى (بتناقص العرض) بحيث يصبح مجموع العرض داخل [min_width, max_width]
         وكذلك يكون الفرق بين (length * used_qty) لكل نوع داخل `tolerance` من قيمة مرجعية (نستخدم
         طول القاعدة * كميتها كمرجع). الشرط يجب أن يتحقق بين كل الأزواج (نحضى بأن تكون قيمة
         كل نوع قريبة من مرجع الطول).
      4. نختار كميات أكبر أولًا لتفادي حلقة استخدام كمية 1 فقط.
      5. عند تشكيل مجموعة ناجحة نقص الكميات المستخدمة من `remaining` ونخزن المجموعة.
      6. نكرر حتى لا يمكن تشكيل مجموعات جديدة.
      7. ندمج المجموعات المتطابقة (نلغي التكرار) عن طريق تجميع الكميات المُستخدمة.

    تحسينات/ملاحظات مطبقة:
      - نجمع العرض باستخدام `width * qty` (تصحيح لسلوك شائع حيث يُحسب العرض بدون ضرب في الكمية).
      - عند اختبار الفرق في الأطوال نؤكد التفاوت بالنسبة للمرجع ولكل العناصر الموجودة في المجموعة.
      - نحد عمق البحث (max_depth) لمنع انفجار التعقيد.

    المخرجات:
      - قائمة المجموعات الجديدة (كل مجموعة: dict تحتوي على 'items' (قائمة dicts مع id,width,length,used),
        'total_width', 'ref_length')
      - القائمة المعدّلة من residuals (مُحدّثة الحقول 'remaining' و'original' إن لزم)

    """

    # تهيئة الحقول الأساسية
    residuals = copy.deepcopy(residuals)
    for r in residuals:
        if 'remaining' not in r:
            r['remaining'] = int(r.get('qty', 0))
        if 'original' not in r:
            r['original'] = r['remaining']

    # دالة مساعدة لجلب عنصر حسب id
    id_map = {r['id']: r for r in residuals}

    # ترتيب تنازلي بالعرض
    def get_candidates():
        return sorted([r for r in residuals if r['remaining'] > 0], key=lambda x: x['width'], reverse=True)

    groups: List[Dict] = []

    # دمج عناصر المجموعة ذات نفس id الى سطر واحد
    def normalize_group_items(items: List[Dict]) -> List[Dict]:
        by_id = {}
        for it in items:
            if it['id'] in by_id:
                by_id[it['id']]['used'] += it['used']
            else:
                by_id[it['id']] = dict(it)
        return list(by_id.values())

    # دالة لمفتاح المجموعة لتجنب التكرار (ترتيب حسب id)
    def group_key(items: List[Dict]) -> Tuple[Tuple[int, int], ...]:
        norm = normalize_group_items(items)
        key = tuple(sorted(((it['id'], int(it['used'])) for it in norm), key=lambda x: x[0]))
        return key

    # دمج المجموعات المتطابقة (بعد الانتهاء)
    def merge_duplicate_groups(groups_list: List[Dict]) -> List[Dict]:
        merged = {}
        for g in groups_list:
            key = group_key(g['items'])
            if key not in merged:
                merged[key] = copy.deepcopy(g)
            else:
                # نجمع الكميات لكل عنصر
                exist = merged[key]
                exist_items = {it['id']: it for it in exist['items']}
                for it in g['items']:
                    if it['id'] in exist_items:
                        exist_items[it['id']]['used'] += it['used']
                    else:
                        exist['items'].append(copy.deepcopy(it))
                # نعيد حساب العرض المرجعي
                exist['items'] = normalize_group_items(exist['items'])
                exist['total_width'] = sum(it['width'] * it['used'] for it in exist['items'])
                exist['count_types'] = len(exist['items'])
        # تحويل للقائمة
        return list(merged.values())

    # دالة التحقق من شرط الفرق في الأطوال (كل زوج يجب أن يكون الفرق <= tolerance)
    def lengths_within_tolerance(items: List[Dict], tolerance: int) -> bool:
        totals = [it['length'] * it['used'] for it in items]
        if not totals:
            return True
        mn = min(totals)
        mx = max(totals)
        return (mx - mn) <= tolerance

    # الدالة الأساسية للبحث العودي عن شركاء (bounded depth)
    def search_partners(candidates: List[Dict], start_idx: int, last_width: float, current_items: List[Dict],
                        current_width: int, ref_total_len: int, depth: int) -> Optional[List[Dict]]:
        # شرط انتهاء ناجح
        if min_width <= current_width <= max_width:
            # تأكد من تحقق شرط الأطوال
            if lengths_within_tolerance(current_items, tolerance):
                return normalize_group_items(current_items)
            # وإلا نستمر للبحث (قد نجد إضافة تُحسّن)

        # حد العمق أو تجاوز العرض
        if depth >= max_depth or current_width > max_width:
            return None

        # محاولة إضافة عناصر لاحقة بعرض أصغر من last_width
        for i in range(start_idx, len(candidates)):
            cand = candidates[i]
            # نطبق شرط "أصغر من العنصر السابق مباشرة" => نسمح فقط بعرض أصغر (strictly smaller)
            if cand['width'] >= last_width:
                continue
            avail = cand['remaining']
            if avail <= 0:
                continue

            # الحد الأقصى الذي نستطيع أخذه من هذه القطعة دون تجاوز max_width
            max_take_by_width = (max_width - current_width) // cand['width']
            max_take = min(avail, max_take_by_width)
            if max_take <= 0:
                continue

            # نجرب الكميات من الأكبر إلى الأصغر (لتفادي حلقة استخدام qty=1 فقط)
            for take in range(max_take, 0, -1):
                new_item = {'id': cand['id'], 'width': cand['width'], 'length': cand['length'], 'used': take}
                new_items = current_items + [new_item]

                # شرط الأطوال: قارن بين إجمالي طول هذا العنصر والمرجع
                cand_total_len = cand['length'] * take
                if abs(cand_total_len - ref_total_len) > tolerance:
                    # إذا كان الفرق كبيرًا، تجاهل هذه الكمية
                    continue

                # تأكد أن الأطوال بين كل الأزواج داخل tolerance
                if not lengths_within_tolerance(new_items, tolerance):
                    continue

                new_width = current_width + cand['width'] * take
                # إذا تجاوزنا الحد الأعلى، لا تأخذ هذه الكمية
                if new_width > max_width:
                    continue

                # استدعاء عودي
                res = search_partners(candidates, i + 1, cand['width'], new_items, new_width, ref_total_len, depth + 1)
                if res is not None:
                    return res

        return None

    # حلقة رئيسية: نجرب كل قاعدة حتى لا نحقق المزيد من المجموعات
    iterations_without_progress = 0
    MAX_NO_PROGRESS = 5

    while True:
        candidates = get_candidates()
        if not candidates:
            break

        progress = False

        # نحاول كل العناصر كقاعدة (لكن نبدأ بالأعرض)
        for base in candidates:
            if base['remaining'] <= 0:
                continue
            if base['width'] > max_width:
                # لا يمكن استخدام هذا العنصر كقاعدة لأنه بعرض أكبر من الحد الأعلى
                continue

            # أقصى كمية يمكن استخدامها من القاعدة بدون تجاوز العرض
            max_base_use = min(base['remaining'], max(1, max_width // base['width']))

            formed = None
            # نجرب كميات القاعدة من الأكبر إلى الأصغر
            for base_use in range(max_base_use, 0, -1):
                base_item = {'id': base['id'], 'width': base['width'], 'length': base['length'], 'used': base_use}
                current_width = base['width'] * base_use
                ref_total_len = base['length'] * base_use

                # إذا وقعت الكمية الحالية ضمن المجال وشرط الأطوال محقق
                if min_width <= current_width <= max_width and lengths_within_tolerance([base_item], tolerance):
                    formed = normalize_group_items([base_item])
                    break

                # ابحث عن شركاء بآلية تنازلية في العرض
                candidates_for_partners = [r for r in candidates if r['id'] != base['id'] and r['width'] < base['width']]
                res = search_partners(candidates_for_partners, 0, base['width'], [base_item], current_width, ref_total_len, 0)
                if res is not None:
                    formed = res
                    break

            # إذا كونّا مجموعة، فقُم بتسجيلها وتحديث الكميات
            if formed is not None:
                # نفترض أن formed مُطَبَّع (normalize) بحيث كل id يظهر مرة واحدة
                total_width = sum(it['width'] * it['used'] for it in formed)
                group_record = {'items': formed, 'total_width': total_width, 'ref_length': ref_total_len, 'count_types': len(formed)}

                # خفض الكميات
                for it in formed:
                    rid = it['id']
                    used = int(it['used'])
                    rec = id_map[rid]
                    # تحقق من عدم السلبية
                    if used > rec['remaining']:
                        # هذا احتمال نادر ولكن نتحاشاه بالتقليم
                        used = rec['remaining']
                        it['used'] = used
                    rec['remaining'] -= used
                    if rec['remaining'] < 0:
                        rec['remaining'] = 0

                groups.append(group_record)
                progress = True
                break

        if not progress:
            iterations_without_progress += 1
            if iterations_without_progress >= MAX_NO_PROGRESS:
                break
        else:
            iterations_without_progress = 0

    # بعد الانتهاء: دمج المجموعات المكررة
    groups = merge_duplicate_groups(groups)

    # إعداد قائمة البواقي المحدثة
    updated_residuals = [r for r in residuals if r['remaining'] > 0]

    return groups, updated_residuals


# مثال سريع (غير مُفعل تلقائيًا) على كيفية استخدام الدالة:
if __name__ == '__main__':
    sample = [
        {'id': 1, 'width': 120, 'length': 200, 'remaining': 2},
        {'id': 2, 'width': 80, 'length': 100, 'remaining': 3},
        {'id': 3, 'width': 60, 'length': 200, 'remaining': 4},
        {'id': 4, 'width': 40, 'length': 195, 'remaining': 10},
    ]

    gs, rem = regroup_residuals_advanced(sample, min_width=180, max_width=260, tolerance=20)
    print('groups:')
    for g in gs:
        print(g)
    print('remaining:')
    for r in rem:
        print(r)


def regroup_residuals_full(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance: int,
    start_group_id: int = 10000
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية موسعة تقوم بإعادة التجميع حتى لا تبقى بواقي ممكنة.
    """

    current_remaining = copy.deepcopy(remaining)
    all_groups: List[Group] = []
    seen_combinations = set()
    group_id = start_group_id

    def can_tolerate(len_a, qty_a, len_b, qty_b) -> bool:
        """هل الفرق في الطول ضمن حدود السماحية"""
        return abs(len_a * qty_a - len_b * qty_b) <= tolerance

    while True:
        current_remaining = [r for r in current_remaining if r.qty > 0]
        if not current_remaining:
            break

        # ترتيب تنازلي حسب العرض
        current_remaining.sort(key=lambda r: r.width, reverse=True)

        group_items = []
        total_width = 0
        ref_rect = current_remaining[0]
        used_indices = set()
        remaining_width = max_width

        # نبدأ بأكبر عنصر طالما عرضه < max_width
        if ref_rect.width > max_width:
            # لا يمكن استخدام هذا المقاس
            current_remaining.pop(0)
            continue

        # نبدأ باستخدام العنصر المرجعي
        ref_used_qty = max(1, ref_rect.qty // 2)
        group_items.append(
            UsedItem(
                rect_id=ref_rect.id,
                width=ref_rect.width,
                length=ref_rect.length,
                used_qty=ref_used_qty,
                original_qty=ref_rect.qty
            )
        )
        total_width += ref_rect.width
        remaining_width -= ref_rect.width
        ref_rect.qty -= ref_used_qty

        # نحاول إضافة عناصر أخرى حتى نصل للنطاق المطلوب
        for idx, other in enumerate(current_remaining[1:], start=1):
            if total_width >= max_width:
                break
            if other.qty <= 0:
                continue

            if not can_tolerate(ref_rect.length, ref_used_qty, other.length, 1):
                continue

            # إذا كنا نحتاج عرض إضافي يكمل إلى النطاق
            if min_width <= total_width + other.width <= max_width:
                use_qty = min(other.qty, ref_used_qty)
                group_items.append(
                    UsedItem(
                        rect_id=other.id,
                        width=other.width,
                        length=other.length,
                        used_qty=use_qty,
                        original_qty=other.qty
                    )
                )
                total_width += other.width
                remaining_width -= other.width
                other.qty -= use_qty
                used_indices.add(idx)

            elif total_width + other.width < min_width:
                # يمكن التكرار داخل نفس المجموعة
                repeat_times = min((min_width - total_width) // other.width, other.qty)
                if repeat_times > 0:
                    group_items.append(
                        UsedItem(
                            rect_id=other.id,
                            width=other.width,
                            length=other.length,
                            used_qty=repeat_times,
                            original_qty=other.qty
                        )
                    )
                    total_width += other.width * repeat_times
                    remaining_width -= other.width * repeat_times
                    other.qty -= repeat_times
                    used_indices.add(idx)

        # إذا لم نصل للنطاق المطلوب نحاول تكرار العنصر المرجعي نفسه
        while total_width < min_width and ref_rect.qty > 0:
            total_width += ref_rect.width
            ref_rect.qty -= 1
            group_items.append(
                UsedItem(
                    rect_id=ref_rect.id,
                    width=ref_rect.width,
                    length=ref_rect.length,
                    used_qty=1,
                    original_qty=ref_rect.qty + 1
                )
            )

        # تحقق من كون المجموعة ضمن النطاق
        if min_width <= total_width <= max_width:
            signature = tuple(sorted((i.rect_id, i.used_qty) for i in group_items))
            if signature not in seen_combinations:
                seen_combinations.add(signature)
                all_groups.append(Group(id=group_id, items=group_items))
                group_id += 1
        else:
            # فشلنا في تكوين مجموعة مناسبة
            break

    leftovers = [r for r in current_remaining if r.qty > 0]
    return all_groups, leftovers

# def exhaustively_regroup(
#     remaining: List[Rectangle],
#     min_width: int,
#     max_width: int,
#     tolerance_length: int,
#     start_group_id: int = 10000,
#     max_rounds: int = 50
# ) -> Tuple[List[Group], List[Rectangle]]:
#     """
#     استدعاء خوارزمية إعادة التجميع المتقدمة تكراراً حتى لا يبقى شيء قابل للتجميع.
#     """
#     current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining if r.qty > 0]
#     all_groups: List[Group] = []
#     next_group_id = start_group_id
#     rounds = 0

#     while rounds < max_rounds:
#         rounds += 1

#         formed, leftover = regroup_residuals_full(
#             current_remaining,
#             min_width=min_width,
#             max_width=max_width,
#             tolerance=tolerance_length,
#             start_group_id=next_group_id
#         )

#         if not formed:
#             break

#         all_groups.extend(formed)
#         next_group_id = (all_groups[-1].id if all_groups else next_group_id) + 1
#         current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in leftover if r.qty > 0]

#         if not current_remaining:
#             break

#     final_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in current_remaining if r.qty > 0]
#     return all_groups, final_remaining

def create_enhanced_remainder_groups(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية محسنة لتشكيل مجموعات إضافية من البواقي مع إمكانية تكرار العناصر.
    تهدف إلى استغلال أقصى قدر ممكن من البواقي مع مراعاة الشروط المطلوبة.
    """
    
    current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining if r.qty > 0]
    all_groups: List[Group] = []
    next_group_id = start_group_id
    rounds = 0

    def can_tolerate(len_a, qty_a, len_b, qty_b) -> bool:
        """فحص ما إذا كان الفرق في الطول ضمن حدود السماحية"""
        return abs(len_a * qty_a - len_b * qty_b) <= tolerance_length

    def find_best_combination(items, target_width, ref_length, ref_qty):
        """البحث عن أفضل توليفة من العناصر المتاحة"""
        from itertools import combinations, product
        
        best_combination = None
        best_score = float('inf')
        
        # نجرب جميع التوليفات الممكنة
        for r in range(1, min(len(items) + 1, 5)):  # حد أقصى 4 عناصر في المجموعة
            for combo in combinations(items, r):
                # نجرب كميات مختلفة لكل عنصر
                quantities = []
                for item in combo:
                    max_qty = min(item.qty, max_width // item.width)
                    quantities.append(list(range(1, max_qty + 1)))
                
                for qty_combo in product(*quantities):
                    total_width = sum(item.width * qty for item, qty in zip(combo, qty_combo))
                    
                    if not (min_width <= total_width <= max_width):
                        continue
                    
                    # فحص شرط السماحية
                    all_valid = True
                    for item, qty in zip(combo, qty_combo):
                        if not can_tolerate(ref_length, ref_qty, item.length, qty):
                            all_valid = False
                            break
                    
                    if all_valid:
                        # حساب النقاط (نفضل المجموعات الأقرب للعرض المثالي)
                        ideal_width = (min_width + max_width) / 2
                        score = abs(total_width - ideal_width)
                        
                        if score < best_score:
                            best_score = score
                            best_combination = list(zip(combo, qty_combo))
        
        return best_combination

    while rounds < max_rounds and current_remaining:
        rounds += 1
        progress_made = False
        
        # ترتيب العناصر تنازلياً حسب العرض
        current_remaining.sort(key=lambda r: r.width, reverse=True)
        
        # محاولة تشكيل مجموعات جديدة
        for i, base_item in enumerate(current_remaining):
            if base_item.qty <= 0:
                continue
            
            # إذا كان العنصر أكبر من الحد الأقصى، نتخطاه
            if base_item.width > max_width:
                continue
            
            # نجرب كميات مختلفة من العنصر الأساسي
            max_base_qty = min(base_item.qty, max_width // base_item.width)
            
            for base_qty in range(1, max_base_qty + 1):
                # فحص ما إذا كان العنصر وحده يكفي
                if min_width <= base_item.width * base_qty <= max_width:
                    # تشكيل مجموعة من عنصر واحد
                    group_items = [
                        UsedItem(
                            rect_id=base_item.id,
                            width=base_item.width,
                            length=base_item.length,
                            used_qty=base_qty,
                            original_qty=base_item.qty
                        )
                    ]
                    
                    # إنشاء المجموعة
                    new_group = Group(id=next_group_id, items=group_items)
                    all_groups.append(new_group)
                    next_group_id += 1
                    
                    # تحديث الكمية
                    base_item.qty -= base_qty
                    progress_made = True
                    break
                
                # البحث عن شركاء
                other_items = [item for j, item in enumerate(current_remaining) 
                              if j != i and item.qty > 0 and item.width < base_item.width]
                
                if other_items:
                    best_combo = find_best_combination(
                        other_items, 
                        max_width - base_item.width * base_qty,
                        base_item.length,
                        base_qty
                    )
                    
                    if best_combo:
                        # تشكيل المجموعة
                        group_items = [
                            UsedItem(
                                rect_id=base_item.id,
                                width=base_item.width,
                                length=base_item.length,
                                used_qty=base_qty,
                                original_qty=base_item.qty
                            )
                        ]
                        
                        for partner, partner_qty in best_combo:
                            group_items.append(
                                UsedItem(
                                    rect_id=partner.id,
                                    width=partner.width,
                                    length=partner.length,
                                    used_qty=partner_qty,
                                    original_qty=partner.qty
                                )
                            )
                            partner.qty -= partner_qty
                        
                        # إنشاء المجموعة
                        new_group = Group(id=next_group_id, items=group_items)
                        all_groups.append(new_group)
                        next_group_id += 1
                        
                        # تحديث كمية العنصر الأساسي
                        base_item.qty -= base_qty
                        progress_made = True
                        break
            
            if progress_made:
                break
        
        # إزالة العناصر التي نفدت كميتها
        current_remaining = [r for r in current_remaining if r.qty > 0]
        
        if not progress_made:
            break

    final_remaining = [r for r in current_remaining if r.qty > 0]
    return all_groups, final_remaining


def exhaustively_regroup(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    استدعاء متكرر لخوارزمية إعادة تجميع البواقي حتى لا يتبقى شيء قابل للتجميع.
    يستخدم الخوارزمية المحسنة مع إمكانية تكرار العناصر.
    """
    
    # استخدام الخوارزمية المحسنة
    return create_enhanced_remainder_groups(
        remaining, min_width, max_width, tolerance_length, start_group_id, max_rounds
    )


def create_enhanced_remainder_groups_from_rectangles(
    remaining_rectangles: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000
) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة مساعدة لإنشاء مجموعات إضافية محسنة من قائمة Rectangle.
    هذه الدالة يمكن استخدامها مباشرة من التطبيق الرئيسي.
    
    المعاملات:
    - remaining_rectangles: قائمة العناصر المتبقية
    - min_width: الحد الأدنى للعرض
    - max_width: الحد الأقصى للعرض  
    - tolerance_length: حدود السماحية للطول
    - start_group_id: رقم المجموعة الأولى (افتراضي: 10000)
    
    الإرجاع:
    - قائمة المجموعات الجديدة
    - قائمة العناصر المتبقية بعد التجميع
    """
    return create_enhanced_remainder_groups(
        remaining_rectangles, min_width, max_width, tolerance_length, start_group_id
    )