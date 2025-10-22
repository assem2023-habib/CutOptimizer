"""
فئة GreedyGrouper - تجميع السجاد بالخوارزمية الجشعة
====================================================

هذه الفئة تحتوي على الخوارزمية المحسنة لتجميع السجاد مع تقسيم المنطق إلى توابع منفصلة
لسهولة الفهم والتعديل والاختبار.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
from .models import Rectangle, UsedItem, Group

from .optional_partner_grouper import create_groups_with_optional_partner


class GreedyGrouper:
    """
    فئة لتجميع السجاد بالخوارزمية الجشعة مع إمكانية التخصيص والتوسع.
    """

    def __init__(self,
                 min_width: int,
                 max_width: int,
                 tolerance_length: int,
                 start_with_largest: bool = True,
                 allow_split_rows: bool = True,
                 start_group_id: int = 1):
        """
        تهيئة مُجمّع السجاد الجشع.

        المعاملات:
        -----------
        min_width : int
            الحد الأدنى للعرض المسموح
        max_width : int
            الحد الأقصى للعرض المسموح
        tolerance_length : int
            حدود السماحية للطول
        start_with_largest : bool
            البدء بالعناصر الأكبر عرضاً (افتراضي: True)
        allow_split_rows : bool
            السماح بتقسيم الصفوف (افتراضي: True)
        start_group_id : int
            رقم المجموعة البداية (افتراضي: 1)
        """
        self.min_width = min_width
        self.max_width = max_width
        self.tolerance_length = tolerance_length
        self.start_with_largest = start_with_largest
        self.allow_split_rows = allow_split_rows
        self.start_group_id = start_group_id

        # بيانات سيتم تهيئتها عند الحاجة
        self.carpets_sorted: List[Rectangle] = []
        self.id_map: Dict[int, Rectangle] = {}
        self.original_qty_map: Dict[int, int] = {}
        self.remaining_qty: Dict[int, int] = {}
        self.widths_map: Dict[int, List[int]] = defaultdict(list)
        self.groups: List[Group] = []
        self.group_id = start_group_id
        self.skipped_ids: Set[int] = set()

    def group_carpets(self, carpets: List[Rectangle]) -> Tuple[List[Group], List[Rectangle]]:
        """
        الدالة الرئيسية لتجميع السجاد.

        المعاملات:
        -----------
        carpets : List[Rectangle]
            قائمة السجاد المراد تجميعه

        الإرجاع:
        --------
        Tuple[List[Group], List[Rectangle]]
            (المجموعات المُشكّلة، العناصر المتبقية)
        """
        self._initialize_data(carpets)
        self._process_grouping()
        return self.groups, self._prepare_remaining()

    def _initialize_data(self, carpets: List[Rectangle]) -> None:
        """تهيئة البيانات الأولية للتجميع."""
        # فرز السجاد
        self.carpets_sorted = sorted(carpets,
                                   key=lambda r: (r.width, r.length),
                                   reverse=self.start_with_largest)

        # خرائط المعرفات
        self.id_map = {r.id: r for r in self.carpets_sorted}
        self.original_qty_map = {r.id: r.qty for r in self.carpets_sorted}
        self.remaining_qty = {r.id: r.qty for r in self.carpets_sorted}

        # خريطة العروض
        self.widths_map.clear()
        for r in self.carpets_sorted:
            self.widths_map[r.width].append(r.id)

        # تهيئة المجموعات والمعرفات
        self.groups = []
        self.group_id = self.start_group_id
        self.skipped_ids.clear()

    def _process_grouping(self) -> None:
        """العملية الرئيسية للتجميع."""
        safety_counter = 0
        max_iterations = 5000

        while safety_counter < max_iterations:
            safety_counter += 1

            # اختيار العنصر الأساسي التالي
            primary = self._select_next_primary()
            if primary is None:
                break

            # محاولة تشكيل مجموعة
            if self._try_create_group(primary):
                continue  # تم تشكيل مجموعة بنجاح

            # إذا لم يتم تشكيل مجموعة، معالجة العنصر الأساسي كمجموعة وحيدة
            self._handle_single_item_group(primary)

        # تنظيف العناصر ذات الكمية الصفرية
        self._cleanup_zero_quantities()

        # مرحلة جديدة: تشكيل مجموعات مع تكرار وإمكانية شريك
        self.groups, self.remaining_qty, self.id_map, self.group_id = create_groups_with_optional_partner(
            self.carpets_sorted,
            self.remaining_qty,
            self.original_qty_map,
            self.id_map,
            self.groups,
            self.group_id,
            self.min_width,
            self.max_width,
            self.tolerance_length
        )

        # المرحلة النهائية: تشكيل مجموعات من عنصر واحد فقط (مكرر) لتحقيق أقصى استفادة
        self._create_single_element_groups()
    def _create_single_element_groups(self) -> None:
        """تشكيل مجموعات من عنصر واحد مكرر لتحقيق أقصى استفادة من البواقي."""
        # قائمة مؤقتة بالعناصر المتبقية للحسابات فقط
        current_remaining = [Rectangle(r.id, r.width, r.length, self.remaining_qty.get(r.id, 0))
                           for r in self.carpets_sorted if self.remaining_qty.get(r.id, 0) > 0]

        # المرحلة النهائية: تشكيل مجموعات من عنصر واحد فقط (مكرر) لتحقيق أقصى استفادة
        # الشرط: العرض الكلي = مجموع عرض الإدخالات (بدون ضرب في الكمية)
        # السماحية: نوزع الكميات بالتساوي بين الإدخالات بحيث يكون الفرق 0 <= tolerance_length/length
        for rect in list(current_remaining):
            if rect.qty <= 0:
                continue

            # الحصول على البيانات الأصلية من self.carpets_sorted
            original_rect = None
            for orig in self.carpets_sorted:
                if orig.id == rect.id:
                    original_rect = orig
                    break

            if original_rect is None:
                continue

            w = rect.width
            L = rect.length if rect.length > 0 else 1

            # حدود عدد الإدخالات الممكنة حسب العرض
            k_min = (self.min_width + w - 1) // w
            k_max = self.max_width // w
            if k_min <= 0:
                k_min = 1
            if k_max <= 0 or k_min > k_max:
                continue

            # طالما يمكننا تشكيل مجموعة صالحة، استمر
            while self.remaining_qty.get(rect.id, 0) > 0:
                Q = self.remaining_qty[rect.id]  # استخدم الكمية الأصلية
                best_k = 0
                best_used = 0
                best_each = 0

                # دلتا الكمية المسموحة بين الإدخالات (نختار توزيعاً متساوياً => الفارق = 0)
                delta_max = self.tolerance_length // L

                # جرّب جميع قيم k الممكنة واختَر ما يزيد الاستخدام
                for k in range(k_max, k_min - 1, -1):
                    total_w = k * w
                    if total_w < self.min_width or total_w > self.max_width:
                        continue

                    # توزيع متساوٍ يحقق الفارق 0 <= delta_max دائماً
                    q_each = Q // k
                    if q_each <= 0:
                        continue

                    used = k * q_each
                    if used > best_used:
                        best_used = used
                        best_k = k
                        best_each = q_each

                if best_used <= 0 or best_k <= 0 or best_each <= 0:
                    break  # لا يمكن تشكيل مزيد من المجموعات

                # بناء المجموعة باستخدام best_k إدخالاً من نفس العنصر وبنفس الكمية لكل إدخال
                group_items = []
                for _ in range(best_k):
                    group_items.append(
                        UsedItem(
                            rect_id=rect.id,
                            width=w,
                            length=L if L != 1 else rect.length,
                            used_qty=best_each,
                            original_qty=Q
                        )
                    )

                new_group = Group(id=self.group_id, items=group_items)

                # تحقق العرض عبر models.Group.total_width()
                if self.min_width <= new_group.total_width() <= self.max_width:
                    # تحقق السماحية: الفارق بين أي إدخالين = |best_each - best_each| * L = 0 <= tolerance_length

                    # خصم الكمية من البيانات الأصلية وإضافة المجموعة
                    self.remaining_qty[rect.id] -= best_used
                    self.id_map[rect.id].qty = self.remaining_qty[rect.id]

                    self.groups.append(new_group)
                    self.group_id += 1
                else:
                    # لا يمكن إنشاء مجموعة بعرض صالح
                    break

    def _select_next_primary(self) -> Optional[Rectangle]:
        """اختيار العنصر الأساسي التالي للمعالجة."""
        for r in self.carpets_sorted:
            if (self.remaining_qty.get(r.id, 0) > 0 and
                r.width <= self.max_width and
                r.id not in self.skipped_ids):
                return r
        return None

    def _try_create_group(self, primary: Rectangle) -> bool:
        """محاولة تشكيل مجموعة مع العنصر الأساسي."""
        primary_avail = self.remaining_qty[primary.id]
        group_created = False

        # تجربة كميات مختلفة من العنصر الأساسي
        for use_primary in range(primary_avail, 0, -1):
            if self._try_form_group_with_primary(primary, use_primary):
                group_created = True
                break

        return group_created

    def _try_form_group_with_primary(self, primary: Rectangle, use_primary: int) -> bool:
        """محاولة تشكيل مجموعة بكمية محددة من العنصر الأساسي."""
        ref_total_len = primary.length * use_primary

        # إنشاء عناصر المجموعة المبدئية
        chosen_items = [UsedItem(primary.id, primary.width, primary.length,
                               use_primary, self.original_qty_map.get(primary.id, 0))]
        chosen_width = primary.width

        # العرض المتبقي المسموح
        min_rem = max(self.min_width - chosen_width, 0)
        max_rem = self.max_width - chosen_width

        # نسخة مؤقتة من الكميات
        temp_qty = dict(self.remaining_qty)
        temp_qty[primary.id] = max(0, temp_qty.get(primary.id, 0) - use_primary)

        # محاولة إضافة شركاء
        if not self._add_partners(chosen_items, chosen_width, ref_total_len,
                                 min_rem, max_rem, temp_qty):
            return False

        # التحقق من صحة المجموعة النهائية
        if self._validate_and_commit_group(chosen_items, temp_qty):
            return True

        # إذا لم نتمكن من إضافة شركاء أو لم نصل للحد الأدنى، جرب تكرار الكتل
        if chosen_width < self.min_width:
            if self._try_repeat_blocks(chosen_items, chosen_width, ref_total_len, temp_qty):
                # التحقق من صحة المجموعة بعد إضافة التكرارات
                if self._validate_and_commit_group(chosen_items, temp_qty):
                    return True

        return False

    def _add_partners(self, chosen_items: List[UsedItem], chosen_width: int,
                     ref_total_len: int, min_rem: int, max_rem: int,
                     temp_qty: Dict[int, int]) -> bool:
        """إضافة شركاء للمجموعة."""
        # ترتيب العروض تنازلياً
        candidate_widths = sorted(self.widths_map.keys(), reverse=True)

        for w in candidate_widths:
            if chosen_width + w > self.max_width:
                continue

            for cid in self.widths_map[w]:
                if cid == chosen_items[0].rect_id:  # تجنب نفس العنصر الأساسي
                    continue

                avail = temp_qty.get(cid, 0)
                if avail <= 0:
                    continue

                cand = self.id_map[cid]

                # تجنب القسمة على الصفر
                if cand.length <= 0:
                    continue

                # حساب الكمية المثالية
                desired_qty = max(1, int(round(ref_total_len / cand.length)))
                take = min(desired_qty, avail)

                if take <= 0:
                    continue

                cand_total_len = cand.length * take
                diff = abs(cand_total_len - ref_total_len)

                # التحقق من الشروط
                if diff <= self.tolerance_length and chosen_width + cand.width <= self.max_width:
                    chosen_items.append(UsedItem(cid, cand.width, cand.length,
                                               take, self.original_qty_map.get(cid, 0)))
                    chosen_width += cand.width
                    temp_qty[cid] = max(0, temp_qty[cid] - take)

                    # التحقق من الوصول للحد الأدنى للعرض
                    if chosen_width >= self.min_width:
                        return True

    def _try_repeat_blocks(self, chosen_items: List[UsedItem], chosen_width: int,
                          ref_total_len: int, temp_qty: Dict[int, int]) -> bool:
        """محاولة تكرار الكتل للوصول للحد الأدنى للعرض."""
        # قائمة الكتل القابلة للتكرار (الأساسية والشركاء)
        repeatable_blocks: List[Tuple[int, int, int, int]] = []

        # إضافة الكتلة الأساسية للتكرار إذا توفرت الكمية
        if temp_qty.get(chosen_items[0].rect_id, 0) >= chosen_items[0].used_qty and chosen_width + chosen_items[0].width <= self.max_width:
            repeatable_blocks.append((chosen_items[0].rect_id, chosen_items[0].width, chosen_items[0].length, chosen_items[0].used_qty))

        # إضافة باقي الكتل للتكرار
        for item in chosen_items[1:]:  # تخطي العنصر الأساسي
            if temp_qty.get(item.rect_id, 0) >= item.used_qty and chosen_width + item.width <= self.max_width:
                repeatable_blocks.append((item.rect_id, item.width, item.length, item.used_qty))

        # ترتيب الكتل حسب العرض تنازلياً
        repeatable_blocks.sort(key=lambda t: t[1], reverse=True)

        # محاولة إضافة التكرارات
        for rid, rwidth, rlength, rqty_block in repeatable_blocks:
            while (chosen_width < self.min_width and
                   temp_qty.get(rid, 0) >= rqty_block and
                   chosen_width + rwidth <= self.max_width):

                # التحقق من السماحية في الطول
                if abs(rlength * rqty_block - ref_total_len) > self.tolerance_length:
                    break

                chosen_items.append(UsedItem(rid, rwidth, rlength, rqty_block, self.original_qty_map.get(rid, 0)))
                chosen_width += rwidth
                temp_qty[rid] = max(0, temp_qty[rid] - rqty_block)

                if chosen_width >= self.min_width:
                    return True

        return False

    def _validate_and_commit_group(self, chosen_items: List[UsedItem],
                                  temp_qty: Dict[int, int]) -> bool:
        """التحقق من صحة المجموعة وإضافتها إذا كانت صالحة."""
        total_width = sum(item.width for item in chosen_items)

        # التحقق من النطاق المسموح للعرض
        if not (self.min_width <= total_width <= self.max_width):
            return False

        # قيد 1: التحقق من عدم تكرار عنصر واحد
        unique_rect_ids = set(item.rect_id for item in chosen_items)
        if len(unique_rect_ids) == 1:
            return False  # مجموعة من عنصر واحد مكرر

        # قيد 2: التحقق من عدم تكرار المجموعات المتطابقة
        if self._is_duplicate_group(chosen_items):
            return False

        # إضافة المجموعة وتحديث المخزون
        self._commit_group(chosen_items)
        return True

    def _is_duplicate_group(self, chosen_items: List[UsedItem]) -> bool:
        """التحقق من تكرار المجموعة مع المجموعات الموجودة."""
        # ترتيب العناصر حسب المعرف والطول
        new_items = sorted(chosen_items, key=lambda x: (x.rect_id, x.length))
        new_signatures = [(item.rect_id, item.length) for item in new_items]

        for existing_group in self.groups:
            existing_items = sorted(existing_group.items, key=lambda x: (x.rect_id, x.length))
            existing_signatures = [(item.rect_id, item.length) for item in existing_items]

            if existing_signatures == new_signatures:
                return True

        return False

    def _commit_group(self, chosen_items: List[UsedItem]) -> None:
        """إضافة المجموعة وتحديث المخزون."""
        # تحديث المخزون الفعلي
        for item in chosen_items:
            self.remaining_qty[item.rect_id] = max(0,
                self.remaining_qty.get(item.rect_id, 0) - item.used_qty)
            self.id_map[item.rect_id].qty = self.remaining_qty[item.rect_id]

        # إضافة المجموعة
        self.groups.append(Group(self.group_id, chosen_items))
        self.group_id += 1

    def _handle_single_item_group(self, primary: Rectangle) -> None:
        """معالجة العنصر الأساسي كمجموعة وحيدة إذا لم يتم تشكيل مجموعة."""
        if self.min_width <= primary.width <= self.max_width:
            use = 1
            self.remaining_qty[primary.id] = max(0, self.remaining_qty.get(primary.id, 0) - use)
            self.id_map[primary.id].qty = self.remaining_qty[primary.id]

            self.groups.append(Group(self.group_id, [
                UsedItem(primary.id, primary.width, primary.length, use,
                        self.original_qty_map.get(primary.id, 0))
            ]))
            self.group_id += 1
        else:
            # إضافة العنصر إلى قائمة المُتجاهلين
            self.skipped_ids.add(primary.id)

    def _cleanup_zero_quantities(self) -> None:
        """تنظيف العناصر ذات الكمية الصفرية."""
        zero_qty_ids = [k for k, v in self.remaining_qty.items() if v <= 0]
        for k in zero_qty_ids:
            del self.remaining_qty[k]

    def _prepare_remaining(self) -> List[Rectangle]:
        """إعداد قائمة العناصر المتبقية."""
        remaining = []
        for r in self.carpets_sorted:
            q = self.remaining_qty.get(r.id, 0)
            if q > 0:
                remaining.append(Rectangle(r.id, r.width, r.length, q))
        return remaining


