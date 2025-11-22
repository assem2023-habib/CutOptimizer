from typing import List, Optional
from collections import Counter
from models.carpet import Carpet
from models.carpet_used import CarpetUsed
from models.group_carpet import GroupCarpet
from core.group_helpers import (
    generate_valid_partner_combinations,
    equal_products_solution,
    equal_products_solution_with_tolerance
)
import json, os
from core.Enums.grouping_mode import GroupingMode
from core.Enums.sort_type import SortType


def build_groups(
        carpets: List[Carpet],
        min_width: int,
        max_width: int,
        max_partner: int = 7,
        tolerance: int = 0,
) -> List[GroupCarpet]:
    selected_mode= load_selected_mode()
    selected_sort_type= load_saved_sort()

    if selected_sort_type== SortType.SORT_BY_WIDTH:
        carpets.sort(key=lambda c: (c.width, c.height, c.qty), reverse=True)
    elif selected_sort_type == SortType.SORT_BY_QUANTITY:
        carpets.sort(key=lambda c: (c.rem_qty, c.height, c.width), reverse=True)
    elif selected_sort_type == SortType.SORT_BY_HEIGHT:
        carpets.sort(key=lambda c: (c.height, c.width, c.qty), reverse=True)

    group: List[GroupCarpet] = []
    group_id = 1
    for main in carpets:
        if not main.is_available():
            continue

        start_index = 0

        if not selected_sort_type == SortType.SORT_BY_QUANTITY:
            remaining_width = max_width - main.width
            
            start_index = next((j for j, c in enumerate(carpets) if c.width <= remaining_width), None)
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
            rem_qty= main.rem_qty
            new_groups, group_id = generate_and_process_partners(
                main=main,
                carpets=carpets,
                partner_level=partner_level,
                min_width=min_width,
                max_width=max_width,
                tolerance=tolerance,
                group_id=group_id,
                selected_mode=selected_mode,
                start_index=start_index
            )
            if selected_sort_type == SortType.SORT_BY_QUANTITY:
                if not new_groups:
                    main.rem_qty= rem_qty
                    continue

            group.extend(new_groups)

        if selected_mode == GroupingMode.NO_MAIN_REPEAT:
            for partner_level in range(1, current_max_partner + 1):
                if not main.is_available():
                    break

                new_groups, group_id = generate_and_process_partners(
                    main=main,
                    carpets=carpets,
                    partner_level=partner_level,
                    min_width=min_width,
                    max_width=max_width,
                    tolerance=tolerance,
                    group_id=group_id,
                    selected_mode=GroupingMode.ALL_COMBINATIONS,
                    start_index=start_index
                )
                group.extend(new_groups)

        single_group = try_create_single_group(
                main, min_width, max_width, group_id
            )

        if single_group:
            group.append(single_group)
            group_id += 1

    for g in group:
        g.sort_items_by_width(reverse= True)

    group.sort(key=lambda g: g.items[0].width if g.items else 0, reverse=True)

    return group

def generate_and_process_partners(
        main: Carpet,
        carpets: List[Carpet],
        partner_level: int,
        min_width: int,
        max_width: int,
        tolerance: int,
        group_id: int,
        selected_mode: GroupingMode,
        start_index: int,
    )->tuple[List[GroupCarpet], int]:

    groups: list[GroupCarpet] = []
    
    if not main.is_available():
        return groups,group_id
    
    partner_sets = []

    if selected_mode == GroupingMode.NO_MAIN_REPEAT:
        partner_sets += generate_valid_partner_combinations(
            main, carpets, partner_level, min_width, max_width,
            allow_repetation=False, start_index=start_index, exclude_main=True
        )
        partner_sets += generate_valid_partner_combinations(
            main, carpets, partner_level, min_width, max_width,
            allow_repetation=True, start_index=start_index, exclude_main=True
        )

    else:
        partner_sets += generate_valid_partner_combinations(
            main, carpets, partner_level, min_width, max_width,
            allow_repetation=False, start_index=start_index
        )
        partner_sets += generate_valid_partner_combinations(
            main, carpets, partner_level, min_width, max_width,
            allow_repetation=True, start_index=start_index
        )

    for partners in partner_sets:
        if not main.is_available():
            break
        result= process_partner_group(
            main, partners, tolerance, group_id,
            min_width= min_width, max_width=max_width
        )
        if result:
            new_group, group_id =result
            groups.append(new_group)

    return groups, group_id

def process_partner_group(
    main: Carpet,
    partners: List[Carpet],
    tolerance: int,
    current_group_id: int,
    min_width: int,
    max_width: int,
) -> Optional[tuple]:

    elements = [main] + partners
    elements_counts = Counter(e.id for e in elements)
    
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
    
    used_items: List[CarpetUsed] = []
    all_valid = True
    rollback_data = []
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
            result= []
            if hasattr(e, "repeated") and e.repeated:
                result= e.consume_from_repeated(qty_per_repetition)
            e.consume(qty_per_repetition)

            rollback_data.append({
                "carpet": e,
                "qty": qty_per_repetition,
                "consumed_repeated": result
            })
            
            used_items.append(
                CarpetUsed(
                    carpet_id=e.id,
                    width=e.width,
                    height=e.height,
                    qty_used=qty_per_repetition,
                    qty_rem=e.rem_qty,
                    client_order= e.client_order,
                    repeated= result
                )
            )
    
    if not all_valid or len(used_items) < 2:
        rollback_consumption(rollback_data)
        return None
    
    new_group = GroupCarpet(group_id=current_group_id, items=used_items)
    if new_group.is_valid(min_width, max_width):
        return new_group, current_group_id + 1
    
    rollback_consumption(rollback_data)
    return None
    

def try_create_single_group(
    carpet: Carpet,
    min_width: int,
    max_width: int,
    group_id: int
) -> Optional[GroupCarpet]:

    if not (carpet.width >= min_width and 
            carpet.width <= max_width and 
            carpet.is_available() and 
            carpet.rem_qty > 0):
        return None
    result= []
    if hasattr(carpet, "repeated") and carpet.repeated:
        result= carpet.consume_from_repeated(carpet.rem_qty)
    single_item = CarpetUsed(
        carpet_id=carpet.id,
        width=carpet.width,
        height=carpet.height,
        qty_used=carpet.rem_qty,
        qty_rem=0,
        client_order= carpet.client_order,
    )

    single_group = GroupCarpet(
        group_id=group_id,
        items=[single_item]
    )

    if not single_group.is_valid(min_width, max_width):
        return None
    
    qty_to_consume = carpet.rem_qty
    carpet.consume(qty_to_consume)
    
    return single_group

def load_selected_mode()->GroupingMode | None:
    config_path= os.path.join(os.getcwd(), "config", "config.json")
    if not os.path.exists(config_path):
        return None
    
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg= json.load(f)
        mode_text = cfg.get("selected_mode", "").strip()
    
    try:
        return GroupingMode(mode_text)
    except ValueError:
        return None
    
 
def load_saved_sort():
    config_path= os.path.join(os.getcwd(), "config", "config.json")
    if not os.path.exists(config_path):
        return None
    
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg= json.load(f)
        mode_text = cfg.get("selected_sort_type", "").strip()

    return SortType(mode_text)

def rollback_consumption(rollback_data: list[dict]) -> None:
    """
    ✅ إرجاع جميع الكميات المستهلكة
    يتم استدعاؤها عندما تفشل المجموعة في التحقق
    """
    for item in rollback_data:
        carpet = item["carpet"]
        qty = item["qty"]
        consumed_repeated = item["consumed_repeated"]
        
        # إرجاع الكمية الرئيسية
        carpet.rem_qty += qty
        
        # إرجاع الكميات من repeated
        if consumed_repeated and hasattr(carpet, "restore_repeated"):
            carpet.restore_repeated(consumed_repeated)