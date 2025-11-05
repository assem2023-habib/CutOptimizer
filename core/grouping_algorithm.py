from typing import List, Optional
from collections import Counter
from models.data_models import Carpet, CarpetUsed, GroupCarpet
from core.group_helpers import (
    generate_valid_partner_combinations,
    equal_products_solution,
    equal_products_solution_with_tolerance
)

def build_groups(
        carpets: List[Carpet],
        min_width: int,
        max_width: int,
        max_partner: int = 7,
        tolerance: int = 0,
) -> List[GroupCarpet]:
    carpets.sort(key=lambda c: (c.width, c.height, c.qty), reverse=True)
    group: List[GroupCarpet] = []
    group_id = 1
    for main in carpets:
        if not main.is_available():
            continue
        remaining_width = max_width - main.width

        start_index = None
        for j, c in enumerate(carpets):
            if c.width <= remaining_width:
                start_index = j
                break
        if start_index is None:
            single_group = try_create_single_group(
                main, min_width, max_width, group_id
            )
            if single_group:
                group.append(single_group)
                group_id += 1
            continue
        current_max_partner = max_partner
        if min_width >= 370 and min_width <= 400 and main.width <= 70:
            current_max_partner = 10
        if min_width >= 470 and main.width <= 60:
            current_max_partner = 12

        partner_level = 1
        
        for partner_level in range(1, current_max_partner + 1):
            if not main.is_available():
                break
           
            partner_sets = []
            partner_sets += generate_valid_partner_combinations(
                main, carpets, partner_level, min_width, max_width, allow_repetation=False, start_index=start_index
            )
            partner_sets += generate_valid_partner_combinations(
                main, carpets, partner_level, min_width, max_width, allow_repetation=True, start_index=start_index
            )

            if not partner_sets:
                continue
            for partners in partner_sets:
                same_id = False
                if not main.is_available():
                    break
                if (len(partners) == 1):
                    for carpet in partners:
                        if carpet.id == main.id or carpet.width == main.width:
                            same_id = True
                if same_id:
                    continue        
                result = process_partner_group(
                    main, partners, tolerance, group_id, min_width=min_width, max_width=max_width
                )
                if result:
                    new_group, group_id = result
                    group.append(new_group)

        if main.is_available():
            if(main.width * 2 >= min_width and main.width * 2 <= max_width and main.rem_qty >= 2):
                used_items = []
                qty_used = main.rem_qty // 2
                total_qty_used = qty_used * 2
                for _ in range(2):
                    main.consume(qty_used)
                    used_items.append(
                        CarpetUsed(
                            carpet_id=main.id,
                            width=main.width,
                            height=main.height,
                            qty_used=qty_used,
                            qty_rem= main.rem_qty,
                        )
                    )
                group.append(GroupCarpet(group_id=group_id, items=used_items))
                group_id += 1

        single_group = try_create_single_group(
                main, min_width, max_width, group_id
            )

        if single_group:
            group.append(single_group)
            group_id += 1
    return group


def process_partner_group(
    main: Carpet,
    partners: List[Carpet],
    tolerance: int,
    current_group_id: int,
    min_width: int,
    max_width: int,
) -> Optional[tuple]:
    """
    معالجة مجموعة من الشركاء وإنشاء مجموعة إذا أمكن
    
    Returns:
    --------
    Optional[tuple]
        (GroupCarpet, new_group_id) أو None
    """
    elements = [main] + partners
    elements_counts = Counter(e.id for e in elements)
    
    # بناء المدخلات
    a = []
    XMax = []
    unique_elements = []
    seen = set()
    
    for e in elements:
        if e.id not in seen:
            seen.add(e.id)
            unique_elements.append(e)
            a.append(e.height)
            
            repetition_count = elements_counts[e.id]
            available_per_repetition = e.rem_qty // repetition_count
            XMax.append(available_per_repetition)
    
    if any(x <= 0 for x in XMax):
        return None
    
    if tolerance == 0:
        x_vals, k_max = equal_products_solution(a, XMax)
    else:
        x_vals, k_max = equal_products_solution_with_tolerance(
            a, XMax, tolerance
        )
    
    if not x_vals or k_max <= 0:
        return None
    
    # بناء العناصر المستخدمة
    used_items: List[CarpetUsed] = []
    all_valid = True
    
    for e, x in zip(unique_elements, x_vals):
        if x <= 0:
            all_valid = False
            break
        
        repetition_count = elements_counts[e.id]
        qty_per_repetition = min(x, e.rem_qty // repetition_count)
        
        if qty_per_repetition <= 0:
            all_valid = False
            break
        
        total_qty_used = qty_per_repetition * repetition_count
        
        if total_qty_used > e.rem_qty:
            all_valid = False
            break
        
        for _ in range(repetition_count):
            e.consume(qty_per_repetition)
            used_items.append(
                CarpetUsed(
                    carpet_id=e.id,
                    width=e.width,
                    height=e.height,
                    qty_used=qty_per_repetition,
                    qty_rem=e.rem_qty
                )
            )
    
    if not all_valid or len(used_items) < 2:
        return None
    
    new_group = GroupCarpet(group_id=current_group_id, items=used_items)
    if new_group.is_valid(min_width, max_width):
        return new_group, current_group_id + 1
    return None
    

def try_create_single_group(
    carpet: Carpet,
    min_width: int,
    max_width: int,
    group_id: int
) -> Optional[GroupCarpet]:
    """
    محاولة إنشاء مجموعة فردية من سجاد واحد
    
    Parameters:
    -----------
    carpet : Carpet
        السجاد المراد إضافته كمجموعة فردية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    group_id : int
        معرّف المجموعة
    
    Returns:
    --------
    Optional[GroupCarpet]
        المجموعة المُنشأة أو None إذا فشل الإنشاء
        
    Notes:
    ------
    - تستهلك هذه الدالة كامل الكمية المتبقية من السجاد
    - تُعدّل كائن carpet مباشرة (side effect)
    """
    # التحقق من الشروط
    if not (carpet.width >= min_width and 
            carpet.width <= max_width and 
            carpet.is_available() and 
            carpet.rem_qty > 0):
        return None
    
    # إنشاء عنصر واحد
    single_item = CarpetUsed(
        carpet_id=carpet.id,
        width=carpet.width,
        height=carpet.height,
        qty_used=carpet.rem_qty,
        qty_rem=0
    )
    
    # استهلاك الكمية
    qty_to_consume = carpet.rem_qty
    carpet.consume(qty_to_consume)
    
    # إنشاء المجموعة
    single_group = GroupCarpet(
        group_id=group_id,
        items=[single_item]
    )
    
    # التحقق من الصلاحية
    if single_group.is_valid(min_width, max_width):
        return single_group
    
    return None