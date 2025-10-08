from core.models import Rectangle, UsedItem, Group
from typing import List, Tuple, Dict
import copy


def form_remaining_groups(remainings: List[Rectangle],
                          min_width: int,
                          max_width: int,
                          tolerance: int,
                          start_group_id: int = 1000) -> List[Group]:
    """
    محاولة تشكيل مجموعات جديدة من البواقي المتبقية حتى لا يمكن تشكيل أي مجموعة إضافية.
    """
    # نرتب البواقي تنازليًا حسب العرض
    remainings = sorted([r for r in remainings if r.qty > 0],
                        key=lambda r: r.width,
                        reverse=True)

    formed_groups: List[Group] = []
    group_id = start_group_id

    # طالما هناك بواقي نحاول تشكيل مجموعات
    while True:
        group_items: List[UsedItem] = []
        total_width = 0
        base_length = None

        # نبدأ بأكبر عرض متاح
        for rect in remainings:
            if rect.qty <= 0:
                continue

            if not group_items:
                # العنصر الأساسي
                base_length = rect.length
                total_width = rect.width
                use_qty = rect.qty  # يمكن استخدام كامل الكمية أو جزء منها
                group_items.append(
                    UsedItem(rect_id=rect.id, width=rect.width,
                             length=rect.length, used_qty=use_qty, original_qty=rect.qty)
                )
                rect.qty -= use_qty
            else:
                # نحاول إضافة عنصر آخر
                diff_len = abs(rect.length - base_length)
                if diff_len > tolerance:
                    continue  # تخطى هذا العنصر

                if total_width + rect.width > max_width:
                    continue  # المجموع سيتجاوز الحد الأعلى

                tentative_width = total_width + rect.width
                if tentative_width < min_width:
                    # نضيفه ونستمر بالبحث
                    use_qty = min(rect.qty, 1)
                    total_width = tentative_width
                    rect.qty -= use_qty
                    group_items.append(
                        UsedItem(rect_id=rect.id, width=rect.width,
                                 length=rect.length, used_qty=use_qty, original_qty=rect.qty)
                    )
                elif min_width <= tentative_width <= max_width:
                    # وجدنا مجموعة صالحة ✅
                    use_qty = min(rect.qty, 1)
                    total_width = tentative_width
                    rect.qty -= use_qty
                    group_items.append(
                        UsedItem(rect_id=rect.id, width=rect.width,
                                 length=rect.length, used_qty=use_qty, original_qty=rect.qty)
                    )
                    break  # المجموعة اكتملت

        # إذا لم نستطع تكوين مجموعة جديدة — نوقف
        if not group_items or total_width < min_width:
            break

        # نحفظ المجموعة التي شكلناها
        formed_groups.append(Group(id=group_id, items=group_items))
        group_id += 1

        # نحذف العناصر التي انتهت كمياتها
        remainings = [r for r in remainings if r.qty > 0]

        # لو انتهت كل البواقي، نتوقف
        if not remainings:
            break

    return formed_groups

def lengths_within_tolerance(items: List[UsedItem], tolerance: int) -> bool:
    totals = [it.length * it.used_qty for it in items]
    if not totals:
        return True
    return (max(totals) - min(totals)) <= tolerance

def normalize_group_signature(items: List[UsedItem]) -> Tuple[Tuple[int,int], ...]:
    # تجميع الكميات لكل rect_id لإنشاء توقيع ثابت (rect_id -> total_used_qty)
    agg: Dict[int,int] = {}
    for it in items:
        agg[it.rect_id] = agg.get(it.rect_id, 0) + int(it.used_qty)
    return tuple(sorted(((rid, qty) for rid, qty in agg.items()), key=lambda x: x[0]))

def form_remaining_groups_with_repeats(
    remainings: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance: int,
    start_group_id: int = 1000,
    max_base_use_try: int = 500
) -> Tuple[List[Group], List[Rectangle]]:
    """
    تشكيل مجموعات من البواقي مع السماح بتكرار نفس النوع (إضافة شرائط مكررة).
    - كل تكرار يُمثل UsedItem منفصل في نفس المجموعة (يضيف العرض مرة أخرى).
    - نجرب كميات مرجعية كبيرة أولا (لتفادي حلقة qty=1).
    """

    # نسخة للعمل
    stock = {r.id: Rectangle(r.id, r.width, r.length, r.qty) for r in remainings}
    # حفظ الكميات الأصلية (للـ original_qty في UsedItem)
    original_qty = {r.id: r.qty for r in remainings}

    groups: List[Group] = []
    seen_signatures = set()
    gid = start_group_id

    progress = True
    SAFETY = 20000
    iterations = 0

    while progress and iterations < SAFETY:
        iterations += 1
        progress = False

        # بنية قائمة مرشحين مرتبة تنازليًا حسب العرض
        candidates = sorted([stock[rid] for rid in stock if stock[rid].qty > 0],
                            key=lambda x: x.width, reverse=True)

        if not candidates:
            break

        # نحاول كل مرشح كقاعدة
        for base in candidates:
            if base.qty <= 0:
                continue
            if base.width > max_width:
                # شريط بعرض أكبر من الحد الأعلى لا يمكن استخدامه
                continue

            # نحدّد أقصى محاولة للـ base_used_qty لتفادي حلقات طويلة
            max_try = min(base.qty, max_base_use_try)

            # نجرب الاستخدام المرجعي بدءًا من الأكبر إلى الأصغر
            for base_use in range(max_try, 0, -1):
                ref_total_len = base.length * base_use

                # نسخة مؤقتة من الكميات للحساب التجريبي
                temp_stock = {rid: Rectangle(r.id, r.width, r.length, r.qty) for rid, r in stock.items()}

                # نعد أول شريط (القاعدة)
                items: List[UsedItem] = []
                # لا نأخذ إلا إذا كان لدينا كمية كافية
                if temp_stock[base.id].qty < base_use:
                    continue
                items.append(UsedItem(rect_id=base.id, width=base.width, length=base.length,
                                      used_qty=base_use, original_qty=original_qty.get(base.id, temp_stock[base.id].qty)))
                temp_stock[base.id].qty -= base_use
                current_width = base.width

                # الآن نحاول إضافة شرائط (يمكن أن تكون من نفس النوع أيضاً إن بقي)
                # نمر على المرشحين (بما فيهم القاعدة نفسها إذا بقيت كمية)
                cand_list = sorted([temp_stock[rid] for rid in temp_stock if temp_stock[rid].qty > 0],
                                   key=lambda x: x.width, reverse=True)

                for cand in cand_list:
                    # لا نضيف إذا تجاوز الحد الأعلى عند إضافة شريط جديد
                    if current_width + cand.width > max_width:
                        continue

                    # نحسب الكمية المطلوبة لتقارب الطول المرجعي
                    desired_qty = max(1, int(round(ref_total_len / cand.length)))

                    # نعتبر أولًا الحالة المثالية: desired_qty متوفرة
                    if cand.qty >= desired_qty:
                        if abs(cand.length * desired_qty - ref_total_len) <= tolerance:
                            # نضيف شريط واحد بهذا desired_qty
                            items.append(UsedItem(rect_id=cand.id, width=cand.width, length=cand.length,
                                                  used_qty=desired_qty, original_qty=original_qty.get(cand.id, cand.qty)))
                            temp_stock[cand.id].qty -= desired_qty
                            current_width += cand.width
                            # تحقق إن كملنا نطاق العرض
                            if current_width >= min_width:
                                break
                            else:
                                # يمكن إضافة نفس الـ cand شريطًا آخر إذا مازال متاحًا
                                # (أي تكرار النوع نفسه داخل نفس المجموعة)
                                # محاولة تكرار قدر الإمكان دون تجاوز max_width أو كميته
                                while temp_stock[cand.id].qty >= desired_qty and current_width + cand.width <= max_width:
                                    items.append(UsedItem(rect_id=cand.id, width=cand.width, length=cand.length,
                                                          used_qty=desired_qty, original_qty=original_qty.get(cand.id, cand.qty + desired_qty)))
                                    temp_stock[cand.id].qty -= desired_qty
                                    current_width += cand.width
                                    if current_width >= min_width:
                                        break
                                if current_width >= min_width:
                                    break
                        else:
                            # إن لم يتحقق شرط السماحية بالـ desired_qty، نجرب أخذ كامل المتوفر (partial)
                            take = cand.qty
                            if take > 0 and abs(cand.length * take - ref_total_len) <= tolerance:
                                # نأخذ كل المتوفر كشريط (partial)
                                items.append(UsedItem(rect_id=cand.id, width=cand.width, length=cand.length,
                                                      used_qty=take, original_qty=original_qty.get(cand.id, cand.qty)))
                                current_width += cand.width
                                temp_stock[cand.id].qty = 0
                                if current_width >= min_width:
                                    break
                            else:
                                # لا يناسب هذا المرشح حالياً
                                continue
                    else:
                        # cand.qty < desired_qty: نجرب استخدام take = cand.qty إذا يطابق السماحية
                        take = cand.qty
                        if take > 0 and abs(cand.length * take - ref_total_len) <= tolerance:
                            items.append(UsedItem(rect_id=cand.id, width=cand.width, length=cand.length,
                                                  used_qty=take, original_qty=original_qty.get(cand.id, cand.qty)))
                            current_width += cand.width
                            temp_stock[cand.id].qty = 0
                            if current_width >= min_width:
                                break
                        # وإلا نتخطى
                        continue

                # بعد المرور على المرشحين: هل كونّا مجموعة صالحة؟
                if min_width <= current_width <= max_width and lengths_within_tolerance(items, tolerance):
                    # توقيع لتفادي التكرار
                    sig = normalize_group_signature(items)
                    if sig in seen_signatures:
                        # دمج بسيط: لا نضيف مجموعة مكررة مجدداً
                        # (أو يمكنك هنا زيادة كميات في مجموعة موجودة بدل الإضافة الجديدة)
                        pass
                    else:
                        # نطبق التغييرات على المخزون الحقيقي (commit)
                        for it in items:
                            # اطرح من المخزون الأصلي
                            stock[it.rect_id].qty -= it.used_qty
                            if stock[it.rect_id].qty < 0:
                                stock[it.rect_id].qty = 0
                        # إنشاء المجموعة وتخزينها
                        groups.append(Group(id=gid, items=items))
                        seen_signatures.add(sig)
                        gid += 1
                        progress = True
                    # بعد تشكيل مجموعة ناجحة نبدأ من جديد من أعلى
                    break

                # إن لم تشكل مجموعة نعيد المحاولة بقيمة base_use أقل
            if progress:
                break

        # نهاية جولة البحث عن قواعد
        # نكرر طالما تحقق تقدم

    # بعد الخروج: نجهز القائمة النهائية للبواقي المتبقية
    final_remaining = [stock[rid] for rid in stock if stock[rid].qty > 0]
    # دمج المجموعات المتطابقة اختياريًا (هنا توقيعنا يمنع التكرار المباشر)
    return groups, final_remaining
