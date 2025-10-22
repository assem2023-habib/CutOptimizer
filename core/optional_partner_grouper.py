"""
وحدة OptionalPartnerGrouper - تجميع مع شريك اختياري
=================================================

هذه الوحدة تحتوي على الدالة المستقلة لتجميع المجموعات مع شريك اختياري
"""

from typing import List, Dict
from .models import Rectangle, UsedItem, Group


def create_groups_with_optional_partner(
    carpets_sorted: List[Rectangle],
    remaining_qty: Dict[int, int],
    original_qty_map: Dict[int, int],
    id_map: Dict[int, Rectangle],
    groups: List[Group],
    group_id: int,
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> tuple:
    """
    تشكيل مجموعات مع تكرار العنصر الأعرض، إضافة شريك، وتجربة كميات تنازلية.

    المعاملات:
    -----------
    carpets_sorted : List[Rectangle]
        القائمة المرتبة للسجاد
    remaining_qty : Dict[int, int]
        الكميات المتبقية
    original_qty_map : Dict[int, int]
        الكميات الأصلية
    id_map : Dict[int, Rectangle]
        خريطة المعرفات
    groups : List[Group]
        المجموعات الحالية
    group_id : int
        رقم المجموعة التالي
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول

    الإرجاع:
    --------
    tuple
        (المجموعات المحدثة، الكميات المتبقية، خريطة المعرفات، رقم المجموعة التالي)
    """
    # نسخ الكميات لتجنب التعديل المباشر
    remaining_qty = remaining_qty.copy()
    id_map = {k: Rectangle(v.id, v.width, v.length, v.qty) for k, v in id_map.items()}  # نسخة عميقة
    groups = groups.copy()
    group_id = group_id

    def is_duplicate_group(chosen_items: List[UsedItem]) -> bool:
        """التحقق من تكرار المجموعة مع المجموعات الموجودة."""
        # ترتيب العناصر حسب المعرف والطول
        new_items = sorted(chosen_items, key=lambda x: (x.rect_id, x.length))
        new_signatures = [(item.rect_id, item.length) for item in new_items]

        for existing_group in groups:
            existing_items = sorted(existing_group.items, key=lambda x: (x.rect_id, x.length))
            existing_signatures = [(item.rect_id, item.length) for item in existing_items]

            if existing_signatures == new_signatures:
                return True

        return False

    def commit_group(chosen_items: List[UsedItem]) -> None:
        """إضافة المجموعة وتحديث المخزون."""
        nonlocal group_id  # Declare nonlocal before use
        
        # تحديث المخزون الفعلي
        for item in chosen_items:
            remaining_qty[item.rect_id] = max(0, remaining_qty.get(item.rect_id, 0) - item.used_qty)
            id_map[item.rect_id].qty = remaining_qty[item.rect_id]

        # إضافة المجموعة
        groups.append(Group(group_id, chosen_items))
        group_id += 1

    def validate_and_commit_group(chosen_items: List[UsedItem]) -> bool:
        """التحقق من صحة المجموعة وإضافتها إذا كانت صالحة."""
        total_width = sum(item.width for item in chosen_items)

        # التحقق من النطاق المسموح للعرض
        if not (min_width <= total_width <= max_width):
            return False

        # قيد 1: التحقق من عدم تكرار عنصر واحد
        unique_rect_ids = set(item.rect_id for item in chosen_items)
        if len(unique_rect_ids) == 1:
            return False  # مجموعة من عنصر واحد مكرر

        # قيد 2: التحقق من عدم تكرار المجموعات المتطابقة
        if is_duplicate_group(chosen_items):
            return False

        # إضافة المجموعة وتحديث المخزون
        commit_group(chosen_items)
        return True

    # المنطق الرئيسي للدالة
    # قائمة مؤقتة بالعناصر المتبقية مرتبة حسب العرض تنازلياً
    current_remaining = [Rectangle(r.id, r.width, r.length, remaining_qty.get(r.id, 0))
                       for r in carpets_sorted if remaining_qty.get(r.id, 0) > 0]
    current_remaining.sort(key=lambda r: r.width, reverse=True)

    for rect in list(current_remaining):
        if rect.qty <= 0:
            continue

        w = rect.width
        L = rect.length if rect.length > 0 else 1
        Q = remaining_qty[rect.id]

        # تكرار للعنصر الأساسي حتى نفاذ الكمية أو تشكيل مجموعات
        while Q > 0:
            # ابدأ بتكرار واحد، زد حتى الوصول إلى النطاق أو max_width
            chosen_items = [UsedItem(rect.id, w, L, 1, original_qty_map[rect.id])]
            chosen_width = w

            while len(chosen_items) * w <= max_width and sum(item.used_qty for item in chosen_items if item.rect_id == rect.id) < Q:
                chosen_items.append(UsedItem(rect.id, w, L, 1, original_qty_map[rect.id]))
                chosen_width = w * len(chosen_items)

            group = Group(id=0, items=chosen_items)
            if min_width <= group.total_width() <= max_width and len(chosen_items) > 1:
                # تحقق السماحية
                ref_len = group.ref_length()
                valid = True
                for item in chosen_items[1:]:
                    diff = abs(item.length * item.used_qty - ref_len)
                    if diff > tolerance_length:
                        valid = False
                        break

                if valid:
                    # استخدم validate_and_commit_group للتحقق من التكرار
                    if validate_and_commit_group(chosen_items):
                        Q = remaining_qty[rect.id]
                        continue
                    else:
                        # إعادة الكميات إذا لم يتم التشكيل
                        pass  # لا تحديث، لأن لم يتم خصم

            # إذا لم يصل، ابحث عن شريك
            if group.total_width() < min_width:
                total_used_primary = sum(item.used_qty for item in chosen_items if item.rect_id == rect.id)
                # جرب مع كل شريك ممكن
                candidate_rects = [r for r in carpets_sorted if r.id != rect.id and remaining_qty.get(r.id, 0) > 0]
                candidate_rects.sort(key=lambda r: r.width, reverse=True)

                for partner in candidate_rects:
                    p_w = partner.width
                    group_width = group.total_width()
                    if group_width + p_w > max_width:
                        continue

                    p_L = partner.length if partner.length > 0 else 1
                    p_Q = remaining_qty[partner.id]

                    # ابدأ بأكبر كمية ممكنة للشريك
                    ref_len = chosen_items[0].length * chosen_items[0].used_qty
                    desired_qty = max(1, int(round(ref_len / p_L)))
                    take = min(desired_qty, p_Q)

                    # جرب كميات تنازلية
                    for qty in range(take, 0, -1):
                        partner_total_len = p_L * qty
                        diff = abs(partner_total_len - ref_len)
                        if diff <= tolerance_length and group_width + p_w <= max_width:
                            new_width = group_width + p_w
                            if min_width <= new_width <= max_width:
                                # أنشئ المجموعة
                                all_items = chosen_items + [UsedItem(partner.id, p_w, p_L, qty, original_qty_map[partner.id])]
                                if len(set(item.rect_id for item in all_items)) > 1:
                                    # تحقق السماحية
                                    valid = True
                                    for item in all_items[1:]:
                                        diff = abs(item.length * item.used_qty - ref_len)
                                        if diff > tolerance_length:
                                            valid = False
                                            break

                                    if valid:
                                        # استخدم validate_and_commit_group
                                        if validate_and_commit_group(all_items):
                                            Q = remaining_qty[rect.id]
                                            break  # انتقل للشريك التالي أو العنصر التالي
                                        else:
                                            # إعادة الكميات إذا لم يتم التشكيل
                                            pass  # لا تحديث

            # إذا لم يتم تشكيل مجموعة، قلص الكمية وجرب مرة أخرى
            Q -= 1

    # تحقق إضافي: إلغاء أي مجموعة مكونة من عنصر واحد مكرر فقط
    groups_to_remove = []
    for group in groups:
        if len(set(item.rect_id for item in group.items)) < 2:
            groups_to_remove.append(group)

    for group in groups_to_remove:
        groups.remove(group)
        group_id -= 1
        # استعادة الكميات
        for item in group.items:
            remaining_qty[item.rect_id] += item.used_qty
            id_map[item.rect_id].qty = remaining_qty[item.rect_id]

    # تنظيف الكميات الصفرية
    zero_qty_ids = [k for k, v in remaining_qty.items() if v <= 0]
    for k in zero_qty_ids:
        del remaining_qty[k]

    return groups, remaining_qty, id_map, group_id
