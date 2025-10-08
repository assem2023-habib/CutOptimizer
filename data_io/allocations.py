"""
وحدة تخصيص الكميات للمجموعات
============================

تقوم هذه الوحدة بحساب الكميات المستخدمة من كل نوع سجاد داخل كل مجموعة،
وفقاً لحدود العرض (min_width, max_width) ومعامل التحمل (tolerance).

المؤلف: نظام تحسين القطع
التاريخ: 2025
"""

from typing import List, Dict
from core.models import Rectangle, Group
import math


def allocate_used_quantities(groups: List[Group], min_width: float, max_width: float, tolerance: float) -> List[Dict]:
    """
    حساب الكميات المستخدمة لكل مجموعة من المستطيلات.

    المعاملات:
    ----------
    groups : List[Group]
        قائمة المجموعات التي تحتوي على المستطيلات.
    min_width : float
        أقل عرض مقبول في التشكيل.
    max_width : float
        أكبر عرض مقبول في التشكيل.
    tolerance : float
        معامل التحمل المسموح به عند حساب الكميات النسبية.

    الإرجاع:
    -------
    List[Dict]
        قائمة من القواميس تحتوي على نتائج كل مجموعة بالشكل:
        [
            {
                "group_id": 1,
                "width_avg": 370,
                "used_items": [
                    {"rect_id": 1, "width": 362, "qty_used": 32},
                    {"rect_id": 5, "width": 368, "qty_used": 12}
                ]
            },
            ...
        ]
    """

    results = []

    for group in groups:
        if not group.items:
            continue

        # --- حساب متوسط العرض للمجموعة ---
        widths = [r.width for r in group.items]
        W_avg = sum(widths) / len(widths)

        # --- تحديد حدود العرض المسموح بها داخل المجموعة ---
        W_min = max(min_width, W_avg - tolerance)
        W_max = min(max_width, W_avg + tolerance)

        # --- استخراج العناصر المؤهلة ---
        eligible = [r for r in group.items if W_min <= r.width <= W_max]
        if not eligible:
            continue

        # --- حساب الوزن النسبي لكل عنصر ---
        raw_ratios = []
        for r in eligible:
            # القرب من المتوسط
            closeness = 1 - abs(r.width - W_avg) / (W_max - W_min) if W_max != W_min else 1
            raw_ratios.append(max(0, closeness))

        total_ratio = sum(raw_ratios) or 1
        normalized_ratios = [r / total_ratio for r in raw_ratios]

        # --- تخصيص الكميات ---
        used_items = []
        for rect, ratio in zip(eligible, normalized_ratios):
            qty_used = math.floor(rect.qty * ratio)
            qty_used = max(1, qty_used) if rect.qty > 0 else 0
            qty_used = min(qty_used, rect.qty)
            used_items.append({
                "rect_id": rect.id,
                "width": rect.width,
                "length": rect.length,
                "qty_used": qty_used,
                "qty_original": rect.qty
            })

        # --- حفظ نتائج المجموعة ---
        results.append({
            "group_id": getattr(group, "id", None),
            "width_avg": round(W_avg, 2),
            "allowed_range": (W_min, W_max),
            "used_items": used_items
        })

    return results
