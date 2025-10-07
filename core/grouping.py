from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from .models import Rectangle, UsedItem, Group
import math


def group_carpets_greedy(carpets: List[Rectangle],
                         min_width: int,
                         max_width: int,
                         tolerance_length: int,
                         start_with_largest: bool = True,
                         allow_split_rows: bool = True,
                         start_group_id: int = 1
                         ) -> Tuple[list[Group], list[Rectangle]]:
    """
    Greedy grouping algorithm:
    - Start with largest width (if start_with_largest = True)
    - For each primary rectangle type, try using quantities from max->1 to find a pairing (or alone)
      that yields total_width in [min_width, max_width] and partner total_length close to primary_total_length
      within tolerance_length.
    - If found, deduct used quantities and create a Group.
    - Continue until no more usable rectangles.
    Returns: (groups, remaining_rectangles_with_remaining_qty)
    """

    # Sort rectangles
    carpets_sorted = sorted(carpets, key=lambda r: r.width, reverse=start_with_largest)
    id_map = {r.id: r for r in carpets_sorted}
    # ثابت: كميات أصلية كما جاءت من الإدخال
    original_qty_map: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}
    remaining_qty: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}

    # Map widths
    widths_map = defaultdict(list)
    for r in carpets_sorted:
        widths_map[r.width].append(r.id)

    groups: list[Group] = []
    group_id = start_group_id
    skipped_ids = set()

    # Safety counter to avoid infinite loops
    safety_counter = 0
    max_iterations = 5000

    while True:
        safety_counter += 1
        if safety_counter > max_iterations:
            print("⚠️ Safety break: exceeded max iterations, stopping loop")
            break

        # Pick primary candidate
        primary = None
        for r in carpets_sorted:
            if remaining_qty.get(r.id, 0) > 0 and r.width <= max_width and r.id not in skipped_ids:
                primary = r
                break

        if primary is None:
            break

        primary_avail = remaining_qty[primary.id]
        group_created = False

        # Try using as many primary pieces as possible
        for use_primary in range(primary_avail, 0, -1):
            ref_total_len = primary.length * use_primary
            chosen_items = [UsedItem(primary.id, primary.width, primary.length, use_primary, original_qty_map.get(primary.id, 0))]
            chosen_width = primary.width

            # Remaining width range
            min_rem = max(min_width - chosen_width, 0)
            max_rem = max_width - chosen_width

            # Work on temporary quantities
            temp_qty = dict(remaining_qty)
            # احجز كمية الأساس مبدئياً
            temp_qty[primary.id] = max(0, temp_qty.get(primary.id, 0) - use_primary)
            candidate_widths = sorted(widths_map.keys(), reverse=True)

            # Try to add partners
            for w in candidate_widths:
                if chosen_width + w > max_width:
                    continue
                for cid in widths_map[w]:
                    if cid == primary.id:
                        continue
                    avail = temp_qty.get(cid, 0)
                    if avail <= 0:
                        continue
                    cand = id_map[cid]

                    desired_qty = max(1, int(round(ref_total_len / cand.length)))
                    take = min(desired_qty, avail)
                    if take <= 0:
                        continue

                    cand_total_len = cand.length * take
                    diff = abs(cand_total_len - ref_total_len)

                    if diff <= tolerance_length and chosen_width + cand.width <= max_width:
                        chosen_items.append(UsedItem(cid, cand.width, cand.length, take, original_qty_map.get(cid, 0)))
                        chosen_width += cand.width
                        temp_qty[cid] = max(0, temp_qty[cid] - take)
                        break
                if chosen_width >= min_width:
                    break

            # If still below min_width, allow repeating blocks (including repeating primary) as separate entries
            if chosen_width < min_width:
                # primary block repeat (if quantities allow)
                repeatable_blocks: list[tuple[int,int,int,int]] = []
                if temp_qty.get(primary.id, 0) >= use_primary and chosen_width + primary.width <= max_width:
                    repeatable_blocks.append((primary.id, primary.width, primary.length, use_primary))

                # also allow repeating of any partner blocks with their desired block size if available
                for rid in list(temp_qty.keys()):
                    if rid == primary.id:
                        continue
                    cand = id_map[rid]
                    desired_block = max(1, int(round(ref_total_len / cand.length)))
                    if temp_qty[rid] >= desired_block and chosen_width + cand.width <= max_width:
                        repeatable_blocks.append((rid, cand.width, cand.length, desired_block))

                repeatable_blocks.sort(key=lambda t: t[1], reverse=True)
                for rid, rwidth, rlength, rqty_block in repeatable_blocks:
                    while chosen_width < min_width and temp_qty.get(rid, 0) >= rqty_block and chosen_width + rwidth <= max_width:
                        if abs(rlength * rqty_block - ref_total_len) > tolerance_length:
                            break
                        chosen_items.append(UsedItem(rid, rwidth, rlength, rqty_block, original_qty_map.get(rid, 0)))
                        chosen_width += rwidth
                        temp_qty[rid] = max(0, temp_qty[rid] - rqty_block)
                        if chosen_width >= min_width:
                            break

            # If valid group formed
            if min_width <= chosen_width <= max_width:
                # خصم نهائي من المخزون الفعلي
                for it in chosen_items:
                    remaining_qty[it.rect_id] = max(0, remaining_qty.get(it.rect_id, 0) - it.used_qty)
                    id_map[it.rect_id].qty = remaining_qty[it.rect_id]
                groups.append(Group(group_id, chosen_items))
                group_id += 1
                group_created = True
                break

        # If no group formed
        if not group_created:
            if min_width <= primary.width <= max_width:
                use = 1
                remaining_qty[primary.id] -= use
                if remaining_qty[primary.id] < 0:
                    remaining_qty[primary.id] = 0
                id_map[primary.id].qty = remaining_qty[primary.id]
                groups.append(Group(group_id, [UsedItem(primary.id, primary.width, primary.length, use, original_qty_map.get(primary.id, 0))]))
                group_id += 1
            else:
                skipped_ids.add(primary.id)

        # Clean up zero-quantity items
        for k in list(remaining_qty.keys()):
            if remaining_qty[k] <= 0:
                del remaining_qty[k]

        # Progress log every 10 groups
        if group_id % 10 == 0:
            print(f"🔹 Processed {group_id} groups so far... Remaining items: {sum(remaining_qty.values())}")

    # Prepare remaining rectangles
    remaining = []
    for r in carpets_sorted:
        q = remaining_qty.get(r.id, 0)
        if q > 0:
            remaining.append(Rectangle(r.id, r.width, r.length, q))

    return groups, remaining

def regroup_residuals(residuals, min_width, max_width, tolerance):
    """
    خوارزمية إعادة تجميع البواقي لتكوين مجموعات جديدة قابلة للاستخدام
    """
    # ترتيب البواقي حسب العرض تنازليًا
    residuals = sorted(residuals, key=lambda x: x['width'], reverse=True)
    new_groups = []

    while residuals:
        base = residuals[0]
        base_width = base['width']
        base_length = base['length']
        base_count = base['remaining']
        group = []
        total_width = base_width
        group_length = base_length

        # نبدأ بالمستطيل الأكبر عرضًا
        group.append({
            'id': base['id'],
            'width': base_width,
            'length': base_length,
            'used': base_count
        })
        residuals[0]['remaining'] = 0  # استُخدم بالكامل

        # نبحث عن قطع تكمل النطاق
        for i in range(1, len(residuals)):
            item = residuals[i]
            if item['remaining'] <= 0:
                continue

            new_width = total_width + item['width']
            if min_width <= new_width <= max_width:
                if abs(item['length'] - group_length) <= tolerance:
                    group.append({
                        'id': item['id'],
                        'width': item['width'],
                        'length': item['length'],
                        'used': item['remaining']
                    })
                    total_width += item['width']
                    residuals[i]['remaining'] = 0

        # إذا تشكّلت مجموعة فعالة
        if len(group) > 1:
            new_groups.append({
                'items': group,
                'total_width': total_width,
                'ref_length': group_length,
                'count_types': len(group)
            })

        # حذف العناصر المستخدمة
        residuals = [r for r in residuals if r['remaining'] > 0]

    return new_groups