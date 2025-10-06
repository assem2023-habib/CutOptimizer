import pandas as pd
from typing import  List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
import os
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name
from collections import defaultdict
import math

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
                       remainder_groups: Optional[List[Group]] = None):
    # sheet1: group details
    row = []
    for g in groups:
        for it in g.items:
            row.append({
                'رقم المجموعة' : f'المجموعة_{g.id}',
                'معرف السجاد' : it.rect_id,
                'العرض' : it.width,
                'الطول' : it.length,
                'الكمية المستخدمة' : it.used_qty,
                'الطول الاجمالي للسجادة' : it.length * it.used_qty,
                'الكمية الأصلية' : it.original_qty
            })
    df1 = pd.DataFrame(row)

    # #sheet2: summary (detailed metrics)
    summary = []
    for g in groups:
        types_count = len(g.items)
        area = sum(it.width * it.length * it.used_qty for it in g.items)
        summary.append({
            'رقم المجموعة' : f'المجموعة_{g.id}',
            'العرض الإجمالي' : g.total_width(),
            'الطول الإجمالي المرجعي (التقريبي)'  : g.ref_length(),
            'المساحة الإجمالية' : area,
            'عدد أنواع السجاد' : types_count,
        })
    df2 = pd.DataFrame(summary)

    # sheet3: remaining
    rem_rows = []
    for r in remaining:
        rem_rows.append({
            'معرف السجادة' : r.id,
            'العرض' : r.width,
            'الطول' : r.length,
            'الكمية المتبقية' : r.qty,
        })
    df3 = pd.DataFrame(rem_rows)

    # sheet4: UI-like summary (mirrors the on-screen table order and labels)
    ui_rows = []
    for g in groups:
        ui_rows.append({
            'عدد الأنواع': len(g.items),
            'الطول المرجعي': g.ref_length(),
            'العرض الإجمالي': g.total_width(),
            'رقم المجموعة': f'المجموعة_{g.id}',
        })
    df4 = pd.DataFrame(ui_rows)

    def _append_totals_row(writer, sheet_name: str, df: pd.DataFrame):
        """Append a totals row at the end of the sheet, summing numeric columns only."""
        ws = writer.sheets[sheet_name]
        nrows, ncols = df.shape
        totals_row_idx = nrows + 1  # 0-based index in Excel where header at row 0, data rows start at 1
        # Label cell in first column
        ws.write(totals_row_idx, 0, 'المجموع')
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
    for r in remaining:
        total_after += r.width * r.length * r.qty

    totals_df = pd.DataFrame([{
        "الإجمالي قبل العملية": total_before,
        "الإجمالي بعد العملية": total_after,
        "المستهلك": total_before - total_after
    }])

    # توليد اقتراحات التشكيل (نحتاج تمرير حدود النطاق والهامش)
    # استخدم القيم المطلوبة هنا؛ إذا تريد تمريرها من الخارج، عدل التوقيع
    min_width = 370   # أو قراءة من config
    max_width = 400
    tolerance_length = 100

     # 1) اقتراحات تحليلية (كما كانت سابقًا)
    suggestions = generate_partner_suggestions(remaining,min_width,max_width, tolerance_length)
    df_sugg = pd.DataFrame(suggestions)

    # 2) **إعادة التجميع الفعلية** للبواقي (نُجرب تكوين مجموعات فعلياً من remaining)
    # ترجع: (قائمة مجموعات من البواقي, قائمة بقايا نهائية بعد المحاولة)
      # ------ استدعاء الإعادة التكرارية للبواقي حتى الاستنفاد ------
    # اختيار 'start_group_id' بحيث لا يتداخل مع المجموعات الأصلية
    existing_max_id = max((g.id for g in groups), default=0)
    start_rem_group_id = max(existing_max_id + 1, 10000)

    computed_remainder_groups, computed_remaining_after = exhaustively_regroup(
        remaining,
        min_width,
        max_width,
        tolerance_length,
        start_group_id=start_rem_group_id,
        max_rounds=100  # يمكنك تعديل هذا للحد الأقصى للجولات
    )
    
    # إذا caller مرر remainder_groups في باراميتر الدالة، نستخدمه؛ وإلا نستخدم المحسوب
    to_write_remainder_groups = remainder_groups if remainder_groups is not None else computed_remainder_groups
    to_write_remaining_after = computed_remaining_after
    
    rem_group_rows = []
    for g in (to_write_remainder_groups or []):
        for it in g.items:
            rem_group_rows.append({
                'رقم المجموعة' : f'باقي_{g.id}',
                'معرف السجاد' : it.rect_id,
                'العرض' : it.width,
                'الطول' : it.length,
                'الكمية المستخدمة' : it.used_qty,
                'الطول الاجمالي للسجادة' : it.length * it.used_qty,
                'الكمية الأصلية' : it.original_qty
            })
    df_rem_groups = pd.DataFrame(rem_group_rows)

    # 4) جدول البواقي النهائية بعد محاولة إعادة التجميع
    df_remaining_after = pd.DataFrame([
        {'معرف السجادة': r.id, 'العرض': r.width, 'الطول': r.length, 'الكمية المتبقية بعد إعادة التجميع': r.qty}
        for r in (to_write_remaining_after or [])
    ])
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
        # ---------------------------
        #  شيت: مجموعات من البواقي المعاد تجميعها (إن وُجدت)
        # ---------------------------
        if not df_rem_groups.empty:
            df_rem_groups.to_excel(writer, sheet_name='مجموعات البواقي', index=False)
            _append_totals_row(writer, 'مجموعات البواقي', df_rem_groups)
        else:
            # نكتب رسالة صغيرة توضيحية في الشيت لو لم توجد مجموعات
            pd.DataFrame([{'ملاحظة': 'لا توجد مجموعات قابلة للتشكيل من البواقي'}]).to_excel(
                writer, sheet_name='مجموعات البواقي', index=False
            )
        # ---------------------------
        #  شيت: البواقي النهائية بعد إعادة التجميع
        # ---------------------------
        if not df_remaining_after.empty:
            df_remaining_after.to_excel(writer, sheet_name='البواقي النهائية', index=False)
            _append_totals_row(writer, 'البواقي النهائية', df_remaining_after)
        else:
            pd.DataFrame([{'ملاحظة': 'لا توجد بواقي بعد إعادة التجميع'}]).to_excel(
                writer, sheet_name='البواقي النهائية', index=False
            )

        
# ---------- generate partner suggestions ----------
def generate_partner_suggestions(remaining: List[Rectangle],
                                 min_width: int,
                                 max_width: int,
                                 tolerance_length: int) -> List[Dict]:
    """
    For each remaining rectangle type (primary), compute what partner widths/qtys
    would be needed to form another group within [min_width, max_width] and
    match total lengths within tolerance_length.

    Returns list of dicts (rows) suitable for a DataFrame.
    """
    # build widths map (allow multiple entries per width)
    widths_map: Dict[int, List[Rectangle]] = {}
    for r in remaining:
        widths_map.setdefault(r.width, []).append(r)

    suggestions = []
    for primary in remaining:
        p_w = primary.width
        p_l = primary.length
        p_q = primary.qty
        if p_q <= 0:
            continue
        primary_total_length = p_l * p_q
        min_rem = max(min_width - p_w, 0)
        max_rem = max_width - p_w

        # if primary alone can form a group
        alone_ok = (min_width <= p_w <= max_width)

        # try to find candidate widths contained in remaining that fit width-range
        found_candidate = False
        for cand_w, cand_list in widths_map.items():
            if cand_w < min_rem or cand_w > max_rem:
                continue
            # for each rectangle with that width
            for cand in cand_list:
                if cand.id == primary.id:
                    continue
                # desired qty to roughly match total length
                desired_qty = max(1, int(round(primary_total_length / cand.length)))
                cand_total_len = cand.length * desired_qty
                diff = abs(cand_total_len - primary_total_length)
                can_match_length = (diff <= tolerance_length)
                available_qty = cand.qty
                shortage = max(0, desired_qty - available_qty)
                suggestions.append({
                    "معرف الأساسي": primary.id,
                    "عرض الأساسي": p_w,
                    "طول الأساسي": p_l,
                    "كمية الأساسي المتبقية": p_q,
                    "الطول الإجمالي الأساسي": primary_total_length,
                    "نطاق العرض المطلوب (بقي)": f"{min_rem}..{max_rem}",
                    "مرشح العرض": cand.width,
                    "مرشح الطول": cand.length,
                    "الكمية المطلوبة من المرشح (تقريب)": desired_qty,
                    "كمية المرشح المتاحة": available_qty,
                    "نقص بالقطع إن وجد": shortage,
                    "فرق الطول (سم)": diff,
                    "يناسب طولاً؟": "نعم" if can_match_length else "لا",
                    "ملاحظة": "" if can_match_length and shortage == 0 else (
                        "يناسب طولاً لكن غير كافٍ" if can_match_length and shortage>0 else
                        ("لا يناسب طولا" if not can_match_length else "")
                    )
                })
                found_candidate = True

        # if no candidate widths found inside range, add suggestion about needed width range
        if not found_candidate:
            # In the simplest practical case, if we want partner pieces with the SAME length as primary,
            # desired number of pieces would be equal to primary quantity (so that total lengths match exactly).
            # So we recommend candidate with same length p_l and qty = p_q, and any width in [min_rem,max_rem].
            suggestions.append({
                "معرف الأساسي": primary.id,
                "عرض الأساسي": p_w,
                "طول الأساسي": p_l,
                "كمية الأساسي المتبقية": p_q,
                "الطول الإجمالي الأساسي": primary_total_length,
                "نطاق العرض المطلوب (بقي)": f"{min_rem}..{max_rem}",
                "مرشح العرض": None,
                "مرشح الطول": p_l,
                "الكمية المطلوبة من المرشح (تقريب)": p_q,
                "كمية المرشح المتاحة": 0,
                "نقص بالقطع إن وجد": p_q,
                "فرق الطول (سم)": 0,
                "يناسب طولاً؟": "نعم (إذا كان طول المرشح = طول الأساسي)",
                "ملاحظة": "لا يوجد مرشح متاح بنفس نطاق العرض؛ تحتاج توفير عرض داخل النطاق أعلاه"
            })

        # also if primary alone fits, add a note row indicating it can be grouped by itself
        if alone_ok:
            suggestions.append({
                "معرف الأساسي": primary.id,
                "عرض الأساسي": p_w,
                "طول الأساسي": p_l,
                "كمية الأساسي المتبقية": p_q,
                "الطول الإجمالي الأساسي": primary_total_length,
                "نطاق العرض المطلوب (بقي)": "0",
                "مرشح العرض": "يمكن تشكيل مجموعة منفردة",
                "مرشح الطول": p_l,
                "الكمية المطلوبة من المرشح (تقريب)": 1,
                "كمية المرشح المتاحة": p_q,
                "نقص بالقطع إن وجد": 0,
                "فرق الطول (سم)": 0,
                "يناسب طولاً؟": "نعم",
                "ملاحظة": "العرض الأساسي وحده داخل النطاق؛ يمكن تشكيل مجموعة بدون شركاء"
            })

    return suggestions




def regroup_remainders(
    rectangles: List[Rectangle],
    min_width: float,
    max_width: float,
    tolerance_length: float,
    start_group_id: int = 10000
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية مُحسَّنة لتجميع البواقي بطريقة منطقية:
    - تقلل عدد المجموعات الناتجة.
    - تدمج عروض مختلفة (ضمن حدود min/max).
    - تراعي فرق الأطوال ضمن tolerance_length.
    - تحاول استهلاك الكميات الكبيرة تدريجياً لتقليل السجلات.
    """

    # ترتيب تنازلي حسب العرض لتبدأ بالأعرض
    rectangles = sorted(rectangles, key=lambda r: r.width, reverse=True)
    remaining_qty = {r.id: r.qty for r in rectangles}

    groups: List[Group] = []
    group_index = start_group_id

    # نحاول حتى نستهلك الكميات
    while True:
        valid_group_found = False

        # نبدأ كل مجموعة من القطع التي لا تزال متبقية
        for base in rectangles:
            if remaining_qty[base.id] <= 0:
                continue

            current_group: List[Rectangle] = []
            total_width = 0

            # نستخدم كمية مبدئية من القطعة الأساسية
            use_qty = min(remaining_qty[base.id], int(max_width // base.width))
            if use_qty == 0:
                continue

            # أضف بعضاً من القطعة الأساسية
            for _ in range(use_qty):
                if total_width + base.width > max_width:
                    break
                current_group.append(base)
                total_width += base.width

            # حاول إكمال العرض بمقاطع أخرى قريبة
            for other in rectangles:
                if remaining_qty[other.id] <= 0 or other.id == base.id:
                    continue

                # السماح بدمج إذا كان الفرق في العرض معقول (<= 40%)
                if abs(other.width - base.width) / base.width > 0.4:
                    continue

                # تحقق من فرق الأطوال ضمن السماحية
                if abs(other.length - base.length) > tolerance_length:
                    continue

                # أضف أكبر عدد ممكن من هذا النوع دون تجاوز max_width
                while remaining_qty[other.id] > 0 and total_width + other.width <= max_width:
                    current_group.append(other)
                    total_width += other.width
                    remaining_qty[other.id] -= 1

                    # إن اقتربنا من الحد الأعلى كفاية، توقف
                    if total_width >= max_width * 0.95:
                        break

                if total_width >= max_width * 0.9:
                    break

            # تحقق من صحة المجموعة
            if not (min_width <= total_width <= max_width):
                continue

            # تحقق من السماحية في الأطوال الفعلية داخل المجموعة
            lengths = [r.length for r in current_group]
            if lengths and (max(lengths) - min(lengths)) > tolerance_length:
                continue

            # ✅ تشكيل المجموعة النهائية
            usage = {}
            for r in current_group:
                usage[r.id] = usage.get(r.id, 0) + 1

            # خصم الكميات من المتبقي
            for rid, used in usage.items():
                remaining_qty[rid] -= used

            # بناء كائن Group فعلي
            used_items = [
                UsedItem(
                    rect_id=r.id,
                    width=r.width,
                    length=r.length,
                    used_qty=usage[r.id],
                    original_qty=r.qty
                )
                for r in current_group if r.id in usage
            ]

            group_index += 1
            groups.append(Group(id=group_index, items=used_items))
            valid_group_found = True

        # إذا لم يتم إنشاء أي مجموعة جديدة — توقف
        if not valid_group_found:
            break

    # إنشاء البواقي النهائية
    remaining = []
    for r in rectangles:
        if remaining_qty[r.id] > 0:
            rem = r.copy()
            rem.qty = remaining_qty[r.id]
            remaining.append(rem)

    return groups, remaining



def exhaustively_regroup(remaining: List[Rectangle],
                         min_width: int,
                         max_width: int,
                         tolerance_length: int,
                         start_group_id: int = 10000,
                         max_rounds: int = 50) -> (List[Group], List[Rectangle]): # type: ignore
    """
    استدعي regroup_remainders تكراراً حتى لا يبقى شيء قابل للتجميع.
    - remaining: قائمة البواقي الابتدائية (لن يتم تعديل ملفات الإكسل الأصلية)
    - start_group_id: بداية ترقيم مجموعات البواقي (تجنّب تداخل مع المجموعات الأصلية)
    - max_rounds: حد أمان لتجنب حلقات لا نهائية
    ترجع: (كل المجموعات المولّدة من البواقي، البواقي النهائية بعد استهلاك الممكن)
    """
    # نعمل على نسخة محلية من البواقي
    current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining if r.qty > 0]
    all_groups: List[Group] = []
    next_group_id = start_group_id
    rounds = 0

    while rounds < max_rounds:
        rounds += 1
        # استدعاء مرة واحدة: regroup_remainders يستهلك أكبر قدر ممكن (حسب تصميمه)
        formed, leftover = regroup_remainders(current_remaining, min_width, max_width, tolerance_length, start_group_id=next_group_id)

        if not formed:
            # لا أية مجموعة جديدة تشكّلت — انتهينا
            break

        # جمع المجموعات الجديدة
        all_groups.extend(formed)
        # زيادة المؤشر الابتدائي للأعرف لاستخدامه في الاستدعاء التالي (لا تداخل)
        next_group_id = (all_groups[-1].id if all_groups else next_group_id) + 1

        # تحضير الجولة التالية: البقايا المتبقية من هذه الجولة
        current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in leftover if r.qty > 0]

        # لو لم يعد هناك بواقي قابلة للاستعمال -> انتهى
        if not current_remaining:
            break

    # بعد الخروج: نعيد كل المجموعات التي كونّاها و البواقي النهائية
    final_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in current_remaining if r.qty > 0]
    return all_groups, final_remaining
