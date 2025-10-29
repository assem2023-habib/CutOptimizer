from typing import List
from collections import Counter
from models.data_models import Carpet, CarpetUsed, GroupCarpet
from core.group_helpers import (
    generate_valid_partner_combinations,
    equal_products_solution
)

def build_groups(
        carpets: List[Carpet],
        min_width: int,
        max_width: int,
        max_partner: int = 5,
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
            continue
        partner_level = 1
        for partner_level in range(1, max_partner + 1):
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
                if not main.is_available():
                    break

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
                    continue

                x_vals, k_max = equal_products_solution(a, XMax)
                if not x_vals or k_max <= 0:
                    continue

                used_items : List[CarpetUsed] = []
                for e,x in zip(unique_elements, x_vals):
                    if x <= 0:
                        continue

                    repetition_count = elements_counts[e.id]
                    
                    qty_per_repetition = min(x, e.rem_qty // repetition_count)
                    if qty_per_repetition <= 0:
                        continue
                    total_qty_used = qty_per_repetition * repetition_count

                    if total_qty_used > e.rem_qty:
                        continue

                    e.consume(total_qty_used)
                    for _ in range(repetition_count):
                        used_items.append(
                            CarpetUsed(
                                carpet_id=e.id,
                                width=e.width,
                                height=e.height,
                                qty_used=qty_per_repetition,
                                qty_rem=e.rem_qty
                            )
                        )
                        
                if len(used_items) < 2:
                    continue
                new_group = GroupCarpet(group_id=group_id, items=used_items)
                if new_group.is_valid(min_width, max_width):
                    group.append(new_group)
                    group_id += 1
                partner_level = 1
    return group