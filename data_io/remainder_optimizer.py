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
    start_group_id: int = 1,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """
    خوارزمية محسّنة لتشكيل مجموعات من العناصر المتبقية
    
    تقبل قائمة من نطاقات العرض وتعالج كل نطاق بشكل منفصل
    مع السماح بتكرار نفس العنصر في المجموعة الواحدة
    
    المعاملات الجديدة:
    -----------------
    min_group_quantity : Optional[int]
        الحد الأدنى لكمية المجموعة (حاصل ضرب الطول × العرض × العدد)
    max_group_quantity : Optional[int]
        الحد الأقصى لكمية المجموعة (حاصل ضرب الطول × العرض × العدد)
    
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle], Dict[str, int]]
        (المجموعات الجديدة، البواقي النهائي، إحصائيات الكميات)
    """
    
    # نسخ العناصر المتبقية مع الاحتفاظ بالكميات الأصلية
    current_remaining = [
        Rectangle(r.id, r.width, r.length, r.qty) 
        for r in remaining if r.qty > 0
    ]
    
    # حساب الكميات الإجمالية قبل العملية
    total_quantity_before = sum(rect.width * rect.length * rect.qty for rect in current_remaining)
    
    all_groups: List[Group] = []
    next_group_id = start_group_id
    
    def check_length_tolerance(ref_length: int, candidate_length: int) -> bool:
        """التحقق من الطول المتقارب"""
        return abs(ref_length - candidate_length) <= tolerance_length
    
    def validate_group(group_items: List[Tuple[Rectangle, int]], min_width: int, max_width: int) -> bool:
        """التحقق من صحة المجموعة قبل إنشائها"""
        if not group_items:
            return False
        
        # حساب العرض الإجمالي (مجموع العرض لكل نوع مرة واحدة)
        # تجميع العناصر حسب النوع
        unique_items = {}
        for rect, qty in group_items:
            key = (rect.id, rect.width, rect.length)
            if key not in unique_items:
                unique_items[key] = rect
            # لا نحتاج للكمية هنا لأن العرض يحسب مرة واحدة لكل نوع
        
        total_width = sum(rect.width for rect in unique_items.values())
        
        # التحقق من نطاق العرض - هذا هو الشرط الأساسي
        if not (min_width <= total_width <= max_width):
            return False
        
        # التحقق من وجود عنصرين على الأقل (إلا إذا كان العنصر الواحد يحقق النطاق)
        if len(unique_items) == 1:
            rect = list(unique_items.values())[0]
            # للعنصر الواحد، يجب أن يحقق النطاق بالضبط
            return min_width <= rect.width <= max_width
        
        # للمجموعات المتعددة، يجب أن يكون العرض في النطاق
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
        max_width: int
    ) -> Optional[Tuple[int, int]]:
        """محاولة تكوين مجموعة من عنصر واحد مكرر مع مراعاة حدود الكمية"""
        # في المنطق الجديد، العرض يحسب مرة واحدة لكل نوع
        # لذلك نحتاج لتكرار نفس العنصر حتى يحقق النطاق
        
        # التحقق من أن العنصر يمكن أن يحقق النطاق
        if rect.width < min_width:
            # نحتاج لتكرار العنصر
            min_repeats = (min_width + rect.width - 1) // rect.width  # تقريب لأعلى
            max_repeats = min(rect.qty, max_width // rect.width)
            
            if min_repeats > max_repeats:
                return None
                
            # اختر أكبر عدد ممكن من التكرارات
            qty = max_repeats
            total_w = rect.width  # العرض يحسب مرة واحدة فقط
            
            group_quantity = calculate_group_quantity([(rect, qty)])
            
            # التحقق من حدود الكمية إذا كانت محددة
            if min_group_quantity and group_quantity < min_group_quantity:
                return None
            if max_group_quantity and group_quantity > max_group_quantity:
                return None
            return (qty, total_w)
        
        elif min_width <= rect.width <= max_width:
            # العنصر يحقق النطاق بمفرده
            qty = 1
            total_w = rect.width
            
            group_quantity = calculate_group_quantity([(rect, qty)])
            
            # التحقق من حدود الكمية إذا كانت محددة
            if min_group_quantity and group_quantity < min_group_quantity:
                return None
            if max_group_quantity and group_quantity > max_group_quantity:
                return None
                
            return (qty, total_w)
        
        return None
    
    def find_optimal_combination(
        base_rect: Rectangle,
        remaining_items: List[Rectangle],
        min_width: int,
        max_width: int,
        tolerance: int
    ) -> Optional[List[Tuple[Rectangle, int]]]:
        """البحث عن أفضل تركيبة من العناصر لإكمال المجموعة مع السماح بالتكرار"""
        
        # ترتيب العناصر حسب العرض (الأكبر أولاً)
        sorted_items = sorted(
            remaining_items, 
            key=lambda r: r.width, 
            reverse=True
        )
        
        best_combination = None
        best_efficiency = 0
        
        # محاولة كل عنصر كعنصر أساسي
        for base_qty in range(1, min(base_rect.qty, max_width // base_rect.width) + 1):
            base_total_width = base_rect.width * base_qty
            ref_length = base_rect.length * base_qty
            
            if base_total_width > max_width:
                continue
            
            # محاولة إضافة عناصر أخرى
            combination = [(base_rect, base_qty)]
            current_width = base_total_width
            
            for candidate in sorted_items:
                if candidate.qty <= 0:
                    continue
                
                # حساب أقصى كمية يمكن استخدامها من هذا العنصر
                max_candidate_qty = min(
                    candidate.qty,
                    (max_width - current_width) // candidate.width
                )
                
                if max_candidate_qty <= 0:
                    continue
                
                # محاولة كميات مختلفة من العنصر المرشح
                for candidate_qty in range(max_candidate_qty, 0, -1):
                    candidate_total_length = candidate.length * candidate_qty
                    
                    if check_length_tolerance(ref_length, candidate_total_length):
                        new_width = current_width + candidate.width * candidate_qty
                        
                        if min_width <= new_width <= max_width:
                            # إضافة العنصر إلى التركيبة
                            combination.append((candidate, candidate_qty))
                            current_width = new_width
                            
                            # حساب كفاءة هذه التركيبة
                            group_quantity = calculate_group_quantity(combination)
                            efficiency = group_quantity / (current_width * ref_length)
                            
                            if efficiency > best_efficiency:
                                best_efficiency = efficiency
                                best_combination = combination.copy()
                            break
            
            # التحقق من حدود الكمية للتركيبة الحالية
            if best_combination:
                group_quantity = calculate_group_quantity(best_combination)
                if min_group_quantity and group_quantity < min_group_quantity:
                    continue
                if max_group_quantity and group_quantity > max_group_quantity:
                    continue
        
        return best_combination
    
    # معالجة كل نطاق عرض
    for min_width, max_width in width_ranges:
        max_rounds = 200  # زيادة عدد المحاولات لاستغلال أفضل للكميات
        round_count = 0
        
        while round_count < max_rounds and current_remaining:
            round_count += 1
            
            # تصفية العناصر التي لا تزال لديها كميات
            current_remaining = [r for r in current_remaining if r.qty > 0]
            if not current_remaining:
                break
            
            # ترتيب العناصر حسب العرض (الأكبر أولاً) ثم حسب الكمية
            current_remaining.sort(key=lambda r: (r.width, r.qty), reverse=True)
            
            created_group = False
            
            # محاولة تكوين مجموعة من كل عنصر متاح
            for base_rect in current_remaining:
                if base_rect.qty <= 0:
                    continue
                
                # محاولة تكوين مجموعة من عنصر واحد مكرر
                result = try_single_repeated_item(
                    base_rect, min_width, max_width
                )
                
                if result:
                    qty_used, total_w = result
                    
                    # إنشاء المجموعة مع تكرار نفس العنصر
                    actual_used = min(qty_used, base_rect.qty)
                    base_rect.qty -= actual_used
                    
                    # إنشاء عناصر منفصلة لكل تكرار
                    group_items = []
                    for _ in range(actual_used):
                        group_items.append(
                            UsedItem(
                                rect_id=base_rect.id,
                                width=base_rect.width,
                                length=base_rect.length,
                                used_qty=1,  # كل عنصر بكمية 1
                                original_qty=base_rect.qty + actual_used
                            )
                        )
                    
                    # التحقق من صحة المجموعة قبل إنشائها
                    group_rects = [(base_rect, actual_used)]
                    if validate_group(group_rects, min_width, max_width):
                        new_group = Group(id=next_group_id, items=group_items)
                        all_groups.append(new_group)
                        next_group_id += 1
                        created_group = True
                        break
                    else:
                        # إرجاع الكمية إذا لم تكن المجموعة صالحة
                        base_rect.qty += actual_used
                
                # إذا فشلت المحاولة الأولى، جرب تركيبة معقدة
                else:
                    # البحث عن أفضل تركيبة
                    combination = find_optimal_combination(
                        base_rect,
                        current_remaining,
                        min_width,
                        max_width,
                        tolerance_length
                    )
                    
                    if combination:
                        # إنشاء المجموعة من التركيبة
                        group_items = []
                        
                        for rect, qty in combination:
                            actual_used = min(rect.qty, qty)
                            if actual_used > 0:
                                rect.qty -= actual_used
                                group_items.append(
                                    UsedItem(
                                        rect_id=rect.id,
                                        width=rect.width,
                                        length=rect.length,
                                        used_qty=actual_used,
                                        original_qty=rect.qty + actual_used
                                    )
                                )
                        
                        if group_items:
                            # التحقق من صحة المجموعة قبل إنشائها
                            group_rects = []
                            for item in group_items:
                                for rect in current_remaining:
                                    if rect.id == item.rect_id:
                                        group_rects.append((rect, item.used_qty))
                                        break
                            
                            if validate_group(group_rects, min_width, max_width):
                                new_group = Group(id=next_group_id, items=group_items)
                                all_groups.append(new_group)
                                next_group_id += 1
                                created_group = True
                                break
                            else:
                                # إرجاع الكميات إذا لم تكن المجموعة صالحة
                                for item in group_items:
                                    for rect in current_remaining:
                                        if rect.id == item.rect_id:
                                            rect.qty += item.used_qty
            
            if not created_group:
                break
    
    # حساب الكميات الإجمالية بعد العملية
    final_remaining = [r for r in current_remaining if r.qty > 0]
    total_quantity_after = sum(rect.width * rect.length * rect.qty for rect in final_remaining)
    total_quantity_used = total_quantity_before - total_quantity_after
    
    # إحصائيات الكميات
    quantity_stats = {
        'total_quantity_before': total_quantity_before,
        'total_quantity_after': total_quantity_after,
        'total_quantity_used': total_quantity_used,
        'utilization_percentage': (total_quantity_used / total_quantity_before * 100) if total_quantity_before > 0 else 0,
        'groups_created': len(all_groups),
        'remaining_items_count': len(final_remaining)
    }
    
    return all_groups, final_remaining, quantity_stats


# ═══════════════════════════════════════════════════════════════════════════════
# الدالة المساعدة: استدعاء بنطاق عرض واحد (للاستخدام البسيط)
# ═══════════════════════════════════════════════════════════════════════════════

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
    min_group_quantity : Optional[int]
        الحد الأدنى لكمية المجموعة
    max_group_quantity : Optional[int]
        الحد الأقصى لكمية المجموعة
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle], Dict[str, int]]
        (المجموعات الجديدة، البواقي النهائي، إحصائيات الكميات)
    
    مثال:
    -----
    >>> groups, remaining, stats = exhaustively_regroup(
    ...     remaining_items,
    ...     min_width=370,
    ...     max_width=400,
    ...     tolerance_length=100,
    ...     start_group_id=1001,
    ...     min_group_quantity=650,
    ...     max_group_quantity=700
    ... )
    """
    # تحويل النطاق الواحد إلى قائمة نطاقات
    width_ranges = [(min_width, max_width)]
    
    # استدعاء الدالة الأساسية
    return create_enhanced_remainder_groups(
        remaining,
        width_ranges,
        tolerance_length,
        start_group_id,
        min_group_quantity,
        max_group_quantity
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
    verbose: bool = True,
    min_group_quantity: Optional[int] = None,
    max_group_quantity: Optional[int] = None
) -> Tuple[List[Group], List[Rectangle], Dict[str, int]]:
    """
    نظام متكامل: تشكيل البواقي ثم دمج المجموعات المتطابقة
    
    هذه هي الدالة الرئيسية التي تستخدمها في الكود الرئيسي
    
    المعاملات الجديدة:
    -----------------
    min_group_quantity : Optional[int]
        الحد الأدنى لكمية المجموعة (حاصل ضرب الطول × العرض × العدد)
    max_group_quantity : Optional[int]
        الحد الأقصى لكمية المجموعة (حاصل ضرب الطول × العرض × العدد)
    
    مثال الاستخدام:
    ───────────────
    rem_groups, rem_final_remaining, stats = process_remainder_complete(
        remaining,
        min_width=370,
        max_width=400,
        tolerance_length=100,
        start_group_id=max([g.id for g in groups] + [0]) + 1,
        merge_after=True,
        verbose=True,
        min_group_quantity=650,
        max_group_quantity=700
    )
    """
    
    # المرحلة 1: التشكيل
    groups, final_remaining, quantity_stats = exhaustively_regroup(
        remaining,
        min_width,
        max_width,
        tolerance_length,
        start_group_id,
        min_group_quantity=min_group_quantity,
        max_group_quantity=max_group_quantity
    )

    # المرحلة 2: الدمج
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
    min_group_quantity : Optional[int]
        الحد الأدنى لكمية المجموعة
    max_group_quantity : Optional[int]
        الحد الأقصى لكمية المجموعة
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle], Dict[str, int]]
        - قائمة المجموعات الجديدة
        - قائمة العناصر المتبقية بعد التجميع
        - إحصائيات الكميات
        
    أمثلة:
    -------
    >>> enhanced_groups, final_remaining, stats = create_enhanced_remainder_groups_from_rectangles(
    >>>     remaining_items, 370, 400, 100, min_group_quantity=650, max_group_quantity=700
    >>> )
    """
    return create_enhanced_remainder_groups(
        remaining_rectangles, 
        [(min_width, max_width)], 
        tolerance_length, 
        start_group_id,
        min_group_quantity,
        max_group_quantity
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


# ═══════════════════════════════════════════════════════════════════════════════
# دالة توليد اقتراحات المقاسات المطلوبة للبواقي
# ═══════════════════════════════════════════════════════════════════════════════

def generate_size_suggestions(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[Dict[str, any]]:
    """
    توليد اقتراحات للمقاسات المطلوبة لتشكيل مجموعات من البواقي
    
    هذه الدالة تحلل البواقي وتقترح المقاسات المطلوبة لتشكيل مجموعات جديدة
    وفقاً للشروط المحددة (النطاق وفرق الأطوال)
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة البواقي
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
        
    الإرجاع:
    -------
    List[Dict[str, any]]
        قائمة اقتراحات المقاسات مع التفاصيل
    """
    suggestions = []
    
    for rect in remaining:
        if rect.qty <= 0:
            continue
            
        # حساب العرض المطلوب لإكمال المجموعة
        remaining_width_min = min_width - rect.width
        remaining_width_max = max_width - rect.width
        
        if remaining_width_min <= 0:
            # العنصر يمكن أن يكون وحده في المجموعة
            suggestions.append({
                'type': 'single_item',
                'current_item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'total_length': rect.length * rect.qty,
                'suggestion': f"يمكن استخدام هذا المقاس وحده ({rect.qty} قطعة)",
                'group_width': rect.width,
                'efficiency': 'عالية'
            })
        else:
            # العنصر يحتاج شريك لإكمال المجموعة
            required_width_min = remaining_width_min
            required_width_max = remaining_width_max
            
            suggestions.append({
                'type': 'needs_partner',
                'current_item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'total_length': rect.length * rect.qty,
                'required_width_range': f"{required_width_min} - {required_width_max}",
                'suggestion': f"يحتاج مقاس بعرض {required_width_min}-{required_width_max}",
                'group_width': f"{rect.width} + {required_width_min}-{required_width_max}",
                'efficiency': 'متوسطة'
            })
    
    return suggestions


def analyze_remaining_for_optimization(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> Dict[str, any]:
    """
    تحليل شامل للبواقي لتحديد إمكانيات التحسين
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة البواقي
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
        
    الإرجاع:
    -------
    Dict[str, any]
        تحليل شامل للبواقي
    """
    if not remaining:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'potential_groups': 0,
            'optimization_recommendations': []
        }
    
    # إحصائيات أساسية
    total_items = len(remaining)
    total_quantity = sum(rect.qty for rect in remaining)
    total_area = sum(rect.width * rect.length * rect.qty for rect in remaining)
    
    # تحليل إمكانيات التجميع
    potential_groups = 0
    recommendations = []
    
    for rect in remaining:
        if rect.qty <= 0:
            continue
            
        # حساب إمكانية التجميع مع العناصر الأخرى
        can_form_group = False
        
        for other_rect in remaining:
            if other_rect.id == rect.id or other_rect.qty <= 0:
                continue
                
            combined_width = rect.width + other_rect.width
            if min_width <= combined_width <= max_width:
                # التحقق من تقارب الأطوال
                length_diff = abs(rect.length * rect.qty - other_rect.length * other_rect.qty)
                if length_diff <= tolerance_length:
                    can_form_group = True
                    potential_groups += 1
                    break
        
        if not can_form_group:
            recommendations.append({
                'item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'issue': 'صعوبة في التجميع',
                'suggestion': f'يحتاج مقاس بعرض {min_width - rect.width}-{max_width - rect.width}'
            })
    
    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_area': total_area,
        'potential_groups': potential_groups,
        'optimization_recommendations': recommendations,
        'utilization_potential': (potential_groups / total_items * 100) if total_items > 0 else 0
    }