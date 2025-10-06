import pandas as pd
from typing import  List, Dict, Optional
from core.models import Rectangle, Group, UsedItem
import os
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name
from collections import defaultdict

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
    computed_remainder_groups, computed_remaining_after = regroup_remainders(
        remaining, min_width, max_width, tolerance_length
    )
    # إذا caller مرر remainder_groups في باراميتر الدالة، نستخدمه؛ وإلا نستخدم المحسوب
    to_write_remainder_groups = remainder_groups if remainder_groups is not None else computed_remainder_groups
    to_write_remaining_after = computed_remaining_after
    

    # ---------------------------
    #  الآن كتابة الأوراق في الملف
    # ---------------------------
    
    # ---------------------------
    #  جديد: كتابة مجموعات البواقي (إن وُجدت)
    # ---------------------------
    # if remainder_groups:
    #     rem_group_rows = []
    #     for g in remainder_groups:
    #         for it in g.items:
    #             rem_group_rows.append({
    #                 'رقم المجموعة' : f'باقي_{g.id}',
    #                 'معرف السجاد' : it.rect_id,
    #                 'العرض' : it.width,
    #                 'الطول' : it.length,
    #                 'الكمية المستخدمة' : it.used_qty,
    #                 'الطول الاجمالي للسجادة' : it.length * it.used_qty,
    #                 'الكمية الأصلية' : it.original_qty
    #             })
    #     df_rem_groups = pd.DataFrame(rem_group_rows)
    #     # اكتب الـ DataFrame أولاً ثم أضف صف المجموع
    #     df_rem_groups.to_excel(writer, sheet_name='مجموعات من البواقي', index=False)
    #     _append_totals_row(writer, 'مجموعات من البواقي', df_rem_groups)
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
            df_remaining_after.to_excel(writer, sheet_name='بواقي نهائية', index=False)
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


def regroup_remainders(remaining: List[Rectangle],
                       min_width: int,
                       max_width: int,
                       tolerance_length: int,
                       start_group_id: int = 10000) -> (List[Group], List[Rectangle]):  # type: ignore
    """
    خوارزمية إعادة التجميع للبواقي (الإصدار المطور).
    - تكرر العنصر نفسه ضمن المجموعة إذا لزم الأمر.
    - تحاول استخراج أقصى عدد من المجموعات الممكنة.
    - تتوقف فقط إذا لم تعد أي توليفة تحقق الشروط.
    """
    remainders = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining if r.qty > 0]
    if not remainders:
        return [], []

    # ترتيب حسب العرض تنازلياً
    remainders.sort(key=lambda x: x.width, reverse=True)

    id_map = {r.id: r for r in remainders}
    remaining_qty: Dict[int, int] = {r.id: r.qty for r in remainders}
    widths_map = defaultdict(list)
    for r in remainders:
        widths_map[r.width].append(r.id)

    groups: List[Group] = []
    group_id = start_group_id

    safety = 0
    max_iters = 10000
    progress = True  # لتتبع ما إذا تم إنشاء أي مجموعة في الدورة

    while progress and safety < max_iters:
        safety += 1
        progress = False  # نفترض مبدئيًا أنه لن تُنشأ مجموعة هذه الدورة

        for primary in remainders:
            if remaining_qty.get(primary.id, 0) <= 0:
                continue

            primary_avail = remaining_qty[primary.id]

            # نحاول أكثر من مجموعة من نفس العنصر طالما هناك كمية متبقية
            while remaining_qty.get(primary.id, 0) > 0:
                made_group = False

                for use_primary in range(min(primary_avail, 50), 0, -1):  # جرب حتى 50 وحدة دفعة واحدة
                    if remaining_qty[primary.id] < use_primary:
                        continue

                    ref_total_len = primary.length * use_primary
                    chosen_items: List[UsedItem] = [UsedItem(primary.id, primary.width, primary.length, use_primary, primary.qty)]
                    chosen_width = primary.width

                    temp_qty = dict(remaining_qty)
                    temp_qty[primary.id] -= use_primary

                    candidate_widths = sorted(widths_map.keys(), reverse=True)

                    for w in candidate_widths:
                        if chosen_width + w > max_width:
                            continue
                        for cid in widths_map[w]:
                            avail = temp_qty.get(cid, 0)
                            if avail <= 0:
                                continue

                            cand = id_map[cid]
                            desired_qty = max(1, int(round(ref_total_len / cand.length)))
                            take = min(desired_qty, avail)

                            if take <= 0:
                                continue

                            cand_total_len = cand.length * take
                            diff = abs(cand_total_len - ref_total_len)

                            if diff <= tolerance_length and chosen_width + cand.width <= max_width:
                                chosen_items.append(UsedItem(cid, cand.width, cand.length, take, cand.qty))
                                chosen_width += cand.width
                                temp_qty[cid] -= take

                                if chosen_width >= min_width:
                                    break
                        if chosen_width >= min_width:
                            break

                    # تحقق صلاحية المجموعة
                    if min_width <= chosen_width <= max_width:
                        for it in chosen_items:
                            remaining_qty[it.rect_id] = max(0, remaining_qty.get(it.rect_id, 0) - it.used_qty)
                            if it.rect_id in id_map:
                                id_map[it.rect_id].qty = remaining_qty[it.rect_id]
                        groups.append(Group(group_id, chosen_items))
                        group_id += 1
                        made_group = True
                        progress = True
                        break  # انتهت هذه المجموعة، جرب التالية

                if not made_group:
                    break  # لم ننجح بتكوين أي مجموعة إضافية من هذا العنصر، انتقل لعنصر آخر

        # تنظيف العناصر التي نفدت كمياتها
        keys_to_remove = [k for k, v in remaining_qty.items() if v <= 0]
        for k in keys_to_remove:
            remaining_qty.pop(k, None)

    # إعداد البواقي النهائية
    remaining_after = []
    for r in remainders:
        q = remaining_qty.get(r.id, 0)
        if q > 0:
            remaining_after.append(Rectangle(r.id, r.width, r.length, q))

    return groups, remaining_after