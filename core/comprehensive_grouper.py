"""
مجمع شامل لتجميع السجاد - Comprehensive Grouper
===============================================

هذا الملف يطبق خوارزمية شاملة لتجميع السجاد بناءً على:
- البحث عن جميع الشركاء المحتملين لكل عنصر
- تشكيل جميع المجموعات الممكنة مع التقيد بالقيود
- استغلال أقصى الكميات المتاحة
- تطبيق التكرار الذكي للعناصر

المؤلف: نظام تحسين القطع الشامل
التاريخ: 2024
"""

from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
import copy
import os
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Safe import handling for both package and standalone execution
try:
    from .models import Rectangle, UsedItem, Group
except ImportError:
    from models import Rectangle, UsedItem, Group


class ComprehensiveGrouper:
    """
    مجمع شامل لتجميع السجاد مع البحث الشامل عن الشركاء والتكرار الذكي.
    """

    def __init__(self,
                 min_width: int,
                 max_width: int,
                 tolerance_length: int,
                 start_group_id: int = 1):
        """
        تهيئة المجمع الشامل.

        المعاملات:
        -----------
        min_width : int
            الحد الأدنى للعرض المسموح
        max_width : int
            الحد الأقصى للعرض المسموح
        tolerance_length : int
            حدود السماحية للطول
        start_group_id : int
            رقم المجموعة البداية (افتراضي: 1)
        """
        self.min_width = min_width
        self.max_width = max_width
        self.tolerance_length = tolerance_length
        self.start_group_id = start_group_id

        # بيانات العمل
        self.carpets: List[Rectangle] = []
        self.carpets_sorted: List[Rectangle] = []
        self.remaining_qty: Dict[int, int] = {}
        self.original_qty: Dict[int, int] = {}
        self.groups: List[Group] = []
        self.group_id: int = start_group_id

    def group_carpets(self, carpets: List[Rectangle]) -> Tuple[List[Group], List[Rectangle]]:
        """
        الدالة الرئيسية للتجميع الشامل.

        المعاملات:
        -----------
        carpets : List[Rectangle]
            قائمة السجاد المراد تجميعه

        الإرجاع:
        --------
        Tuple[List[Group], List[Rectangle]]
            (المجموعات المُشكّلة، العناصر المتبقية)
        """
        # تهيئة البيانات
        self._initialize_data(carpets)

        # ترتيب العناصر حسب الأولوية
        self._sort_carpets_by_priority()

        # المرحلة الأولى: البحث الشامل عن الشركاء
        self._comprehensive_partner_search()

        # المرحلة الثانية: تشكيل مجموعات من المتبقي
        self._process_remaining_items()

        # المرحلة النهائية: تكرار العناصر لاستغلال الكميات المتبقية
        self._final_repetition_optimization()

        return self.groups, self._get_final_remaining()

    def _initialize_data(self, carpets: List[Rectangle]) -> None:
        """تهيئة البيانات الأولية."""
        self.carpets = copy.deepcopy(carpets)
        self.remaining_qty = {r.id: r.qty for r in self.carpets}
        self.original_qty = {r.id: r.qty for r in self.carpets}
        self.groups = []
        self.group_id = self.start_group_id

    def _get_width_bin(self, width: int) -> str:
        """تصنيف العرض إلى فئات لتحسين البحث عن الشركاء."""
        if width >= 200:
            return "large"      # 200-240
        elif width >= 130:
            return "medium"     # 130-199
        elif width >= 70:
            return "small"      # 70-129
        else:
            return "tiny"       # 50-69

    def _find_compatible_width_bins(self, primary_bin: str) -> List[str]:
        """إيجاد فئات العرض المتوافقة مع الفئة الأساسية."""
        compatibility_map = {
            "large": ["medium", "small"],
            "medium": ["large", "small", "tiny"],
            "small": ["medium", "small", "tiny"],
            "tiny": ["small", "tiny"]
        }
        return compatibility_map.get(primary_bin, [])

    def _sort_carpets_by_priority(self) -> None:
        """ترتيب العناصر حسب الأولوية مع مراعاة فئات العرض وصعوبة التجميع."""
        def sort_key(carpet):
            bin_priority = {"large": 0, "medium": 1, "small": 2, "tiny": 3}
            width_bin = self._get_width_bin(carpet.width)

            # الأولوية: فئة العرض، ثم العرض، ثم الطول، ثم الكمية
            # نعطي أولوية أعلى للعناصر ذات الكميات الأكبر (أصعب في التجميع)
            return (bin_priority[width_bin], carpet.width, carpet.length, -carpet.qty)

        self.carpets_sorted = sorted(self.carpets, key=sort_key)

    def _comprehensive_partner_search(self) -> None:
        """البحث الشامل عن الشركاء وتشكيل المجموعات."""
        processed_items = set()

        for primary_idx, primary in enumerate(self.carpets_sorted):
            if primary.id in processed_items or self.remaining_qty[primary.id] <= 0:
                continue

            # البحث عن جميع الشركاء المحتملين مع كميات مختلفة من العنصر الأساسي
            all_possible_groups = self._find_all_possible_groups(primary)

            # ترتيب المجموعات حسب الكفاءة (الاستغلال الأمثل للكميات)
            all_possible_groups.sort(
                key=lambda group: self._calculate_group_efficiency(group),
                reverse=True
            )

            # تشكيل أفضل المجموعات
            for group_items in all_possible_groups:
                if self._is_valid_group(group_items):
                    # التحقق من توفر الكميات
                    if self._check_quantities_available(group_items):
                        self._create_and_commit_group(group_items)
                        self._update_quantities(group_items)
                        break

            processed_items.add(primary.id)

    def _find_all_possible_groups(self, primary: Rectangle) -> List[List[UsedItem]]:
        """البحث عن جميع المجموعات الممكنة للعنصر الأساسي مع تكرار تدريجي."""
        possible_groups = []
        max_qty = self.remaining_qty[primary.id]

        # تجربة كميات مختلفة من العنصر الأساسي مع تكرار تدريجي
        max_repetitions = self.max_width // primary.width

        for repetition in range(1, max_repetitions + 1):
            # حساب الكمية المطلوبة للتكرار الحالي
            qty_per_repetition = max(1, max_qty // repetition)
            total_qty_for_repetition = qty_per_repetition * repetition

            if total_qty_for_repetition > max_qty or total_qty_for_repetition <= 0:
                continue

            # حساب العرض الإجمالي للتكرار
            current_width = primary.width * repetition
            if current_width > self.max_width:
                continue

            ref_length = primary.length * total_qty_for_repetition
            remaining_width = self.max_width - current_width

            # إضافة المجموعة الأساسية من التكرار بدون شركاء
            base_group = []
            for _ in range(repetition):
                base_group.append(UsedItem(
                    rect_id=primary.id,
                    width=primary.width,
                    length=primary.length,
                    used_qty=qty_per_repetition,
                    original_qty=self.original_qty[primary.id]
                ))

            if self._is_valid_group(base_group):
                possible_groups.append(base_group)

            # البحث عن شركاء لملء العرض المتبقي
            if remaining_width > 0:
                partners = self._find_compatible_partners_for_repetition(
                    primary, total_qty_for_repetition, ref_length, current_width, remaining_width
                )

                # إضافة المجموعات مع الشركاء
                for partner_combination in partners:
                    group_items = base_group + partner_combination
                    if self._is_valid_group(group_items):
                        possible_groups.append(group_items)

        return possible_groups

    def _find_compatible_partners_for_repetition(self, primary: Rectangle, primary_qty: int,
                                                ref_length: int, current_width: int,
                                                remaining_width: int) -> List[List[UsedItem]]:
        """البحث عن شركاء لملء العرض المتبقي بعد تكرار العنصر الأساسي."""
        partners_list = []

        # تحديد فئة العرض للعنصر الأساسي وفئات التوافق
        primary_bin = self._get_width_bin(primary.width)
        compatible_bins = self._find_compatible_width_bins(primary_bin)

        # قائمة المرشحين الذين يمكن أن يملؤوا العرض المتبقي
        candidates = [
            r for r in self.carpets_sorted
            if (r.id != primary.id and self.remaining_qty[r.id] > 0 and
                r.width <= remaining_width and
                self._get_width_bin(r.width) in compatible_bins)
        ]

        # ترتيب المرشحين حسب التوافق مع العرض المتبقي والكمية
        candidates.sort(key=lambda r: (remaining_width - r.width, -r.qty, abs(r.length - (ref_length / primary_qty))))

        # استخدام البحث الشامل للعثور على تركيبات تملأ العرض المتبقي
        self._find_compatible_combinations_for_remaining_width(
            candidates, 0, current_width, ref_length, remaining_width, [], partners_list
        )

        return partners_list

    def _find_compatible_combinations_for_remaining_width(self, candidates: List[Rectangle],
                                                         index: int, current_width: int,
                                                         ref_length: int, remaining_width: int,
                                                         current_partners: List[UsedItem],
                                                         result: List[List[UsedItem]]) -> None:
        """البحث عن تركيبات تملأ العرض المتبقي بالضبط."""
        # إضافة الحل الحالي إذا كان يملأ العرض المتبقي بشكل جيد
        used_width = sum(item.width for item in current_partners)
        if remaining_width - used_width <= 20:  # سماحية صغيرة للعرض المتبقي
            result.append(current_partners.copy())

        if index >= len(candidates) or used_width >= remaining_width - 20:
            return

        candidate = candidates[index]

        # تجربة عدم استخدام هذا المرشح
        self._find_compatible_combinations_for_remaining_width(
            candidates, index + 1, current_width, ref_length, remaining_width,
            current_partners.copy(), result
        )

        # تجربة استخدام كميات مختلفة من هذا المرشح
        max_qty = self.remaining_qty[candidate.id]
        min_qty = max(1, ref_length // (candidate.length * 2)) if candidate.length > 0 else 1
        max_qty = min(max_qty, ref_length // candidate.length + 1) if candidate.length > 0 else max_qty

        for qty in range(min_qty, max_qty + 1):
            total_length = candidate.length * qty
            new_width = current_width + candidate.width

            if (new_width <= self.max_width and
                abs(total_length - ref_length) <= self.tolerance_length):

                new_partners = current_partners.copy()
                new_partners.append(UsedItem(
                    rect_id=candidate.id,
                    width=candidate.width,
                    length=candidate.length,
                    used_qty=qty,
                    original_qty=self.original_qty[candidate.id]
                ))

                self._find_compatible_combinations_for_remaining_width(
                    candidates, index + 1, new_width, ref_length, remaining_width,
                    new_partners, result
                )

    def _find_all_compatible_combinations(self, candidates: List[Rectangle],
                                         index: int, current_width: int,
                                         ref_length: int, current_partners: List[UsedItem],
                                         result: List[List[UsedItem]]) -> None:
        """البحث عن تركيبات تملأ العرض المتبقي بالضبط."""
        # إضافة الحل الحالي إذا كان يملأ العرض المتبقي بشكل جيد
        used_width = sum(item.width for item in current_partners)
        if len(candidates) - index <= 1 and used_width + candidates[index].width <= self.max_width:
            result.append(current_partners.copy() + [UsedItem(
                rect_id=candidates[index].id,
                width=candidates[index].width,
                length=candidates[index].length,
                used_qty=1,
                original_qty=self.original_qty[candidates[index].id]
            )])

        if index >= len(candidates) or used_width >= self.max_width:
            return

        candidate = candidates[index]

        # تجربة عدم استخدام هذا المرشح
        self._find_all_compatible_combinations(
            candidates, index + 1, current_width, ref_length,
            current_partners.copy(), result
        )

        # تجربة استخدام كميات مختلفة من هذا المرشح
        max_qty = self.remaining_qty[candidate.id]
        min_qty = max(1, ref_length // (candidate.length * 2)) if candidate.length > 0 else 1
        max_qty = min(max_qty, ref_length // candidate.length + 1) if candidate.length > 0 else max_qty
        max_qty = min(max_qty, ref_length // candidate.length + 2) if candidate.length > 0 else max_qty

        for qty in range(min_qty, max_qty + 1):
            total_length = candidate.length * qty
            new_width = current_width + candidate.width

            if (new_width <= self.max_width and
                abs(total_length - ref_length) <= self.tolerance_length):

                new_partners = current_partners.copy()
                new_partners.append(UsedItem(
                    rect_id=candidate.id,
                    width=candidate.width,
                    length=candidate.length,
                    used_qty=qty,
                    original_qty=self.original_qty[candidate.id]
                ))

                self._find_all_compatible_combinations(
                    candidates, index + 1, new_width, ref_length,
                    new_partners, result
                )

    def _calculate_group_efficiency(self, group_items: List[UsedItem]) -> float:
        """حساب كفاءة المجموعة (الاستغلال الأمثل للكميات)."""
        total_used_qty = sum(item.used_qty for item in group_items)
        total_original_qty = sum(item.original_qty for item in group_items)
        total_width = sum(item.width for item in group_items)

        if total_original_qty == 0:
            return 0

        # كفاءة = (الكمية المستخدمة / الكمية الأصلية) * (العرض / العرض الأقصى)
        efficiency = (total_used_qty / total_original_qty) * (total_width / self.max_width)
        return efficiency

    def _check_quantities_available(self, group_items: List[UsedItem]) -> bool:
        """التحقق من توفر الكميات المطلوبة."""
        for item in group_items:
            if self.remaining_qty[item.rect_id] < item.used_qty:
                return False
        return True

    def _try_single_item_repetition(self, carpet: Rectangle) -> bool:
        """محاولة تكرار عنصر واحد لتشكيل مجموعة."""
        qty = self.remaining_qty[carpet.id]

        # حساب عدد التكرارات الممكنة
        max_repetitions = self.max_width // carpet.width
        if max_repetitions <= 0:
            return False

        # توزيع الكمية بالتساوي
        base_qty = qty // max_repetitions
        if base_qty <= 0:
            return False

        used_qty = base_qty * max_repetitions
        total_width = carpet.width * max_repetitions

        if (self.min_width <= total_width <= self.max_width and
            used_qty <= qty and used_qty > 0):

            group_items = []
            for _ in range(max_repetitions):
                group_items.append(UsedItem(
                    rect_id=carpet.id,
                    width=carpet.width,
                    length=carpet.length,
                    used_qty=base_qty,
                    original_qty=self.original_qty[carpet.id]
                ))

            self._create_and_commit_group(group_items)
            self._update_quantities(group_items)
            return True

        return False

    def _is_valid_group(self, group_items: List[UsedItem]) -> bool:
        """التحقق من صحة المجموعة."""
        if not group_items:
            return False

        total_width = sum(item.width for item in group_items)
        return self.min_width <= total_width <= self.max_width

    def _create_and_commit_group(self, group_items: List[UsedItem]) -> None:
        """إنشاء وتسجيل المجموعة."""
        group = Group(id=self.group_id, items=group_items)
        self.groups.append(group)
        self.group_id += 1

    def _update_quantities(self, group_items: List[UsedItem]) -> None:
        """تحديث الكميات المستخدمة."""
        for item in group_items:
            self.remaining_qty[item.rect_id] -= item.used_qty
            if self.remaining_qty[item.rect_id] < 0:
                self.remaining_qty[item.rect_id] = 0

    def _process_remaining_items(self) -> None:
        """معالجة العناصر المتبقية مع التكرار الذكي."""
        # ترتيب العناصر المتبقية حسب العرض
        remaining_carpets = [
            Rectangle(r.id, r.width, r.length, self.remaining_qty[r.id])
            for r in self.carpets_sorted
            if self.remaining_qty[r.id] > 0
        ]

        remaining_carpets.sort(key=lambda r: (r.width, r.length, r.qty), reverse=True)

        for carpet in remaining_carpets:
            if self.remaining_qty[carpet.id] <= 0:
                continue

            # المرحلة 1: محاولة تكرار نفس العنصر
            if self._try_repetition_patterns(carpet):
                continue

            # المرحلة 2: محاولة إضافة العنصر كمجموعة وحيدة
            if self._try_single_item_group(carpet):
                continue

            # المرحلة 3: محاولة البحث المتقدم عن شركاء للعناصر الصعبة
            if self._try_advanced_partner_search(carpet):
                continue

    def _try_repetition_patterns(self, carpet: Rectangle) -> bool:
        """محاولة أنماط التكرار المختلفة للعنصر مع تكرار تدريجي."""
        qty = self.remaining_qty[carpet.id]

        # تجربة التكرار التدريجي (من 1 إلى الحد الأقصى)
        max_repetitions = self.max_width // carpet.width
        if max_repetitions <= 0:
            return False

        # توزيع الكمية بالتساوي على التكرارات
        for repetitions in range(max_repetitions, 0, -1):
            total_width = repetitions * carpet.width
            if total_width < self.min_width or total_width > self.max_width:
                continue

            base_qty = qty // repetitions
            if base_qty <= 0:
                continue

            used_qty = base_qty * repetitions
            if used_qty <= qty and used_qty > 0:
                return self._create_repeated_group(carpet, repetitions, base_qty)

        # تجربة تكرارات أقل لاستخدام كمية أكبر إذا لم تنجح التكرارات الكثيرة
        for repetitions in range(1, min(max_repetitions, 5)):
            total_width = repetitions * carpet.width
            if total_width >= self.min_width and total_width <= self.max_width:
                if qty >= repetitions:
                    return self._create_repeated_group(carpet, repetitions, repetitions)

        return False

    def _create_repeated_group(self, carpet: Rectangle, repetitions: int, qty_per_item: int) -> bool:
        """إنشاء مجموعة من تكرار العنصر."""
        group_items = []
        for _ in range(repetitions):
            group_items.append(UsedItem(
                rect_id=carpet.id,
                width=carpet.width,
                length=carpet.length,
                used_qty=qty_per_item,
                original_qty=self.original_qty[carpet.id]
            ))

        self._create_and_commit_group(group_items)
        self._update_quantities(group_items)
        return True

    def _try_single_item_group(self, carpet: Rectangle) -> bool:
        """محاولة إنشاء مجموعة من عنصر واحد."""
        if self.min_width <= carpet.width <= self.max_width:
            qty_to_use = min(self.remaining_qty[carpet.id], 1)
            if qty_to_use > 0:
                group_items = [UsedItem(
                    rect_id=carpet.id,
                    width=carpet.width,
                    length=carpet.length,
                    used_qty=qty_to_use,
                    original_qty=self.original_qty[carpet.id]
                )]

                self._create_and_commit_group(group_items)
                self._update_quantities(group_items)
                return True
        return False

    def _try_advanced_partner_search(self, carpet: Rectangle) -> bool:
        """محاولة البحث المتقدم عن شركاء للعناصر الصعبة التجميع."""
        qty = self.remaining_qty[carpet.id]

        # البحث عن جميع المجموعات الممكنة للعنصر الحالي
        all_possible_groups = self._find_all_possible_groups(carpet)

        # ترتيب المجموعات حسب الكفاءة
        all_possible_groups.sort(
            key=lambda group: self._calculate_group_efficiency(group),
            reverse=True
        )

        # تجربة أفضل المجموعات
        for group_items in all_possible_groups[:3]:  # تجربة أفضل 3 مجموعات فقط
            if self._is_valid_group(group_items):
                if self._check_quantities_available(group_items):
                    self._create_and_commit_group(group_items)
                    self._update_quantities(group_items)
                    return True

        return False

    def _final_repetition_optimization(self) -> None:
        """التحسين النهائي بتكرار العناصر لاستغلال الكميات المتبقية."""
        # محاولة تكرار كل عنصر متبقي بطرق مختلفة
        remaining_carpets = [
            Rectangle(r.id, r.width, r.length, self.remaining_qty[r.id])
            for r in self.carpets_sorted
            if self.remaining_qty[r.id] > 0
        ]

        for carpet in remaining_carpets:
            while self.remaining_qty[carpet.id] > 0:
                # المحاولة الأولى: تكرار لملء العرض
                if self._try_repetition_patterns(carpet):
                    continue

                # المحاولة الثانية: مجموعة وحيدة
                if self._try_single_item_group(carpet):
                    continue

                # إذا لم نتمكن من تشكيل أي مجموعة، ننتقل للعنصر التالي
                break

    def _get_final_remaining(self) -> List[Rectangle]:
        """الحصول على العناصر المتبقية النهائية."""
        remaining = []
        for carpet in self.carpets_sorted:
            qty = self.remaining_qty.get(carpet.id, 0)
            if qty > 0:
                remaining.append(Rectangle(carpet.id, carpet.width, carpet.length, qty))
        return remaining
