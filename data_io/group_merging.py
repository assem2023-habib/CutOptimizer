"""
وحدة دمج المجموعات
===================

تحتوي على الدوال المتعلقة بدمج المجموعات المتطابقة
وإدارة تواقيع المجموعات.
"""

from typing import List, Dict, Tuple
from core.models import Group, UsedItem


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
