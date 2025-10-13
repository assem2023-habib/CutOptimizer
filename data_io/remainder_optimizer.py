"""
وحدة تحسين تجميع البواقي
========================

هذه الوحدة تحتوي على الخوارزميات المتقدمة لتجميع البواقي
وإنشاء مجموعات إضافية من العناصر المتبقية.

الاستراتيجية الجديدة (محدّثة):
---------------------------------
1. الترتيب: يتم ترتيب العناصر حسب العرض (width) من الأكبر للأصغر
2. البحث عن شركاء: الأولوية للبحث عن عناصر مختلفة لتكوين مجموعات متنوعة
3. التكرار عند الضرورة: إذا لم تتحقق شروط العرض، يتم تكرار عنصر أو أكثر
4. الحفاظ على السماحية: يتم التحقق من شرط السماحية في جميع الحالات

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
        
        # حساب العرض الإجمالي (مجموع عرض كل نوع مرة واحدة - بدون ضرب في الكمية)
        total_width = sum(rect.width for rect, qty in group_items)
        
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
        max_width: int
    ) -> Optional[Tuple[int, int]]:
        """
        محاولة تكوين مجموعة من عنصر واحد مكرر مع مراعاة حدود الكمية
        ملاحظة: العرض الكلي = width (مرة واحدة) بغض النظر عن الكمية
        """
        
        # العرض الكلي هو عرض العنصر فقط (حسب models.py)
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
        tolerance: int
    ) -> Optional[List[Tuple[Rectangle, int]]]:
        """
        البحث عن شركاء لتشكيل مجموعة - أولوية للتنويع قبل التكرار
        
        الاستراتيجية:
        -------------
        1. محاولة تشكيل مجموعة بدون تكرار (كل عنصر مرة واحدة)
        2. البحث عن شركاء من عناصر مختلفة مع زيادة الكميات
        3. إذا لم يتحقق النطاق، اللجوء للتكرار
        """
        
        # ترتيب العناصر حسب العرض من الأكبر للأصغر
        sorted_items = sorted(
            [r for r in remaining_items if r.qty > 0],
            key=lambda r: r.width,
            reverse=True
        )
        
        best_combination = None
        best_score = 0
        
        # جرب كميات مختلفة من العنصر الأساسي (محاولة استخدام أكبر كمية ممكنة)
        max_base_qty = base_rect.qty  # أقصى كمية متاحة
        
        for base_qty in range(max_base_qty, 0, -1):
            base_total_width = base_rect.width  # العرض هو عرض العنصر فقط (بدون ضرب في الكمية)
            ref_length = base_rect.length * base_qty
            
            # إذا كان العنصر الأساسي يحقق النطاق بمفرده
            if min_width <= base_total_width <= max_width:
                combination = [(base_rect, base_qty)]
                group_quantity = calculate_group_quantity(combination)
                
                # التحقق من حدود الكمية
                if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                   (not max_group_quantity or group_quantity <= max_group_quantity):
                    score = group_quantity
                    if score > best_score:
                        best_score = score
                        best_combination = combination.copy()
            
            # الخطوة 2: البحث عن شركاء (السماح بتكرار نفس العنصر)
            combination = [(base_rect, base_qty)]
            current_width = base_total_width
            used_qty = {base_rect.id: base_qty}  # تتبع الكمية المستخدمة لكل عنصر
            
            for candidate in sorted_items:
                if candidate.qty <= 0:
                    continue
                
                # التحقق من إمكانية إضافة هذا العنصر
                if current_width + candidate.width > max_width:
                    continue
                
                # حساب الكمية المتبقية المتاحة من هذا العنصر
                already_used = used_qty.get(candidate.id, 0)
                available_qty = candidate.qty - already_used
                
                if available_qty <= 0:
                    continue
                
                # أقصى كمية متاحة من العنصر
                max_candidate_qty = available_qty
                
                # جرب كميات مختلفة من الأكبر للأصغر
                for candidate_qty in range(max_candidate_qty, 0, -1):
                    new_width = current_width + candidate.width  # العرض = مجموع عرض كل نوع
                    candidate_total_length = candidate.length * candidate_qty
                    
                    # التحقق من نطاق العرض
                    if new_width > max_width:
                        continue
                    
                    # التحقق من السماحية في الطول
                    if check_length_tolerance(ref_length, candidate_total_length):
                        test_combination = combination + [(candidate, candidate_qty)]
                        test_width = sum(r.width for r, q in test_combination)  # مجموع عرض كل نوع
                        
                        # إذا وصلنا للنطاق المطلوب
                        if min_width <= test_width <= max_width:
                            group_quantity = calculate_group_quantity(test_combination)
                            
                            # التحقق من حدود الكمية
                            if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                               (not max_group_quantity or group_quantity <= max_group_quantity):
                                diversity_score = len(test_combination)
                                score = group_quantity * diversity_score
                                
                                if score > best_score:
                                    best_score = score
                                    best_combination = test_combination.copy()
                            
                            # تحديث الكمية المستخدمة
                            used_qty[candidate.id] = already_used + candidate_qty
                            combination = test_combination
                            current_width = test_width
                        break
        
        # إذا وجدنا تركيبة جيدة، أرجعها
        if best_combination:
            return best_combination
        
        # الخطوة 3: إذا لم نحقق النطاق، جرب التكرار
        return find_combination_with_repetition(
            base_rect, remaining_items, min_width, max_width, tolerance
        )
    
    def find_combination_with_repetition(
        base_rect: Rectangle,
        remaining_items: List[Rectangle],
        min_width: int,
        max_width: int,
        tolerance: int
    ) -> Optional[List[Tuple[Rectangle, int]]]:
        """البحث عن تركيبة مع السماح بالتكرار عند الضرورة"""
        
        sorted_items = sorted(
            [r for r in remaining_items if r.qty > 0],
            key=lambda r: r.width,
            reverse=True
        )
        
        best_combination = None
        best_score = 0
        
        # جرب كميات مختلفة من العنصر الأساسي (من الأكبر للأصغر لزيادة الاستفادة)
        max_base_qty = base_rect.qty
        for base_qty in range(max_base_qty, 0, -1):
            base_total_width = base_rect.width  # العرض هو عرض العنصر فقط
            ref_length = base_rect.length * base_qty
            
            # إذا حقق النطاق بالتكرار
            if min_width <= base_total_width <= max_width:
                combination = [(base_rect, base_qty)]
                group_quantity = calculate_group_quantity(combination)
                
                if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                   (not max_group_quantity or group_quantity <= max_group_quantity):
                    score = group_quantity
                    if score > best_score:
                        best_score = score
                        best_combination = combination.copy()
            
            # حاول إضافة عناصر أخرى (السماح بتكرار نفس العنصر)
            combination = [(base_rect, base_qty)]
            current_width = base_total_width
            used_qty = {base_rect.id: base_qty}  # تتبع الكمية المستخدمة لكل عنصر
            
            for candidate in sorted_items:
                if candidate.qty <= 0:
                    continue
                
                # التحقق من إمكانية إضافة هذا العنصر
                if current_width + candidate.width > max_width:
                    continue
                
                # حساب الكمية المتبقية المتاحة من هذا العنصر
                already_used = used_qty.get(candidate.id, 0)
                available_qty = candidate.qty - already_used
                
                if available_qty <= 0:
                    continue
                
                # أقصى كمية متاحة من العنصر
                max_candidate_qty = available_qty
                
                # جرب كميات مختلفة من الأكبر للأصغر
                for candidate_qty in range(max_candidate_qty, 0, -1):
                    candidate_total_length = candidate.length * candidate_qty
                    
                    if check_length_tolerance(ref_length, candidate_total_length):
                        new_width = current_width + candidate.width  # العرض = مجموع عرض كل نوع
                        
                        if min_width <= new_width <= max_width:
                            test_combination = combination + [(candidate, candidate_qty)]
                            group_quantity = calculate_group_quantity(test_combination)
                            
                            if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                               (not max_group_quantity or group_quantity <= max_group_quantity):
                                score = group_quantity
                                if score > best_score:
                                    best_score = score
                                    best_combination = test_combination.copy()
                            
                            # تحديث الكمية المستخدمة
                            used_qty[candidate.id] = already_used + candidate_qty
                            combination = test_combination
                            current_width = new_width
                        break
        
        return best_combination
    
    # معالجة كل نطاق عرض
    for min_width, max_width in width_ranges:
        max_rounds = 100  # زيادة عدد المحاولات
        round_count = 0
        
        while round_count < max_rounds and current_remaining:
            round_count += 1
            
            # تصفية العناصر التي لا تزال لديها كميات
            current_remaining = [r for r in current_remaining if r.qty > 0]
            if not current_remaining:
                break
            
            # ترتيب العناصر حسب العرض (الأكبر أولاً)
            current_remaining.sort(
                key=lambda r: r.width, 
                reverse=True
            )
            
            created_group = False
            
            # محاولة تكوين مجموعة من كل عنصر متاح (البدء من الأكبر)
            for base_rect in current_remaining:
                if base_rect.qty <= 0:
                    continue
                
                # الخطوة 1: البحث عن شركاء أولاً (التنويع قبل التكرار)
                combination = find_partners_combination(
                    base_rect,
                    current_remaining,
                    min_width,
                    max_width,
                    tolerance_length
                )
                
                if combination:
                    # إنشاء المجموعة من التركيبة
                    group_items = []
                    temp_quantities = {}  # لحفظ الكميات الأصلية
                    total_qty_per_rect = {}  # مجموع الكميات المطلوبة لكل عنصر
                    
                    # حساب مجموع الكميات المطلوبة لكل عنصر
                    for rect, qty in combination:
                        if rect.id not in temp_quantities:
                            temp_quantities[rect.id] = rect.qty
                            total_qty_per_rect[rect.id] = 0
                        total_qty_per_rect[rect.id] += qty
                    
                    # التحقق من أن الكميات المطلوبة لا تتجاوز الكميات المتاحة
                    valid_combination = True
                    for rect_id, total_needed in total_qty_per_rect.items():
                        if total_needed > temp_quantities[rect_id]:
                            valid_combination = False
                            break
                    
                    if not valid_combination:
                        continue
                    
                    # خصم الكميات وإنشاء العناصر
                    processed_rects = {}  # لتتبع ما تم معالجته
                    for rect, qty in combination:
                        # البحث عن العنصر في القائمة الحالية
                        for current_rect in current_remaining:
                            if current_rect.id == rect.id:
                                if rect.id not in processed_rects:
                                    # أول مرة نرى هذا العنصر - استخدم المجموع الكلي
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
                        # إنشاء المجموعة للتحقق من صحتها
                        new_group = Group(id=next_group_id, items=group_items)
                        
                        # استخدام دالة total_width() من models
                        total_width = new_group.total_width()
                        
                        if min_width <= total_width <= max_width:
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
                                        break
            
            # الخطوة 2: إذا لم نستطع تشكيل مجموعات بعناصر مختلفة، جرب التكرار
            if not created_group:
                for base_rect in current_remaining:
                    if base_rect.qty <= 0:
                        continue
                    
                    # محاولة تشكيل مجموعة من عنصر واحد مكرر
                    if min_width <= base_rect.width <= max_width:
                        # العنصر يحقق النطاق - استخدم أكبر كمية ممكنة
                        qty_to_use = base_rect.qty
                        
                        # التحقق من حدود الكمية
                        group_quantity = calculate_group_quantity([(base_rect, qty_to_use)])
                        if (not min_group_quantity or group_quantity >= min_group_quantity) and \
                           (not max_group_quantity or group_quantity <= max_group_quantity):
                            
                            # إنشاء المجموعة
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
                            
                            # التحقق من العرض
                            if min_width <= new_group.total_width() <= max_width:
                                # خصم الكمية
                                base_rect.qty -= qty_to_use
                                
                                all_groups.append(new_group)
                                next_group_id += 1
                                created_group = True
                                break
            
            if not created_group:
                break
        
        # المرحلة النهائية لهذا النطاق: تشكيل مجموعات من عنصر واحد فقط (مكرر) لتحقيق أقصى استفادة
        # الشرط: العرض الكلي = مجموع عرض الإدخالات (بدون ضرب في الكمية)
        # السماحية: نوزع الكميات بالتساوي بين الإدخالات بحيث يكون الفرق 0 <= tolerance_length/length
        for rect in list(current_remaining):
            if rect.qty <= 0:
                continue
            w = rect.width
            L = rect.length if rect.length > 0 else 1
            # حدود عدد الإدخالات الممكنة حسب العرض
            k_min = (min_width + w - 1) // w
            k_max = max_width // w
            if k_min <= 0:
                k_min = 1
            if k_max <= 0 or k_min > k_max:
                continue
            
            # طالما يمكننا تشكيل مجموعة صالحة، استمر
            while rect.qty > 0:
                Q = rect.qty
                best_k = 0
                best_used = 0
                best_each = 0
                # دلتا الكمية المسموحة بين الإدخالات (نختار توزيعاً متساوياً => الفارق = 0)
                delta_max = tolerance_length // L
                # جرّب جميع قيم k الممكنة واختَر ما يزيد الاستخدام
                for k in range(k_max, k_min - 1, -1):
                    total_w = k * w
                    if total_w < min_width or total_w > max_width:
                        continue
                    # توزيع متساوٍ يحقق الفارق 0 <= delta_max دائماً
                    q_each = Q // k
                    if q_each <= 0:
                        continue
                    used = k * q_each
                    if used > best_used:
                        best_used = used
                        best_k = k
                        best_each = q_each
                
                if best_used <= 0 or best_k <= 0 or best_each <= 0:
                    break  # لا يمكن تشكيل مزيد من المجموعات
                
                # بناء المجموعة باستخدام best_k إدخالاً من نفس العنصر وبنفس الكمية لكل إدخال
                group_items = []
                for _ in range(best_k):
                    group_items.append(
                        UsedItem(
                            rect_id=rect.id,
                            width=w,
                            length=L if L != 1 else rect.length,
                            used_qty=best_each,
                            original_qty=Q
                        )
                    )
                new_group = Group(id=next_group_id, items=group_items)
                # تحقق العرض عبر models.Group.total_width()
                if min_width <= new_group.total_width() <= max_width:
                    # تحقق السماحية: الفارق بين أي إدخالين = |best_each - best_each| * L = 0 <= tolerance_length
                    # خصم الكمية وإضافة المجموعة
                    rect.qty -= best_used
                    all_groups.append(new_group)
                    next_group_id += 1
                else:
                    # لا يمكن إنشاء مجموعة بعرض صالح
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