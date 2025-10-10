"""
وحدة تحسين تجميع البواقي
========================

هذه الوحدة تحتوي على الخوارزميات المتقدمة لتجميع البواقي
وإنشاء مجموعات إضافية من العناصر المتبقية.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import copy
from typing import List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
from itertools import combinations, product
import statistics

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
    
    هذه الدالة تستخدم خوارزمية ذكية لتجميع البواقي مع:
    - إمكانية تكرار العناصر في نفس المجموعة
    - البحث عن أفضل التوليفات الممكنة
    - مراعاة جميع الشروط المطلوبة
    - تحسين الأداء لتجنب التعقيد المفرط
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية المراد تجميعها
    min_width : int
        الحد الأدنى للعرض المطلوب
    max_width : int
        الحد الأقصى للعرض المسموح
    tolerance_length : int
        حدود السماحية للفرق في الطول
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
    max_rounds : int, optional
        الحد الأقصى لعدد المحاولات (افتراضي: 50)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة المشكلة
        - قائمة العناصر المتبقية بعد التجميع
        
    أمثلة:
    -------
    >>> enhanced_groups, final_remaining = create_enhanced_remainder_groups(
    >>>     remaining_items, 370, 400, 100
    >>> )
    >>> print(f"تم تشكيل {len(enhanced_groups)} مجموعة إضافية")
    """
    # نسخ العناصر لتجنب تعديل الأصلية
    current_remaining = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining if r.qty > 0]
    all_groups: List[Group] = []
    next_group_id = start_group_id
    rounds = 0

    def can_tolerate(len_a: int, qty_a: int, len_b: int, qty_b: int) -> bool:
        """فحص ما إذا كان الفرق في الطول ضمن حدود السماحية."""
        return abs(len_a * qty_a - len_b * qty_b) <= tolerance_length

    def find_best_combination(items: List[Rectangle], target_width: int, ref_length: int, ref_qty: int) -> Optional[List[Tuple[Rectangle, int]]]:
        """
        البحث عن أفضل توليفة من العناصر المتاحة.
        
        هذه الدالة تبحث عن أفضل توليفة من العناصر المتاحة
        التي تحقق الشروط المطلوبة وتقترب من العرض المثالي.
        """
        best_combination = None
        best_score = float('inf')
        
        # تجربة جميع التوليفات الممكنة (حد أقصى 4 عناصر في المجموعة)
        for r in range(1, min(len(items) + 1, 5)):
            for combo in combinations(items, r):
                # تجربة كميات مختلفة لكل عنصر
                quantities = []
                for item in combo:
                    max_qty = min(item.qty, max_width // item.width)
                    quantities.append(list(range(1, max_qty + 1)))
                
                for qty_combo in product(*quantities):
                    total_width = sum(item.width * qty for item, qty in zip(combo, qty_combo))
                    
                    # فحص حدود العرض
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

    # الحلقة الرئيسية لتشكيل المجموعات
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
            
            # تجربة كميات مختلفة من العنصر الأساسي
            max_base_qty = min(base_item.qty, max_width // base_item.width)
            
            for base_qty in range(1, max_base_qty + 1):
                # فحص ما إذا كان العنصر وحده يكفي
                if min_width <= base_item.width * base_qty <= max_width:
                  # تشكيل مجموعة من نفس العنصر مكررة base_qty مرات
                    group_items = [
                        UsedItem(
                            rect_id=base_item.id,
                            width=base_item.width,
                            length=base_item.length,
                            used_qty=1,
                            original_qty=base_item.qty
                        )
                        for _ in range(base_qty)
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
    # ✅ دمج المجموعات المتكررة قبل الإرجاع النهائي
    def normalize_group_signature(group: Group) -> Tuple:
        """توليد بصمة موحدة لكل مجموعة لتحديد المجموعات المتطابقة."""
        sig = tuple(sorted([
            (item.rect_id, item.width, item.length, item.used_qty)
            for item in group.items
        ]))
        return sig

    merged_groups = []
    signature_map = {}
    for g in all_groups:
        sig = normalize_group_signature(g)
        if sig in signature_map:
            # دمج الكميات في نفس المجموعة
            existing_group = signature_map[sig]
            for item in g.items:
                # نحاول زيادة الكمية في العناصر المتطابقة
                for e_item in existing_group.items:
                    if (e_item.rect_id == item.rect_id and 
                        e_item.width == item.width and 
                        e_item.length == item.length):
                        e_item.used_qty += item.used_qty
                        break
        else:
            signature_map[sig] = g
            merged_groups.append(g)

    all_groups = merged_groups

    final_remaining = [r for r in current_remaining if r.qty > 0]
    return all_groups, final_remaining


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
    
    هذه الدالة تستخدم الخوارزمية المحسنة مع إمكانية تكرار العناصر
    لتجميع أقصى قدر ممكن من البواقي.
    
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
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
    max_rounds : int, optional
        الحد الأقصى لعدد المحاولات (افتراضي: 50)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة
        - قائمة العناصر المتبقية بعد التجميع
    """
    return create_enhanced_remainder_groups(
        remaining, min_width, max_width, tolerance_length, start_group_id, max_rounds
    )


def calculate_group_efficiency(group: Group) -> Dict[str, float]:
    """
    حساب كفاءة المجموعة بناءً على عدة معايير.
    
    المعاملات:
    ----------
    group : Group
        المجموعة المراد حساب كفاءتها
        
    الإرجاع:
    -------
    Dict[str, float]
        قاموس يحتوي على معايير الكفاءة:
        - width_utilization: استغلال العرض
        - length_consistency: اتساق الأطوال
        - area_efficiency: كفاءة المساحة
        - overall_score: النقاط الإجمالية
    """
    if not group.items:
        return {
            'width_utilization': 0.0,
            'length_consistency': 0.0,
            'area_efficiency': 0.0,
            'overall_score': 0.0
        }
    
    # حساب استغلال العرض
    total_width = group.total_width()
    width_utilization = total_width / 400.0  # افتراض الحد الأقصى 400
    
    # حساب اتساق الأطوال
    lengths = [item.length * item.used_qty for item in group.items]
    if lengths:
        length_variance = max(lengths) - min(lengths)
        length_consistency = max(0, 1 - length_variance / max(lengths))
    else:
        length_consistency = 1.0
    
    # حساب كفاءة المساحة
    total_area = sum(item.width * item.length * item.used_qty for item in group.items)
    theoretical_max_area = total_width * max(lengths) if lengths else 0
    area_efficiency = total_area / theoretical_max_area if theoretical_max_area > 0 else 0
    
    # النقاط الإجمالية
    overall_score = (width_utilization + length_consistency + area_efficiency) / 3
    
    return {
        'width_utilization': width_utilization,
        'length_consistency': length_consistency,
        'area_efficiency': area_efficiency,
        'overall_score': overall_score
    }


def optimize_group_formation(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    max_groups: int = 100
) -> Tuple[List[Group], List[Rectangle]]:
    """
    تحسين تشكيل المجموعات باستخدام خوارزمية متقدمة.
    
    هذه الدالة تستخدم خوارزمية تحسين متقدمة لتشكيل المجموعات
    مع مراعاة عدة معايير للكفاءة.
    
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
    max_groups : int, optional
        الحد الأقصى لعدد المجموعات (افتراضي: 100)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات المحسنة
        - قائمة العناصر المتبقية
    """
    # استخدام الخوارزمية الأساسية أولاً
    groups, final_remaining = create_enhanced_remainder_groups(
        remaining, min_width, max_width, tolerance_length
    )
    
    # تحسين المجموعات المشكلة
    optimized_groups = []
    for group in groups:
        efficiency = calculate_group_efficiency(group)
        if efficiency['overall_score'] > 0.5:  # عتبة الكفاءة
            optimized_groups.append(group)
    
    return optimized_groups, final_remaining
