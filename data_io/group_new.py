
from typing import List
from core.models import Rectangle, UsedItem, Group
from data_io.excel_reader import read_input_excel  # ← هذا هو الملف الذي أرسلته أنت


def form_groups_by_width(rectangles: List[Rectangle], W_MIN: int, W_MAX: int) -> List[Group]:
    """
    تشكل مجموعات من المستطيلات بناءً على نطاق العرض فقط.
    """
    # 1️⃣ فرز تنازلي حسب العرض
    rects = sorted(rectangles, key=lambda r: r.width, reverse=True)

    groups: List[Group] = []
    used = set()  # تتبع العناصر المستخدمة
    group_id = 1

    # 2️⃣ البدء بتشكيل المجموعات
    for rect in rects:
        if rect.id in used:
            continue

        current_items: List[UsedItem] = []
        current_width = rect.width
        used.add(rect.id)
        current_items.append(
            UsedItem(rect_id=rect.id, width=rect.width, length=rect.length,
                     used_qty=1, original_qty=rect.qty)
        )

        # نحاول إضافة مستطيلات أصغر لتكملة المجال
        for other in rects:
            if other.id in used:
                continue
            tentative_width = current_width + other.width
            if tentative_width <= W_MAX:
                current_width = tentative_width
                used.add(other.id)
                current_items.append(
                    UsedItem(rect_id=other.id, width=other.width,
                             length=other.length, used_qty=1, original_qty=other.qty)
                )
            if current_width >= W_MIN:
                break  # المجموعة مكتملة

        groups.append(Group(id=group_id, items=current_items))
        group_id += 1

    return groups


def build_groups_from_excel(path: str, W_MIN: int, W_MAX: int) -> List[Group]:
    """
    قراءة ملف Excel ثم تكوين المجموعات تلقائيًا.
    """
    # قراءة الملف
    carpets = read_input_excel(path)

    # تكوين المجموعات
    groups = form_groups_by_width(carpets, W_MIN, W_MAX)

    return groups