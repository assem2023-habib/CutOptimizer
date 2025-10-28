"""
وحدة خوارزميات التجميع
========================

تحتوي على الخوارزميات الأساسية لتشكيل مجموعات من البواقي
وإعادة تنظيمها وفقاً للشروط المحددة.
"""

from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from core.models import Rectangle, Group, UsedItem
from itertools import combinations, product
import copy
import statistics


# Helper functions extracted from create_enhanced_remainder_groups

def check_length_tolerance(ref_length: int, candidate_length: int, tolerance_length: int) -> bool:
    """التحقق من الطول المتقارب"""
    return abs(ref_length - candidate_length) <= tolerance_length


def validate_group(group_items: List[Tuple[Rectangle, int]], min_width: int, max_width: int) -> bool:
    """التحقق من صحة المجموعة قبل إنشائها"""
    if not group_items:
        return False

    # حساب العرض الإجمالي (مجموع عرض كل نوع مرة واحدة - بدون ضرب في الكمية)
    # total_width = sum(rect.width for rect, qty in group_items)
    total_width = group_items.total_width()

    # التحقق من نطاق العرض - هذا هو الشرط الأساسي
    return min_width <= total_width <= max_width


def calculate_group_quantity(group_items: List[Tuple[Rectangle, int]]) -> int:
    """حساب كمية المجموعة (حاصل ضرب الطول × العرض × العدد)"""
    total_quantity = 0
    for rect, qty in group_items:
        total_quantity += rect.width * rect.length * qty
    return total_quantity


def try_single_repeated_item(
    rect: Rectangle,
    min_width: int,
    max_width: int,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Optional[Tuple[int, int]]:
    """
    محاولة تكوين مجموعة من عنصر واحد مكرر مع مراعاة حدود الكمية
    """
    # العرض الكلي هو عرض العنصر فقط
    total_w = rect.width

    # التحقق من أن العنصر يمكن أن يحقق النطاق
    if min_width <= total_w <= max_width:
        # العنصر يحقق النطاق - استخدم أكبر كمية ممكنة
        qty = rect.qty

        group_quantity = calculate_group_quantity([(rect, qty)])

        # التحقق من حدود الكمية إذا كانت محددة
        if min_group_quantity and group_quantity < min_group_quantity:
            return None
        if max_group_quantity and group_quantity > max_group_quantity:
            return None

        return (qty, total_w)

    return None


def find_partners_combination(
    base_rect: Rectangle,
    remaining_items: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Optional[List[Tuple[Rectangle, int]]]:
    """
    البحث عن شركاء لتشكيل مجموعة - أولوية للتنويع قبل التكرار
    """
    # ترتيب العناصر حسب العرض من الأكبر للأصغر
    sorted_items = sorted(
        [r for r in remaining_items if r.qty > 0],
        key=lambda r: r.width,
        reverse=True
    )

    best_combination = None
    best_score = 0

    # جرب كميات مختلفة من العنصر الأساسي
    max_base_qty = base_rect.qty

    for base_qty in range(max_base_qty, 0, -1):
        base_total_width = base_rect.width
        ref_length = base_rect.length * base_qty

        # إذا كان العنصر الأساسي يحقق النطاق بمفرده
        if min_width <= base_total_width <= max_width:
            combination = [(base_rect, base_qty)]
            group_quantity = calculate_group_quantity(combination)

            if (not min_group_quantity or group_quantity >= min_group_quantity) and \
               (not max_group_quantity or group_quantity <= max_group_quantity):
                score = group_quantity
                if score > best_score:
                    best_score = score
                    best_combination = combination.copy()

        # البحث عن شركاء
        combination = [(base_rect, base_qty)]
        current_width = base_total_width
        used_qty = {base_rect.id: base_qty}

        for candidate in sorted_items:
            if candidate.qty <= 0:
                continue

            if current_width + candidate.width > max_width:
                continue

            already_used = used_qty.get(candidate.id, 0)
            available_qty = candidate.qty - already_used

            if available_qty <= 0:
                continue

            max_candidate_qty = available_qty

            for candidate_qty in range(max_candidate_qty, 0, -1):
                new_width = current_width + candidate.width
                candidate_total_length = candidate.length * candidate_qty

                if new_width > max_width:
                    continue

                if check_length_tolerance(ref_length, candidate_total_length, tolerance_length):
                    test_combination = combination + [(candidate, candidate_qty)]
                    test_width = sum(r.width for r, q in test_combination)

                    if min_width <= test_width <= max_width:
                        group_quantity = calculate_group_quantity(test_combination)

                        if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                           (not max_group_quantity or group_quantity <= max_group_quantity):
                            diversity_score = len(test_combination)
                            score = group_quantity * diversity_score

                            if score > best_score:
                                best_score = score
                                best_combination = test_combination.copy()

                        used_qty[candidate.id] = already_used + candidate_qty
                        combination = test_combination
                        current_width = test_width
                        break

    if best_combination:
        return best_combination

    # إذا لم نحقق، جرب التكرار
    return find_combination_with_repetition(
        base_rect, remaining_items, min_width, max_width, tolerance_length,
        min_group_quantity, max_group_quantity
    )


def find_combination_with_repetition(
    base_rect: Rectangle,
    remaining_items: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Optional[List[Tuple[Rectangle, int]]]:
    """البحث عن تركيبة مع السماح بالتكرار عند الضرورة"""
    sorted_items = sorted(
        [r for r in remaining_items if r.qty > 0],
        key=lambda r: r.width,
        reverse=True
    )

    best_combination = None
    best_score = 0

    max_base_qty = base_rect.qty
    for base_qty in range(max_base_qty, 0, -1):
        base_total_width = base_rect.width
        ref_length = base_rect.length * base_qty

        if min_width <= base_total_width <= max_width:
            combination = [(base_rect, base_qty)]
            group_quantity = calculate_group_quantity(combination)

            if (not min_group_quantity or group_quantity >= min_group_quantity) and \
               (not max_group_quantity or group_quantity <= max_group_quantity):
                score = group_quantity
                if score > best_score:
                    best_score = score
                    best_combination = combination.copy()

        combination = [(base_rect, base_qty)]
        current_width = base_total_width
        used_qty = {base_rect.id: base_qty}

        for candidate in sorted_items:
            if candidate.qty <= 0:
                continue

            if current_width + candidate.width > max_width:
                continue

            already_used = used_qty.get(candidate.id, 0)
            available_qty = candidate.qty - already_used

            if available_qty <= 0:
                continue

            max_candidate_qty = available_qty

            for candidate_qty in range(max_candidate_qty, 0, -1):
                candidate_total_length = candidate.length * candidate_qty

                if check_length_tolerance(ref_length, candidate_total_length, tolerance_length):
                    new_width = current_width + candidate.width

                    if min_width <= new_width <= max_width:
                        test_combination = combination + [(candidate, candidate_qty)]
                        group_quantity = calculate_group_quantity(test_combination)

                        if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                           (not max_group_quantity or group_quantity <= max_group_quantity):
                            score = group_quantity
                            if score > best_score:
                                best_score = score
                                best_combination = test_combination.copy()

                        used_qty[candidate.id] = already_used + candidate_qty
                        combination = test_combination
                        current_width = new_width
                        break

    return best_combination


def create_enhanced_remainder_groups(
    remaining: List[Rectangle],
    width_ranges: List[Tuple[int, int]],
    tolerance_length: int,
    start_group_id: int = 1,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """
    خوارزمية محسّنة لتشكيل مجموعات من العناصر المتبقية
    """
    # نسخ العناصر المتبقية
    current_remaining = [
        Rectangle(r.id, r.width, r.length, r.qty)
        for r in remaining if r.qty > 0
    ]

    total_quantity_before = sum(rect.width * rect.length * rect.qty for rect in current_remaining)

    all_groups: List[Group] = []
    next_group_id = start_group_id

    # معالجة كل نطاق عرض
    for min_width, max_width in width_ranges:
        max_rounds = 100
        round_count = 0

        while round_count < max_rounds and current_remaining:
            round_count += 1

            current_remaining = [r for r in current_remaining if r.qty > 0]
            if not current_remaining:
                break

            current_remaining.sort(key=lambda r: r.width, reverse=True)

            created_group = False

            for base_rect in current_remaining:
                if base_rect.qty <= 0:
                    continue

                combination = find_partners_combination(
                    base_rect,
                    current_remaining,
                    min_width,
                    max_width,
                    tolerance_length,
                    min_group_quantity,
                    max_group_quantity
                )

                if combination:
                    group_items = []
                    temp_quantities = {}
                    total_qty_per_rect = {}

                    for rect, qty in combination:
                        if rect.id not in temp_quantities:
                            temp_quantities[rect.id] = rect.qty
                            total_qty_per_rect[rect.id] = 0
                        total_qty_per_rect[rect.id] += qty

                    valid_combination = True
                    for rect_id, total_needed in total_qty_per_rect.items():
                        if total_needed > temp_quantities[rect_id]:
                            valid_combination = False
                            break

                    if not valid_combination:
                        continue

                    processed_rects = {}
                    for rect, qty in combination:
                        for current_rect in current_remaining:
                            if current_rect.id == rect.id:
                                if rect.id not in processed_rects:
                                    actual_used = min(current_rect.qty, total_qty_per_rect[rect.id])
                                    current_rect.qty -= actual_used

                                    group_items.append(
                                        UsedItem(
                                            rect_id=rect.id,
                                            width=rect.width,
                                            length=rect.length,
                                            used_qty=actual_used,
                                            original_qty=temp_quantities[rect.id]
                                        )
                                    )
                                    processed_rects[rect.id] = True
                                break

                    if group_items:
                        new_group = Group(id=next_group_id, items=group_items)
                        total_width = new_group.total_width()

                        if min_width <= total_width <= max_width:
                            all_groups.append(new_group)
                            next_group_id += 1
                            created_group = True
                            break
                        else:
                            for item in group_items:
                                for rect in current_remaining:
                                    if rect.id == item.rect_id:
                                        rect.qty += item.used_qty
                                        break

            if not created_group:
                for base_rect in current_remaining:
                    if base_rect.qty <= 0:
                        continue

                    if min_width <= base_rect.width <= max_width:
                        qty_to_use = base_rect.qty

                        group_quantity = calculate_group_quantity([(base_rect, qty_to_use)])
                        if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                           (not max_group_quantity or group_quantity <= max_group_quantity):

                            group_items = [
                                UsedItem(
                                    rect_id=base_rect.id,
                                    width=base_rect.width,
                                    length=base_rect.length,
                                    used_qty=qty_to_use,
                                    original_qty=base_rect.qty
                                )
                            ]

                            new_group = Group(id=next_group_id, items=group_items)

                            if min_width <= new_group.total_width() <= max_width:
                                base_rect.qty -= qty_to_use

                                all_groups.append(new_group)
                                next_group_id += 1
                                created_group = True
                                break

            if not created_group:
                break

    final_remaining = [r for r in current_remaining if r.qty > 0]
    total_quantity_after = sum(rect.width * rect.length * rect.qty for rect in final_remaining)
    total_quantity_used = total_quantity_before - total_quantity_after

    quantity_stats = {
        'total_quantity_before': total_quantity_before,
        'total_quantity_after': total_quantity_after,
        'total_quantity_used': total_quantity_used,
        'utilization_percentage': (total_quantity_used / total_quantity_before * 100) if total_quantity_before > 0 else 0,
        'groups_created': len(all_groups),
        'remaining_items_count': len(final_remaining)
    }

    return all_groups, final_remaining, quantity_stats


def exhaustively_regroup(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """دالة مساعدة لإعادة تجميع البواقي باستخدام نطاق عرض واحد"""
    width_ranges = [(min_width, max_width)]

    return create_enhanced_remainder_groups(
        remaining,
        width_ranges,
        tolerance_length,
        start_group_id,
        min_group_quantity,
        max_group_quantity
    )


def process_remainder_complete(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    merge_after: bool = True,
    verbose: bool = True,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """نظام متكامل: تشكيل البواقي ثم دمج المجموعات المتطابقة"""
    from .group_merging import merge_identical_groups  # Import here to avoid circular import

    groups, final_remaining, quantity_stats = exhaustively_regroup(
        remaining,
        min_width,
        max_width,
        tolerance_length,
        start_group_id,
        min_group_quantity=min_group_quantity,
        max_group_quantity=max_group_quantity
    )

    if merge_after and len(groups) > 0:
        groups = merge_identical_groups(groups, tolerance_length, verbose)

    return groups, final_remaining, quantity_stats


def create_enhanced_remainder_groups_from_rectangles(
    remaining_rectangles: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """دالة مساعدة لإنشاء مجموعات إضافية محسنة من قائمة Rectangle."""
    return create_enhanced_remainder_groups(
        remaining_rectangles,
        [(min_width, max_width)],
        tolerance_length,
        start_group_id,
        min_group_quantity,
        max_group_quantity
    )
