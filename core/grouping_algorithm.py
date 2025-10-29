from typing import List
from models.data_models import Carpet, CarpetUsed, GroupCarpet
from core.group_helpers import (
    generate_valid_partner_combinations,
    equal_products_solution
)

def build_groups(
        carpets: List[Carpet],
        min_width: int,
        max_width: int,
        max_partner: int = 25,
) -> List[GroupCarpet]:
    carpets.sort(key=lambda c: (c.width, c.height, c.qty), reverse=True)
    group: List[GroupCarpet] = []
    group_id = 1
    for main in carpets:
        if not main.is_available():
            continue
        no_partner_found = False
        partner_level = 1
        while partner_level <= max_partner and main.is_available() and not no_partner_found:
            formed_group_in_level = False
            # partner_sets = generate_valid_partner_combinations(
            #     main, carpets, partner_level, min_width, max_width, allow_repetation= False  
            # )
            partner_sets = generate_valid_partner_combinations(
                main, carpets,partner_level,  min_width, max_width, allow_repetation= True
            )

            if not partner_sets:
                no_partner_found = True
                break

            for partners in partner_sets:
                elements = [main] + partners
                a = [e.height for e in elements]
                XMax = [e.rem_qty for e in elements]

                x_vals, k_max = equal_products_solution(a, XMax)
                if not x_vals or k_max <= 0:
                    continue

                used_items : List[CarpetUsed] = []
                for e,x in zip(elements, x_vals):
                    if x <= 0:
                        continue
                    qty_used =min(x, e.rem_qty)
                    e.consume(qty_used)
                    used_items.append(
                        CarpetUsed(
                            carpet_id=e.id,
                            width=e.width,
                            height=e.height,
                            qty_used=qty_used,
                            qty_rem=e.rem_qty
                        )
                    )

                    new_group = GroupCarpet(group_id=group_id, items=used_items)
                    if new_group.is_valid(min_width, max_width):
                        group.append(new_group)
                        group_id += 1
                        formed_group_in_level = True

                if not formed_group_in_level:
                    no_partner_found = True

                partner_level +=1
    return group


def run_demo():
    from models.data_models import Carpet

    carpets_data =carpets_data = [
        {"width": 347, "height": 240, "qty": 128},
        {"width": 315, "height": 400, "qty": 112},
        {"width": 304, "height": 200, "qty": 20},
        {"width": 294, "height": 370, "qty": 84},
        {"width": 263, "height": 200, "qty": 296},
        {"width": 260, "height": 350, "qty": 124},
        {"width": 250, "height": 300, "qty": 144},
        {"width": 242, "height": 160, "qty": 115},
        {"width": 241, "height": 160, "qty": 40},
        {"width": 210, "height": 250, "qty": 160},
        {"width": 210, "height": 285, "qty": 140},
        {"width": 200, "height": 300, "qty": 12},
        {"width": 178, "height": 120, "qty": 40},
        {"width": 168, "height": 235, "qty": 182},
        {"width": 160, "height": 230, "qty": 18},
        {"width": 145, "height": 200, "qty": 130},
        {"width": 133, "height": 190, "qty": 12},
        {"width": 126, "height": 170, "qty": 182},
        {"width": 126, "height": 70, "qty": 212},
        {"width": 95, "height": 60, "qty": 316},
        {"width": 84, "height": 120, "qty": 210},
        {"width": 84, "height": 50, "qty": 576},
        {"width": 80, "height": 150, "qty": 20},
        {"width": 45, "height": 50, "qty": 150},
    ]

    carpets = [Carpet(id=i+1, **d) for i, d in enumerate(carpets_data)]

    groups = build_groups(carpets, min_width=370, max_width=400)
    for g in groups:
        print(g.summary())


if __name__ == "__main__":
    run_demo()