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


def create_enhanced_remainder_groups(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    🏆 خوارزمية محسّنة لتشكيل مجموعات من العناصر المتبقية
    
    الميزات:
    ✓ تشكيل مجموعات تحقق شرط نطاق العرض (min_width ≤ total_width ≤ max_width)
    ✓ احترام tolerance الطول: |len₁×qty₁ - len₂×qty₂| ≤ tolerance
    ✓ إمكانية تكرار نفس العنصر عدة مرات في نفس المجموعة
    ✓ استخدام أقصى كمية ممكنة دون إخلال بالشروط
    ✓ معالجة عدة نطاقات عرض متتالية
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    width_ranges : List[Tuple[int, int]]
        قائمة نطاقات العرض [(min1, max1), (min2, max2), ...]
    tolerance_length : int
        حد السماحية للفرق في الطول الإجمالي (±)
    start_group_id : int
        رقم المجموعة الأولى
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        (المجموعات الجديدة، العناصر المتبقية بعد التشكيل)
    """
    width_ranges: List[Tuple[int, int]] = [min_width, max_width],
    # نسخ البيانات لتجنب تعديل الأصلية
    current_remaining = [
        Rectangle(r.id, r.width, r.length, r.qty) 
        for r in remaining if r.qty > 0
    ]
    
    all_groups: List[Group] = []
    next_group_id = start_group_id
    
    # ═══════════════════════════════════════════════════════════════
    # دالة مساعدة: فحص إذا كان الطول الإجمالي متقارباً
    # ═══════════════════════════════════════════════════════════════
    
    def check_length_tolerance(ref_length: int, candidate_length: int) -> bool:
        """
        التحقق من أن الفرق في الطول ضمن حدود السماحية
        |ref_length - candidate_length| ≤ tolerance
        """
        return abs(ref_length - candidate_length) <= tolerance_length
    
    # ═══════════════════════════════════════════════════════════════
    # دالة مساعدة: البحث عن أفضل توليفة من عنصر واحد مكرر
    # ═══════════════════════════════════════════════════════════════
    
    def try_single_repeated_item(
        rect: Rectangle, 
        min_width: int, 
        max_width: int
    ) -> Optional[Tuple[int, int]]:
        """
        محاولة تكوين مجموعة من عنصر واحد مكرر عدة مرات
        
        الإرجاع: (used_qty, total_width) أو None
        """
        # الكمية القصوى التي يمكن أخذها بناءً على العرض
        max_possible_qty = max_width // rect.width
        max_usable_qty = min(rect.qty, max_possible_qty)
        
        # البحث عن أفضل كمية تحقق النطاق
        # نبدأ من الكمية الأكبر لتعظيم الاستخدام
        for qty in range(max_usable_qty, 0, -1):
            total_w = rect.width * qty
            if min_width <= total_w <= max_width:
                return (qty, total_w)
        
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # دالة مساعدة: البحث عن شركاء لإكمال العرض
    # ═══════════════════════════════════════════════════════════════
    
    def find_partner_items(
        base_rect: Rectangle,
        base_qty: int,
        remaining_items: List[Rectangle],
        min_width: int,
        max_width: int,
        tolerance: int
    ) -> Optional[List[Tuple[Rectangle, int]]]:
        """
        البحث عن عناصر (من نفس النوع أو أنواع أخرى) لإكمال المجموعة
        
        الخطوات:
        1. حساب الطول المرجعي من العنصر الأساسي
        2. حساب العرض المتبقي المطلوب
        3. تجربة إضافة عناصر (مع إمكانية التكرار)
        
        الإرجاع: قائمة (عنصر، كمية) أو None
        """
        
        ref_length = base_rect.length * base_qty
        base_total_width = base_rect.width * base_qty
        remaining_width_min = min_width - base_total_width
        remaining_width_max = max_width - base_total_width
        
        # إذا كان العنصر الأساسي وحده يكفي
        if remaining_width_min <= 0 <= remaining_width_max:
            return []
        
        # إذا كنا بحاجة لمزيد من العرض
        if remaining_width_min > 0:
            partners = []
            current_width = base_total_width
            
            # ترتيب العناصر حسب العرض (الأكبر أولاً)
            sorted_items = sorted(
                remaining_items, 
                key=lambda r: r.width, 
                reverse=True
            )
            
            # محاولة إضافة عناصر
            for candidate in sorted_items:
                if candidate.qty <= 0:
                    continue
                
                # التحقق من أن العرض مناسب
                if candidate.width > remaining_width_max - current_width:
                    continue
                
                # محاولة تكرار العنصر عدة مرات
                max_candidate_qty = min(
                    candidate.qty,
                    (remaining_width_max - current_width) // candidate.width
                )
                
                # نبحث عن أفضل كمية
                for candidate_qty in range(max_candidate_qty, 0, -1):
                    candidate_total_length = candidate.length * candidate_qty
                    
                    # فحص tolerance الطول
                    if check_length_tolerance(ref_length, candidate_total_length):
                        # فحص العرض
                        new_width = current_width + candidate.width * candidate_qty
                        if min_width <= new_width <= max_width:
                            partners.append((candidate, candidate_qty))
                            current_width = new_width
                            break
                
                # هل وصلنا للعرض المطلوب؟
                if min_width <= current_width <= max_width:
                    return partners
            
            # إذا لم نستطع الوصول للحد الأدنى، فشل البحث
            if current_width < min_width:
                return None
            
            return partners
        
        return []
    
    # ═══════════════════════════════════════════════════════════════
    # الحلقة الرئيسية: معالجة كل نطاق عرض
    # ═══════════════════════════════════════════════════════════════
    
    for min_width, max_width in width_ranges:
        max_rounds = 100  # حد أقصى للمحاولات لكل نطاق
        round_count = 0
        
        while round_count < max_rounds and current_remaining:
            round_count += 1
            
            # إزالة العناصر التي نفدت
            current_remaining = [r for r in current_remaining if r.qty > 0]
            if not current_remaining:
                break
            
            # ترتيب حسب العرض (من الأكبر للأصغر)
            current_remaining.sort(key=lambda r: r.width, reverse=True)
            
            created_group = False
            
            # ═══════════════════════════════════════════════════════
            # المحاولة 1: عنصر واحد مكرر عدة مرات
            # ═══════════════════════════════════════════════════════
            
            for base_rect in current_remaining:
                if base_rect.qty <= 0:
                    continue
                
                result = try_single_repeated_item(
                    base_rect, min_width, max_width
                )
                
                if result:
                    qty_used, total_w = result
                    
                    # إنشاء المجموعة (تكرار العنصر نفسه)
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
                    
                    # تحديث الكمية
                    base_rect.qty -= qty_used
                    created_group = True
                    break
            
            if created_group:
                continue
            
            # ═══════════════════════════════════════════════════════
            # المحاولة 2: عنصر أساسي + عناصر شريكة
            # ═══════════════════════════════════════════════════════
            
            for i, base_rect in enumerate(current_remaining):
                if base_rect.qty <= 0:
                    continue
                
                # تجربة كميات مختلفة من العنصر الأساسي
                max_base_qty = min(
                    base_rect.qty,
                    max_width // base_rect.width
                )
                
                for base_qty in range(max_base_qty, 0, -1):
                    # الحصول على العناصر المتاحة للشراكة
                    other_items = [
                        r for j, r in enumerate(current_remaining)
                        if j != i and r.qty > 0
                    ]
                    
                    # البحث عن شركاء
                    partners = find_partner_items(
                        base_rect,
                        base_qty,
                        other_items,
                        min_width,
                        max_width,
                        tolerance_length
                    )
                    
                    if partners is not None:
                        # تشكيل المجموعة
                        group_items = [
                            UsedItem(
                                rect_id=base_rect.id,
                                width=base_rect.width,
                                length=base_rect.length,
                                used_qty=base_qty,
                                original_qty=base_rect.qty
                            )
                        ]
                        
                        # إضافة الشركاء
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
                            # تحديث الكمية المتبقية
                            partner_rect.qty -= partner_qty
                        
                        new_group = Group(id=next_group_id, items=group_items)
                        all_groups.append(new_group)
                        next_group_id += 1
                        
                        # تحديث الكمية الأساسية
                        base_rect.qty -= base_qty
                        created_group = True
                        break
                
                if created_group:
                    break
            
            # إذا لم نتمكن من إنشاء أي مجموعة، توقف
            if not created_group:
                break
    
    # المتبقي النهائي
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
