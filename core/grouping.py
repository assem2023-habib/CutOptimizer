from .greedy_grouper import GreedyGrouper
from .optimized_grouping import group_carpets_optimized, combine_similar_groups, regroup_residuals

from typing import List, Tuple
from .models import Rectangle, Group

# دالة مساعدة للحفاظ على التوافق مع الكود الموجود
def group_carpets_greedy(carpets: List[Rectangle],
                         min_width: int,
                         max_width: int,
                         tolerance_length: int,
                         start_with_largest: bool = True,
                         allow_split_rows: bool = True,
                         start_group_id: int = 1
                         ) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة التوافق - تستخدم الفئة الجديدة GreedyGrouper.

    هذه الدالة محفوظة للحفاظ على التوافق مع الكود الموجود.
    يُفضل استخدام GreedyGrouper مباشرة في الكود الجديد.
    """
    grouper = GreedyGrouper(min_width, max_width, tolerance_length,
                           start_with_largest, allow_split_rows, start_group_id)
    return grouper.group_carpets(carpets)

# دوال wrapper لاستدعاء التوابع المحسنة من الملف الجديد
def group_carpets_advanced(
    carpets: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_with_largest: bool = True,
    beam_width: int = 5,
    max_combo_types: int = 4,
    time_budget_sec: float = None,
    start_group_id: int = 1
) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة wrapper للخوارزمية المحسنة group_carpets_optimized.

    تستخدم خوارزمية متقدمة مع beam search للحصول على نتائج أفضل.
    مناسبة للحالات التي تحتاج دقة أعلى في التجميع.
    """
    return group_carpets_optimized(
        carpets, min_width, max_width, tolerance_length,
        start_with_largest, beam_width, max_combo_types,
        time_budget_sec, start_group_id
    )

def merge_similar_groups(groups: List[Group], min_width: int, max_width: int, tolerance: int) -> List[Group]:
    """
    دالة wrapper لدمج المجموعات المتشابهة combine_similar_groups.

    تقوم بدمج المجموعات التي تحتوي على نفس أنواع العناصر
    لتحسين الكفاءة وتقليل العدد الإجمالي للمجموعات.
    """
    return combine_similar_groups(groups, min_width, max_width, tolerance)

def regroup_remainders(residuals, min_width: int, max_width: int, tolerance: int):
    """
    دالة wrapper لإعادة تجميع البواقي regroup_residuals.

    تقوم بإعادة ترتيب وتجميع العناصر المتبقية لتكوين مجموعات جديدة
    فعالة من البواقي غير المستخدمة.
    """
    return regroup_residuals(residuals, min_width, max_width, tolerance)
