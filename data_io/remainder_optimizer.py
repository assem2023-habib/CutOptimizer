"""
وحدة تحسين تجميع البواقي
========================

هذه الوحدة تحتوي على الخوارزميات المتقدمة لتجميع البواقي
وإنشاء مجموعات إضافية من العناصر المتبقية.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from core.models import Rectangle, Group, UsedItem
from itertools import combinations, product
import copy
import statistics

# ═══════════════════════════════════════════════════════════════════════════════
# الدالة الأساسية: تشكيل مجموعات من البواقي
# ═══════════════════════════════════════════════════════════════════════════════

def create_enhanced_remainder_groups(
    remaining: List[Rectangle],
    width_ranges: List[Tuple[int, int]],
    tolerance_length: int,
    start_group_id: int = 1
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية محسّنة لتشكيل مجموعات من العناصر المتبقية
    
    تقبل قائمة من نطاقات العرض وتعالج كل نطاق بشكل منفصل
    """
    
    current_remaining = [
        Rectangle(r.id, r.width, r.length, r.qty) 
        for r in remaining if r.qty > 0
    ]
    
    all_groups: List[Group] = []
    next_group_id = start_group_id
    
    def check_length_tolerance(ref_length: int, candidate_length: int) -> bool:
        """التحقق من الطول المتقارب"""
        return abs(ref_length - candidate_length) <= tolerance_length
    
    def try_single_repeated_item(
        rect: Rectangle, 
        min_width: int, 
        max_width: int
    ) -> Optional[Tuple[int, int]]:
        """محاولة تكوين مجموعة من عنصر واحد مكرر"""
        max_possible_qty = max_width // rect.width
        max_usable_qty = min(rect.qty, max_possible_qty)
        
        for qty in range(max_usable_qty, 0, -1):
            total_w = rect.width * qty
            if min_width <= total_w <= max_width:
                return (qty, total_w)
        
        return None
    
    def find_partner_items(
        base_rect: Rectangle,
        base_qty: int,
        remaining_items: List[Rectangle],
        min_width: int,
        max_width: int,
        tolerance: int
    ) -> Optional[List[Tuple[Rectangle, int]]]:
        """البحث عن عناصر شريكة لإكمال المجموعة"""
        
        ref_length = base_rect.length * base_qty
        base_total_width = base_rect.width * base_qty
        remaining_width_min = min_width - base_total_width
        remaining_width_max = max_width - base_total_width
        
        if remaining_width_min <= 0 <= remaining_width_max:
            return []
        
        if remaining_width_min > 0:
            partners = []
            current_width = base_total_width
            
            sorted_items = sorted(
                remaining_items, 
                key=lambda r: r.width, 
                reverse=True
            )
            
            for candidate in sorted_items:
                if candidate.qty <= 0:
                    continue
                
                if candidate.width > remaining_width_max - current_width:
                    continue
                
                max_candidate_qty = min(
                    candidate.qty,
                    (remaining_width_max - current_width) // candidate.width
                )
                
                for candidate_qty in range(max_candidate_qty, 0, -1):
                    candidate_total_length = candidate.length * candidate_qty
                    
                    if check_length_tolerance(ref_length, candidate_total_length):
                        new_width = current_width + candidate.width * candidate_qty
                        if min_width <= new_width <= max_width:
                            partners.append((candidate, candidate_qty))
                            current_width = new_width
                            break
                
                if min_width <= current_width <= max_width:
                    return partners
            
            if current_width < min_width:
                return None
            
            return partners
        
        return []
    
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
            
            # محاولة عنصر واحد مكرر
            for base_rect in current_remaining:
                if base_rect.qty <= 0:
                    continue
                
                result = try_single_repeated_item(
                    base_rect, min_width, max_width
                )
                
                if result:
                    qty_used, total_w = result
                    
                    group_items = []
                    for _ in range(qty_used):
                        group_items.append(
                            UsedItem(
                                rect_id=base_rect.id,
                                width=base_rect.width,
                                length=base_rect.length,
                                used_qty=1,
                                original_qty=base_rect.qty
                            )
                        )
                    
                    new_group = Group(id=next_group_id, items=group_items)
                    all_groups.append(new_group)
                    next_group_id += 1
                    
                    base_rect.qty -= qty_used
                    created_group = True
                    break
            
            if created_group:
                continue
            
            # محاولة عنصر أساسي + شركاء
            for i, base_rect in enumerate(current_remaining):
                if base_rect.qty <= 0:
                    continue
                
                max_base_qty = min(
                    base_rect.qty,
                    max_width // base_rect.width
                )
                
                for base_qty in range(max_base_qty, 0, -1):
                    other_items = [
                        r for j, r in enumerate(current_remaining)
                        if j != i and r.qty > 0
                    ]
                    
                    partners = find_partner_items(
                        base_rect,
                        base_qty,
                        other_items,
                        min_width,
                        max_width,
                        tolerance_length
                    )
                    
                    if partners is not None:
                        group_items = [
                            UsedItem(
                                rect_id=base_rect.id,
                                width=base_rect.width,
                                length=base_rect.length,
                                used_qty=base_qty,
                                original_qty=base_rect.qty
                            )
                        ]
                        
                        for partner_rect, partner_qty in partners:
                            group_items.append(
                                UsedItem(
                                    rect_id=partner_rect.id,
                                    width=partner_rect.width,
                                    length=partner_rect.length,
                                    used_qty=partner_qty,
                                    original_qty=partner_rect.qty
                                )
                            )
                            partner_rect.qty -= partner_qty
                        
                        new_group = Group(id=next_group_id, items=group_items)
                        all_groups.append(new_group)
                        next_group_id += 1
                        
                        base_rect.qty -= base_qty
                        created_group = True
                        break
                
                if created_group:
                    break
            
            if not created_group:
                break
    
    final_remaining = [r for r in current_remaining if r.qty > 0]
    
    return all_groups, final_remaining


# ═══════════════════════════════════════════════════════════════════════════════
# الدالة المساعدة: استدعاء بنطاق عرض واحد (للاستخدام البسيط)
# ═══════════════════════════════════════════════════════════════════════════════

def exhaustively_regroup(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة مساعدة لإعادة تجميع البواقي باستخدام نطاق عرض واحد
    
    هذه الدالة تحويل بسيط للدالة الأساسية
    لتقبل (min_width, max_width) بدلاً من قائمة نطاقات
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
    start_group_id : int
        رقم المجموعة الأولى (افتراضي: 10000)
    max_rounds : int
        الحد الأقصى للمحاولات (افتراضي: 50)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        (المجموعات الجديدة، البواقي النهائي)
    
    مثال:
    -----
    >>> groups, remaining = exhaustively_regroup(
    ...     remaining_items,
    ...     min_width=370,
    ...     max_width=400,
    ...     tolerance_length=100,
    ...     start_group_id=1001
    ... )
    """
    # تحويل النطاق الواحد إلى قائمة نطاقات
    width_ranges = [(min_width, max_width)]
    
    # استدعاء الدالة الأساسية
    return create_enhanced_remainder_groups(
        remaining,
        width_ranges,
        tolerance_length,
        start_group_id
    )


# ═══════════════════════════════════════════════════════════════════════════════
# دالة الدمج: دمج المجموعات المتطابقة
# ═══════════════════════════════════════════════════════════════════════════════

def get_group_signature(group: Group) -> str:
    """إرجاع بصمة فريدة للمجموعة"""
    signature_parts = []
    for item in group.items:
        part = f"{item.rect_id}_{item.width}_{item.length}"
        signature_parts.append(part)
    return "|".join(signature_parts)


def merge_identical_groups(
    groups: List[Group],
    tolerance: int = 100,
    verbose: bool = True
) -> List[Group]:
    """
    دمج المجموعات المتطابقة مع دمج الكميات
    
    المعاملات:
    ----------
    groups : List[Group]
        المجموعات المراد دمجها
    tolerance : int
        حد السماحية للطول المرجعي
    verbose : bool
        طباعة التفاصيل أم لا
        
    الإرجاع:
    -------
    List[Group]
        المجموعات بعد الدمج
    """
    
    groups_by_signature: Dict[str, List[Group]] = {}
    
    for group in groups:
        signature = get_group_signature(group)
        
        if signature not in groups_by_signature:
            groups_by_signature[signature] = []
        
        groups_by_signature[signature].append(group)
    
    merged_groups: List[Group] = []
    merge_count = 0
    
    for signature, similar_groups in groups_by_signature.items():
        
        if len(similar_groups) == 1:
            merged_groups.append(similar_groups[0])
            continue
        
        # التحقق من الطول المرجعي
        ref_lengths = [g.ref_length() for g in similar_groups]
        
        if max(ref_lengths) - min(ref_lengths) > tolerance:
            for group in similar_groups:
                merged_groups.append(group)
            continue
        
        # دمج الكميات
        base_group = similar_groups[0]
        
        total_qty_by_item: Dict[Tuple[int, int, int], int] = {}
        
        for group in similar_groups:
            for item in group.items:
                key = (item.rect_id, item.width, item.length)
                total_qty_by_item[key] = total_qty_by_item.get(key, 0) + item.used_qty
        
        merged_items_list: List[UsedItem] = []
        
        for item in base_group.items:
            key = (item.rect_id, item.width, item.length)
            total_qty = total_qty_by_item[key]
            
            merged_item = UsedItem(
                rect_id=item.rect_id,
                width=item.width,
                length=item.length,
                used_qty=total_qty,
                original_qty=item.original_qty
            )
            
            merged_items_list.append(merged_item)
        
        merged_group = Group(
            id=base_group.id,
            items=merged_items_list
        )
        
        merged_groups.append(merged_group)
        merge_count += 1
    
    return merged_groups


# ═══════════════════════════════════════════════════════════════════════════════
# النظام المتكامل
# ═══════════════════════════════════════════════════════════════════════════════

def process_remainder_complete(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    merge_after: bool = True,
    verbose: bool = True
) -> Tuple[List[Group], List[Rectangle]]:
    """
    نظام متكامل: تشكيل البواقي ثم دمج المجموعات المتطابقة
    
    هذه هي الدالة الرئيسية التي تستخدمها في الكود الرئيسي
    
    مثال الاستخدام:
    ───────────────
    rem_groups, rem_final_remaining = process_remainder_complete(
        remaining,
        min_width=370,
        max_width=400,
        tolerance_length=100,
        start_group_id=max([g.id for g in groups] + [0]) + 1,
        merge_after=True,
        verbose=True
    )
    """
    
    
    # المرحلة 1: التشكيل
    groups, final_remaining = exhaustively_regroup(
        remaining,
        min_width,
        max_width,
        tolerance_length,
        start_group_id
    )

    # المرحلة 2: الدمج
    if merge_after and len(groups) > 0:
        groups = merge_identical_groups(groups, tolerance_length, verbose)
    
    return groups, final_remaining


def create_enhanced_remainder_groups_from_rectangles(
    remaining_rectangles: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000
) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة مساعدة لإنشاء مجموعات إضافية محسنة من قائمة Rectangle.
    
    هذه الدالة توفر واجهة سهلة الاستخدام لإنشاء مجموعات إضافية
    من البواقي مع إمكانية تكرار العناصر.
    
    المعاملات:
    ----------
    remaining_rectangles : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض  
    tolerance_length : int
        حدود السماحية للطول
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة
        - قائمة العناصر المتبقية بعد التجميع
        
    أمثلة:
    -------
    >>> enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
    >>>     remaining_items, 370, 400, 100
    >>> )
    """
    return create_enhanced_remainder_groups(
        remaining_rectangles, min_width, max_width, tolerance_length, start_group_id
    )