# from typing import List, Tuple, Dict, Optional
# from collections import defaultdict
# from .models import Rectangle, UsedItem, Group

# def group_carpets_greedy(carpets: List[Rectangle],
#                          min_width: int,
#                          max_width: int,
#                          tolerance_length: int,
#                          start_with_largest: bool = True,
#                          allow_split_rows: bool = True,
#                          start_group_id: int = 1
#                          ) -> Tuple[list[Group], list[Rectangle]]:
#     """
#     Greedy grouping algorithm:
#     - Start with largest width (if start_with_largest = True)
#     - For each primary rectangle type, try using quantities from max->1 to find a pairing (or alone)
#       that yields total_width in [min_width, max_width] and partner total_length close to primary_total_length
#       within tolerance_length.
#     - If found, deduct used quantities and create a Group.
#     - Continue until no more usable rectangles.
#     Returns: (groups, remaining_rectangles_with_remaining_qty)
#     """

#     # Sort
#     carpets_sorted = sorted(carpets, key=lambda r: r.width, reverse= start_with_largest)
#     id_map = {r.id: r for r in carpets_sorted}
#     remaining_qty: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}
#     # widths map: width -> list of rectangle ids (stable order)
#     skipped_ids = set()

#     def any_available():
#         return any(q > 0 and id_map[k].width <= max_width and k not in skipped_ids for k, q in remaining_qty.items())

#     widths_map = defaultdict(list)
#     for r in carpets_sorted:
#         widths_map[r.width].append(r.id)

#     group: list[Group] = []
#     group_id = start_group_id

#     # Keep track of rectangle ids that cannot currently form a group as primary,
#     # to avoid infinite loops while preserving their remaining quantities.
#     frozen_primary_ids = set()

#     while True:
#         # pick primary candidate (first available in sorted list whose width <= max_width)
#         primary = None
#         for r in carpets_sorted:
#             if remaining_qty.get(r.id, 0) > 0 and r.width <= max_width and r.id not in skipped_ids:
#                 primary = r
#                 break
        
#         if primary is None:
#             break

#         primary_avail = remaining_qty[primary.id]
#         group_created = False

#         # try using as many primary pieces as possible, decreasing to 1
#         for use_primary in range(primary_avail, 0, -1):
#             ref_total_len = primary.length * use_primary
#             chosen_items = [UsedItem(primary.id, primary.width, primary.length, use_primary, remaining_qty[primary.id])]
#             chosen_width = primary.width

#             # target remaining width interval after placing primary
#             min_rem = max(min_width - chosen_width, 0)
#             max_rem = max_width - chosen_width

#             # attempt to fill remaining width by greedy picking other widths (largest first)
#             # Work on a temporary view of available quantities (do not modify remaining_qty yet)
#             temp_qty = dict(remaining_qty)

#             # We'll choose up to many different types until chosen_width >= min_width or no candidate left
#             # Candidate widths sorted descending to prefer larger widths
#             candidate_widths = sorted(widths_map.keys(), reverse=True)
#             for w in candidate_widths:
#                 # if adding this width would exceed max_width, skip
#                 if chosen_width + w > max_width:
#                     continue
#                 # iterate ids that have this width
#                 for cid in widths_map[w]:
#                     if cid == primary.id:
#                         # skip reusing the primary as a partner (already included)
#                         continue
#                     avail = temp_qty.get(cid, 0)
#                     if avail <= 0:
#                         continue
#                     cand = id_map[cid]
#                     # desired qty to match lengths
#                     desired_qty = max(1, int(round(ref_total_len / cand.length)))
#                     take = min(desired_qty, avail)
#                     if take <= 0:
#                         continue
#                     cand_total_len = cand.length * take
#                     diff = abs(cand_total_len - ref_total_len)
#                     # accept partner if diff within tolerance and width fits
#                     if diff <= tolerance_length and chosen_width + cand.width <= max_width:
#                         chosen_items.append(UsedItem(cid, cand.width, cand.length, take, remaining_qty[cid]))
#                         chosen_width += cand.width
#                         temp_qty[cid] -= take
#                         break # move to next candidate width (we only use one type per width slot unless duplicates exist)
#                 # early stop if we reached required min width
#                 if chosen_width >= min_width:
#                     break
            
#             # after trying to fill partner, check if chosen_width within [min, max]
#             if min_width <= chosen_width <= max_width:
#                 for it in chosen_items:
#                     remaining_qty[it.rect_id] -= it.used_qty
#                     if remaining_qty[it.rect_id] < 0:
#                         remaining_qty[it.rect_id] = 0
#                     # مزامنة الكائن الأصلي مع الكمية المتبقية
#                     id_map[it.rect_id].qty = remaining_qty[it.rect_id]
#                 group.append(Group(group_id, chosen_items))
#                 group_id += 1
#                 group_created = True
#                 break

#         if not group_created:
#             if min_width <= primary.width <= max_width:
#                 use = 1
#                 remaining_qty[primary.id] -= use
#                 if remaining_qty[primary.id] < 0:
#                     remaining_qty[primary.id] = 0
#                 id_map[primary.id].qty = remaining_qty[primary.id]
#                 group.append(Group(group_id, [UsedItem(primary.id, primary.width, primary.length, use, primary.qty)]))
#                 group_id += 1
#             else:
#                 skipped_ids.add(primary.id)

#     # prepare remaining rectangles list
#     remaining = []
#     for r in carpets_sorted:
#         q = remaining_qty.get(r.id, 0)
#         if q > 0:
#             remaining.append(Rectangle(r.id, r.width, r.length, q))
#     return group, remaining
