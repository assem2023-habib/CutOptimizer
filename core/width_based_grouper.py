"""
مجمع السجاد بناءً على العرض - Width Based Grouper
===============================================

هذا الملف يطبق خوارزمية لتجميع السجاد بناءً على العرض مع إعطاء أولوية للأعرض.
الخوارزمية ترتب العناصر حسب العرض تنازلياً وتشكل مجموعات محسنة للعرض المحدد.

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


class WidthBasedGrouper:
    """
    مجمع السجاد بناءً على العرض مع أولوية للأعرض.

    هذه الفئة تركز على:
    - ترتيب العناصر حسب العرض تنازلياً (الأولوية للأعرض)
    - تشكيل مجموعات محسنة للعرض المحدد
    - استغلال أقصى للكميات المتاحة
    - تقديم إحصائيات مفصلة
    """

    def __init__(self,
                 min_width: int,
                 max_width: int,
                 tolerance_length: int = 10,
                 start_group_id: int = 1):
        """
        تهيئة المجمع بناءً على العرض.

        المعاملات:
        -----------
        min_width : int
            الحد الأدنى للعرض المسموح
        max_width : int
            الحد الأقصى للعرض المسموح
        tolerance_length : int
            حدود السماحية للطول (افتراضي: 10)
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

        # إحصائيات
        self.stats: Dict = {}
        # تتبع الكميات المستخدمة لكل عنصر
        self.used_qty_tracker: Dict[int, int] = {}

    def group_carpets(self, carpets: List[Rectangle]) -> Tuple[List[Group], List[Rectangle], Dict]:
        """
        الدالة الرئيسية للتجميع بناءً على العرض.

        المعاملات:
        -----------
        carpets : List[Rectangle]
            قائمة السجاد المراد تجميعه

        الإرجاع:
        --------
        Tuple[List[Group], List[Rectangle], Dict]
            (المجموعات المُشكّلة، العناصر المتبقية، الإحصائيات)
        """
        # تهيئة البيانات
        self._initialize_data(carpets)

        # ترتيب العناصر حسب العرض تنازلياً (أولوية للأعرض)
        self._sort_carpets_by_width()

        # تشكيل المجموعات بالأولوية للأعرض
        self._form_width_optimized_groups()

        # معالجة العناصر المتبقية
        self._process_remaining_items()

        # حساب الإحصائيات
        self._calculate_statistics()

        return self.groups, self._get_final_remaining(), self.stats

    def _initialize_data(self, carpets: List[Rectangle]) -> None:
        """تهيئة البيانات الأولية."""
        self.carpets = copy.deepcopy(carpets)
        self.remaining_qty = {r.id: r.qty for r in self.carpets}
        self.original_qty = {r.id: r.qty for r in self.carpets}
        self.used_qty_tracker = {r.id: 0 for r in self.carpets}
        self.groups = []
        self.group_id = self.start_group_id
        self.stats = {}

    def _sort_carpets_by_width(self) -> None:
        """ترتيب العناصر حسب العرض تنازلياً مع مراعاة الطول والكمية."""
        def sort_key(carpet):
            # المفتاح: عرض تنازلي، ثم طول تنازلي، ثم كمية تنازلي
            return (-carpet.width, -carpet.length, -carpet.qty)

        self.carpets_sorted = sorted(self.carpets, key=sort_key)

    def _form_width_optimized_groups(self) -> None:
        """تشكيل المجموعات بالأولوية للأعرض."""
        processed_items = set()

        # المرحلة الأولى: تشكيل مجموعات من العناصر الأكبر عرضاً
        for carpet in self.carpets_sorted:
            if carpet.id in processed_items or self.remaining_qty[carpet.id] <= 0:
                continue

            # محاولة تشكيل مجموعة مع هذا العنصر كأساس
            if self._try_form_group_with_primary(carpet):
                processed_items.add(carpet.id)

    def _try_form_group_with_primary(self, primary: Rectangle) -> bool:
        """محاولة تشكيل مجموعة مع العنصر الأساسي."""
        primary_qty = self.remaining_qty[primary.id]

        # تجربة كميات مختلفة من العنصر الأساسي
        for use_qty in range(primary_qty, 0, -1):
            if self._try_form_group_with_quantity(primary, use_qty):
                return True

        return False

    def _try_form_group_with_quantity(self, primary: Rectangle, use_qty: int) -> bool:
        """محاولة تشكيل مجموعة بكمية محددة من العنصر الأساسي."""
        ref_length = primary.length * use_qty
        current_width = primary.width
        remaining_width = self.max_width - current_width

        # إنشاء عنصر المجموعة الأساسي
        group_items = [UsedItem(
            rect_id=primary.id,
            width=primary.width,
            length=primary.length,
            used_qty=use_qty,
            original_qty=self.original_qty[primary.id]
        )]

        # البحث عن شركاء لملء العرض المتبقي
        if self._find_compatible_partners(group_items, current_width, ref_length, remaining_width):
            # التحقق من صحة المجموعة وإضافتها
            if self._is_valid_group(group_items):
                self._create_and_commit_group(group_items)
                self._update_quantities(group_items)
                return True

        # إذا لم نتمكن من إضافة شركاء، جرب تكرار العنصر الأساسي
        if self._try_repeat_primary_for_width(group_items, ref_length):
            if self._is_valid_group(group_items):
                self._create_and_commit_group(group_items)
                self._update_quantities(group_items)
                return True

        return False

    def _find_compatible_partners(self, group_items: List[UsedItem], current_width: int, ref_length: int, remaining_width: int) -> bool:
        """البحث عن شركاء متوافقين لملء العرض المتبقي."""
        if remaining_width < 30:  # لا يوجد مساحة كافية للشركاء
            return True

        # ترتيب العناصر المرشحة حسب العرض تنازلياً
        candidates = [
            r for r in self.carpets_sorted
            if (r.id != group_items[0].rect_id and  # تجنب العنصر الأساسي
                self.remaining_qty[r.id] > 0 and
                r.width <= remaining_width and
                r.width >= 30)  # تجنب العناصر الصغيرة جداً
        ]

        # ترتيب المرشحين حسب العرض تنازلياً (أولوية للأعرض)
        candidates.sort(key=lambda r: (-r.width, -r.length, -r.qty))

        # تجربة إضافة الشركاء
        for candidate in candidates:
            if current_width + candidate.width > self.max_width:
                continue

            # حساب الكمية المثالية للمرشح
            ideal_qty = ref_length // candidate.length if candidate.length > 0 else 1
            use_qty = min(ideal_qty, self.remaining_qty[candidate.id])

            if use_qty <= 0:
                continue

            # التحقق من توفر الكمية المطلوبة
            if self.remaining_qty[candidate.id] < use_qty:
                continue

            # التحقق من السماحية في الطول
            total_length = candidate.length * use_qty
            if abs(total_length - ref_length) <= self.tolerance_length:
                # إضافة المرشح للمجموعة
                group_items.append(UsedItem(
                    rect_id=candidate.id,
                    width=candidate.width,
                    length=candidate.length,
                    used_qty=use_qty,
                    original_qty=self.original_qty[candidate.id]
                ))

                current_width += candidate.width
                remaining_width = self.max_width - current_width

                # إذا امتلأ العرض، توقف
                if remaining_width < 30:
                    return True

        return True  # تم العثور على حل مقبول حتى بدون شركاء

    def _try_repeat_primary_for_width(self, group_items: List[UsedItem], ref_length: int) -> bool:
        """محاولة تكرار العنصر الأساسي لملء العرض."""
        primary = group_items[0]
        current_width = sum(item.width for item in group_items)
        available_qty = self.remaining_qty[primary.rect_id]

        # حساب عدد التكرارات الممكنة
        max_repetitions = (self.max_width - current_width) // primary.width

        if max_repetitions <= 0:
            return False

        # إضافة تكرارات العنصر الأساسي
        for _ in range(max_repetitions):
            if (current_width + primary.width > self.max_width or
                available_qty < primary.used_qty or
                self.remaining_qty[primary.rect_id] < primary.used_qty):
                break

            group_items.append(UsedItem(
                rect_id=primary.rect_id,
                width=primary.width,
                length=primary.length,
                used_qty=primary.used_qty,
                original_qty=primary.original_qty
            ))

            current_width += primary.width
            available_qty -= primary.used_qty

            # إذا وصلنا للحد الأدنى، توقف
            if current_width >= self.min_width:
                break

        return current_width >= self.min_width

    def _process_remaining_items(self) -> None:
        """معالجة العناصر المتبقية بعد المرحلة الأولى."""
        remaining_carpets = [
            Rectangle(r.id, r.width, r.length, self.remaining_qty[r.id])
            for r in self.carpets_sorted
            if self.remaining_qty[r.id] > 0
        ]

        # ترتيب المتبقي حسب العرض تنازلياً
        remaining_carpets.sort(key=lambda r: (-r.width, -r.length, -r.qty))

        for carpet in remaining_carpets:
            if self.remaining_qty[carpet.id] <= 0:
                continue

            # محاولة تشكيل مجموعات من العنصر الواحد إذا كان يتناسب مع النطاق
            if self._try_single_item_group(carpet):
                continue

            # محاولة تكرار العنصر لملء العرض
            if self._try_repetition_group(carpet):
                continue

    def _try_single_item_group(self, carpet: Rectangle) -> bool:
        """محاولة تشكيل مجموعة من عنصر واحد."""
        if self.min_width <= carpet.width <= self.max_width:
            use_qty = min(self.remaining_qty[carpet.id], 1)
            if use_qty > 0 and self.remaining_qty[carpet.id] >= use_qty:
                group_items = [UsedItem(
                    rect_id=carpet.id,
                    width=carpet.width,
                    length=carpet.length,
                    used_qty=use_qty,
                    original_qty=self.original_qty[carpet.id]
                )]

                self._create_and_commit_group(group_items)
                self._update_quantities(group_items)
                return True
        return False

    def _try_repetition_group(self, carpet: Rectangle) -> bool:
        """محاولة تشكيل مجموعة من تكرار العنصر."""
        qty = self.remaining_qty[carpet.id]

        # حساب عدد التكرارات الممكنة
        max_repetitions = self.max_width // carpet.width
        if max_repetitions <= 1:
            return False

        # تجربة تكرارات مختلفة
        for repetitions in range(max_repetitions, 1, -1):
            total_width = repetitions * carpet.width
            if total_width < self.min_width or total_width > self.max_width:
                continue

            # توزيع الكمية بالتساوي
            qty_per_repetition = qty // repetitions
            if qty_per_repetition <= 0:
                continue

            used_qty = qty_per_repetition * repetitions
            if used_qty > qty or self.remaining_qty[carpet.id] < used_qty:
                continue

            # إنشاء المجموعة
            group_items = []
            for _ in range(repetitions):
                group_items.append(UsedItem(
                    rect_id=carpet.id,
                    width=carpet.width,
                    length=carpet.length,
                    used_qty=qty_per_repetition,
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
            self.used_qty_tracker[item.rect_id] += item.used_qty
            if self.remaining_qty[item.rect_id] < 0:
                self.remaining_qty[item.rect_id] = 0

    def _get_final_remaining(self) -> List[Rectangle]:
        """الحصول على العناصر المتبقية النهائية."""
        remaining = []
        for carpet in self.carpets_sorted:
            qty = self.remaining_qty.get(carpet.id, 0)
            if qty > 0:
                remaining.append(Rectangle(carpet.id, carpet.width, carpet.length, qty))
        return remaining

    def _calculate_statistics(self) -> None:
        """حساب الإحصائيات التفصيلية."""
        total_original_qty = sum(self.original_qty.values())
        total_used_qty = sum(self.used_qty_tracker.values())
        total_remaining_qty = sum(self.remaining_qty.values())

        # إحصائيات المجموعات
        group_widths = [group.total_width() for group in self.groups]
        group_areas = [group.total_area() for group in self.groups]
        group_quantities = [group.total_used_qty() for group in self.groups]

        # إحصائيات العناصر حسب العرض
        width_distribution = defaultdict(int)
        for carpet in self.carpets:
            width_category = self._get_width_category(carpet.width)
            width_distribution[width_category] += carpet.qty

        # إحصائيات كل عنصر على حدة
        per_item_stats = {}
        for carpet in self.carpets:
            used_qty = self.used_qty_tracker[carpet.id]
            remaining_qty = self.remaining_qty.get(carpet.id, 0)

            per_item_stats[carpet.id] = {
                'width': carpet.width,
                'length': carpet.length,
                'original_qty': self.original_qty[carpet.id],
                'used_qty': used_qty,
                'remaining_qty': remaining_qty,
                'utilization_percentage': (used_qty / self.original_qty[carpet.id] * 100) if self.original_qty[carpet.id] > 0 else 0
            }

        self.stats = {
            'total_original_quantity': total_original_qty,
            'total_used_quantity': total_used_qty,
            'total_remaining_quantity': total_remaining_qty,
            'utilization_percentage': (total_used_qty / total_original_qty * 100) if total_original_qty > 0 else 0,
            'total_groups': len(self.groups),
            'average_group_width': sum(group_widths) / len(group_widths) if group_widths else 0,
            'min_group_width': min(group_widths) if group_widths else 0,
            'max_group_width': max(group_widths) if group_widths else 0,
            'total_group_area': sum(group_areas),
            'average_group_quantity': sum(group_quantities) / len(group_quantities) if group_quantities else 0,
            'width_distribution': dict(width_distribution),
            'remaining_items': len([r for r in self.carpets if self.remaining_qty.get(r.id, 0) > 0]),
            'per_item_stats': per_item_stats
        }

    def _get_width_category(self, width: int) -> str:
        """تصنيف العرض إلى فئات."""
        if width >= 200:
            return "كبير جداً (≥200)"
        elif width >= 150:
            return "كبير (150-199)"
        elif width >= 100:
            return "متوسط (100-149)"
        elif width >= 50:
            return "صغير (50-99)"
        else:
            return "صغير جداً (<50)"

    def print_detailed_report(self) -> None:
        """طباعة تقرير مفصل بالنتائج والإحصائيات."""
        print("\n" + "="*70)
        print("📊 تقرير التجميع بناءً على العرض")
        print("="*70)

        # معلومات المجموعات
        print(f"\n📋 المجموعات المُشكلة: {self.stats['total_groups']}")
        print(f"📏 متوسط عرض المجموعة: {self.stats['average_group_width']:.1f}")
        print(f"📏 أقل عرض مجموعة: {self.stats['min_group_width']}")
        print(f"📏 أكبر عرض مجموعة: {self.stats['max_group_width']}")

        # معلومات الاستغلال
        print(f"\n📦 إجمالي الكمية الأصلية: {self.stats['total_original_quantity']}")
        print(f"✅ إجمالي الكمية المستخدمة: {self.stats['total_used_quantity']}")
        print(f"📦 إجمالي الكمية المتبقية: {self.stats['total_remaining_quantity']}")
        print(f"📈 نسبة الاستغلال: {self.stats['utilization_percentage']:.1f}%")

        # توزيع العروض
        print(f"\n📊 توزيع العناصر حسب العرض:")
        for category, qty in self.stats['width_distribution'].items():
            print(f"  {category}: {qty} عنصر")

        # إحصائيات كل عنصر على حدة
        print(f"\n📋 إحصائيات كل عنصر:")
        print(f"{'─'*80}")
        print(f"{'العنصر':<8} {'العرض':<8} {'الطول':<8} {'الأصلية':<10} {'المستخدمة':<12} {'المتبقية':<10} {'الاستغلال':<10}")
        print(f"{'─'*80}")

        for item_id, stats in sorted(self.stats['per_item_stats'].items()):
            print(f"{item_id:<8} {stats['width']:<8} {stats['length']:<8} {stats['original_qty']:<10} {stats['used_qty']:<12} {stats['remaining_qty']:<10} {stats['utilization_percentage']:<10.1f}%")

        print(f"{'─'*80}")
        print(f"{'المجموع':<8} {'':<8} {'':<8} {self.stats['total_original_quantity']:<10} {self.stats['total_used_quantity']:<12} {self.stats['total_remaining_quantity']:<10} {self.stats['utilization_percentage']:<9.1f}%")

        # عرض المجموعات بالتفصيل
        if self.groups:
            print(f"\n📋 تفاصيل المجموعات:")
            for group in self.groups:
                print(f"\n  مجموعة {group.id}: عرض إجمالي = {group.total_width()}")
                print(f"    المساحة الإجمالية: {group.total_area()}")
                print(f"    الكمية المستخدمة: {group.total_used_qty()}")

                # تفاصيل العناصر في المجموعة
                unique_items = {}
                for item in group.items:
                    if item.rect_id not in unique_items:
                        unique_items[item.rect_id] = {'count': 0, 'qty': 0, 'width': item.width, 'length': item.length}
                    unique_items[item.rect_id]['count'] += 1
                    unique_items[item.rect_id]['qty'] += item.used_qty

                for rect_id, info in unique_items.items():
                    print(f"    - العنصر {rect_id}: عرض={info['width']}, طول={info['length']}")
                    print(f"      التكرار: {info['count']} مرة, الكمية: {info['qty']}")

        # العناصر المتبقية
        remaining = self._get_final_remaining()
        if remaining:
            print(f"\n📦 العناصر المتبقية ({len(remaining)}):")
            for rem in remaining:
                print(f"  - العنصر {rem.id}: عرض={rem.width}, طول={rem.length}, كمية={rem.qty}")
        else:
            print(f"\n✅ لا توجد عناصر متبقية!")

        print(f"\n{'='*70}")


def test_width_based_grouper():
    """اختبار المجمع الجديد بناءً على العرض."""
    print("=== اختبار المجمع بناءً على العرض ===\n")

    # البيانات التجريبية
    test_data = [
        (210, 248, 1332),  # عرض 210, طول 248, عدد 1332
        (160, 230, 712),   # عرض 160, طول 230, عدد 712
        (145, 208, 2004),  # عرض 145, طول 208, عدد 2004
        (120, 170, 646),   # عرض 120, طول 170, عدد 646
        (105, 148, 4668),  # عرض 105, طول 148, عدد 4668
        (53, 98, 3336),    # عرض 53, طول 98, عدد 3336
        (42, 68, 6672),    # عرض 42, طول 68, عدد 6672
    ]

    # تحويل البيانات إلى قائمة Rectangle
    carpets = []
    for i, (width, length, qty) in enumerate(test_data, 1):
        carpets.append(Rectangle(id=i, width=width, length=length, qty=qty))

    print("📊 البيانات المستخدمة في الاختبار:")
    total_qty = 0
    for carpet in carpets:
        print(f"  العنصر {carpet.id}: عرض={carpet.width}, طول={carpet.length}, كمية={carpet.qty}")
        total_qty += carpet.qty
    print(f"\nإجمالي الكمية: {total_qty}\n")

    # نطاق العرض المناسب للبيانات
    min_width = 370
    max_width = 400

    print(f"🔧 نطاق العرض: {min_width} - {max_width}")
    print(f"📏 سماحية الطول: 10\n")

    # إنشاء المجمع وتشغيل الخوارزمية
    grouper = WidthBasedGrouper(
        min_width=min_width,
        max_width=max_width,
        tolerance_length=10,
        start_group_id=1
    )

    groups, remaining, stats = grouper.group_carpets(carpets)

    # طباعة التقرير المفصل
    grouper.print_detailed_report()

    # التحقق من الصحة
    print(f"\n✅ التحقق من الصحة:")
    print(f"  ✓ إجمالي المجموعات: {len(groups)}")

    # التحقق من أن جميع المجموعات ضمن النطاق
    valid_groups = 0
    for group in groups:
        if min_width <= group.total_width() <= max_width:
            valid_groups += 1
        else:
            print(f"  ❌ مجموعة {group.id} خارج النطاق: {group.total_width()}")

    print(f"  ✓ المجموعات الصحيحة: {valid_groups}/{len(groups)}")

    # التحقق من إجمالي الكميات
    if stats['total_used_quantity'] + stats['total_remaining_quantity'] == stats['total_original_quantity']:
        print(f"  ✓ إجمالي الكميات صحيح")
    else:
        print(f"  ❌ خطأ في الكميات: {stats['total_used_quantity']} + {stats['total_remaining_quantity']} ≠ {stats['total_original_quantity']}")

    # التحقق من إحصائيات كل عنصر
    print(f"\n🔍 التحقق من إحصائيات كل عنصر:")
    all_correct = True
    for item_id, item_stats in stats['per_item_stats'].items():
        calculated_remaining = item_stats['original_qty'] - item_stats['used_qty']
        if calculated_remaining == item_stats['remaining_qty']:
            print(f"  ✓ العنصر {item_id}: صحيح ({item_stats['used_qty']}/{item_stats['original_qty']})")
        else:
            print(f"  ❌ العنصر {item_id}: خطأ في الحساب ({calculated_remaining} ≠ {item_stats['remaining_qty']})")
            all_correct = False

    if all_correct:
        print(f"  ✓ جميع إحصائيات العناصر صحيحة")
    else:
        print(f"  ❌ توجد أخطاء في إحصائيات بعض العناصر")
    return groups, remaining, stats


if __name__ == "__main__":
    try:
        test_width_based_grouper()

        print(f"\n{'='*60}")
        print("✅ تم إنجاز الاختبار المطلوب بنجاح!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
