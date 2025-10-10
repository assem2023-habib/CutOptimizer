"""
الوحدة الرئيسية لمعالجة ملفات Excel
===================================

هذه الوحدة تحتوي على الدوال الرئيسية لقراءة وكتابة ملفات Excel
وتنسيق البيانات للاستخدام في نظام تحسين القطع.

المؤلف: نظام تحسين القطع
التاريخ: 2024
الإصدار: 2.0
"""

# =============================================================================
# IMPORTS
# =============================================================================

import copy
import pandas as pd
from typing import List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
import os
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name
from collections import defaultdict
import math
import random

# استيراد الوحدات المنفصلة
from .excel_reader import read_input_excel, validate_excel_data, get_excel_summary
from .excel_writer import write_output_excel
from .remainder_optimizer import (
    create_enhanced_remainder_groups,
    create_enhanced_remainder_groups_from_rectangles,
    exhaustively_regroup,
    calculate_group_efficiency,
    optimize_group_formation
)
from .suggestion_generator import (
    generate_partner_suggestions,
    analyze_remaining_items,
    get_optimization_recommendations
)


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def read_input_excel(path: str, sheet_name: int = 0) -> List[Rectangle]:
    """
    قراءة ملف Excel وتحويله إلى قائمة من كائنات Rectangle.
    
    هذه الدالة تقرأ ملف Excel يحتوي على بيانات السجاد في الأعمدة الثلاثة الأولى:
    - العمود الأول: العرض
    - العمود الثاني: الطول  
    - العمود الثالث: الكمية
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel المراد قراءته
    sheet_name : int, optional
        رقم الورقة المراد قراءتها (افتراضي: 0)
        
    الإرجاع:
    -------
    List[Rectangle]
        قائمة من كائنات Rectangle تمثل السجاد الموجود في الملف
        
    الاستثناءات:
    ------------
    Exception
        في حالة فشل قراءة الملف أو تلف البيانات
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> print(f"تم قراءة {len(carpets)} نوع من السجاد")
    """
    from .excel_reader import read_input_excel as _read_input_excel
    return _read_input_excel(path, sheet_name)


def write_output_excel(
    path: str,
    groups: List[Group],
    remaining: List[Rectangle],
    remainder_groups: Optional[List[Group]] = None,
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None,
    originals: Optional[List[Rectangle]] = None,
    enhanced_remainder_groups: Optional[List[Group]] = None
) -> None:
    """
    كتابة النتائج إلى ملف Excel مع تقارير مفصلة.
    
    هذه الدالة تنشئ ملف Excel يحتوي على عدة أوراق:
    - تفاصيل المجموعات: تفاصيل كل مجموعة مع تصنيفها
    - ملخص المجموعات: إحصائيات شاملة للمجموعات
    - السجاد المتبقي: العناصر التي لم يتم استخدامها
    - ملخص الواجهة: ملخص مبسط للعرض
    - الإجماليات: مقارنة قبل وبعد العملية
    - اقتراحات تشكيل مجموعات: اقتراحات لتجميع البواقي
    - إحصائيات المجموعات الإضافية: إحصائيات المجموعات المحسنة
    - تدقيق الكميات: فحص دقيق للكميات
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel المراد كتابته
    groups : List[Group]
        المجموعات الأصلية
    remaining : List[Rectangle]
        العناصر المتبقية
    remainder_groups : Optional[List[Group]]
        مجموعات البواقي العادية
    min_width : Optional[int]
        الحد الأدنى للعرض
    max_width : Optional[int]
        الحد الأقصى للعرض
    tolerance_length : Optional[int]
        حدود السماحية للطول
    originals : Optional[List[Rectangle]]
        العناصر الأصلية للتدقيق
    enhanced_remainder_groups : Optional[List[Group]]
        المجموعات الإضافية المحسنة من البواقي
        
    أمثلة:
    -------
    >>> write_output_excel(
    >>>     "results.xlsx",
    >>>     groups=original_groups,
    >>>     remaining=remaining_items,
    >>>     enhanced_remainder_groups=enhanced_groups
    >>> )
    """
    from .excel_writer import write_output_excel as _write_output_excel
    _write_output_excel(
        path, groups, remaining, remainder_groups, min_width, max_width,
        tolerance_length, originals, enhanced_remainder_groups
    )


# =============================================================================
# REMAINDER OPTIMIZATION FUNCTIONS
# =============================================================================

def create_enhanced_remainder_groups(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية محسنة لتشكيل مجموعات إضافية من البواقي مع إمكانية تكرار العناصر.
    
    هذه الدالة تستخدم خوارزمية ذكية لتجميع البواقي مع:
    - إمكانية تكرار العناصر في نفس المجموعة
    - البحث عن أفضل التوليفات الممكنة
    - مراعاة جميع الشروط المطلوبة
    - تحسين الأداء لتجنب التعقيد المفرط
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية المراد تجميعها
    min_width : int
        الحد الأدنى للعرض المطلوب
    max_width : int
        الحد الأقصى للعرض المسموح
    tolerance_length : int
        حدود السماحية للفرق في الطول
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
    max_rounds : int, optional
        الحد الأقصى لعدد المحاولات (افتراضي: 50)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة المشكلة
        - قائمة العناصر المتبقية بعد التجميع
        
    أمثلة:
    -------
    >>> enhanced_groups, final_remaining = create_enhanced_remainder_groups(
    >>>     remaining_items, 370, 400, 100
    >>> )
    >>> print(f"تم تشكيل {len(enhanced_groups)} مجموعة إضافية")
    """
    from .remainder_optimizer import create_enhanced_remainder_groups as _create_enhanced_remainder_groups
    return _create_enhanced_remainder_groups(
        remaining, min_width, max_width, tolerance_length, start_group_id, max_rounds
    )


def create_enhanced_remainder_groups_from_rectangles(
    remaining_rectangles: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000
) -> Tuple[List[Group], List[Rectangle]]:
    """
    دالة مساعدة لإنشاء مجموعات إضافية محسنة من قائمة Rectangle.
    
    هذه الدالة توفر واجهة سهلة الاستخدام لإنشاء مجموعات إضافية
    من البواقي مع إمكانية تكرار العناصر.
    
    المعاملات:
    ----------
    remaining_rectangles : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض  
    tolerance_length : int
        حدود السماحية للطول
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة
        - قائمة العناصر المتبقية بعد التجميع
        
    أمثلة:
    -------
    >>> enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
    >>>     remaining_items, 370, 400, 100
    >>> )
    """
    from .remainder_optimizer import create_enhanced_remainder_groups_from_rectangles as _create_enhanced_remainder_groups_from_rectangles
    return _create_enhanced_remainder_groups_from_rectangles(
        remaining_rectangles, min_width, max_width, tolerance_length, start_group_id
    )


def exhaustively_regroup(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_group_id: int = 10000,
    max_rounds: int = 50
) -> Tuple[List[Group], List[Rectangle]]:
    """
    استدعاء متكرر لخوارزمية إعادة تجميع البواقي حتى لا يتبقى شيء قابل للتجميع.
    
    هذه الدالة تستخدم الخوارزمية المحسنة مع إمكانية تكرار العناصر
    لتجميع أقصى قدر ممكن من البواقي.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
    start_group_id : int, optional
        رقم المجموعة الأولى (افتراضي: 10000)
    max_rounds : int, optional
        الحد الأقصى لعدد المحاولات (افتراضي: 50)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات الجديدة
        - قائمة العناصر المتبقية بعد التجميع
    """
    from .remainder_optimizer import exhaustively_regroup as _exhaustively_regroup
    return _exhaustively_regroup(
        remaining, min_width, max_width, tolerance_length, start_group_id, max_rounds
    )


# =============================================================================
# SUGGESTION FUNCTIONS
# =============================================================================

def generate_partner_suggestions(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[Dict]:
    """
    توليد اقتراحات ذكية لتشكيل مجموعات من البواقي.
    
    هذه الدالة تقترح أفضل التوليفات الممكنة لكل عنصر أساسي
    مع مراعاة الشروط المطلوبة والكميات المتاحة.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض المطلوب
    max_width : int
        الحد الأقصى للعرض المسموح
    tolerance_length : int
        حدود السماحية للفرق في الطول
        
    الإرجاع:
    -------
    List[Dict]
        قائمة من القواميس تحتوي على الاقتراحات
        
    أمثلة:
    -------
    >>> suggestions = generate_partner_suggestions(remaining_items, 370, 400, 100)
    >>> for suggestion in suggestions:
    >>>     print(f"العنصر {suggestion['معرف الأساسي']}: {suggestion['توصية مختصرة']}")
    """
    from .suggestion_generator import generate_partner_suggestions as _generate_partner_suggestions
    return _generate_partner_suggestions(remaining, min_width, max_width, tolerance_length)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_excel_data(carpets: List[Rectangle]) -> bool:
    """
    التحقق من صحة البيانات المقروءة من ملف Excel.
    
    المعاملات:
    ----------
    carpets : List[Rectangle]
        قائمة كائنات Rectangle للتحقق منها
        
    الإرجاع:
    -------
    bool
        True إذا كانت البيانات صحيحة، False إذا كانت هناك مشاكل
    """
    from .excel_reader import validate_excel_data as _validate_excel_data
    return _validate_excel_data(carpets)


def get_excel_summary(carpets: List[Rectangle]) -> dict:
    """
    الحصول على ملخص إحصائي للبيانات المقروءة من ملف Excel.
    
    المعاملات:
    ----------
    carpets : List[Rectangle]
        قائمة كائنات Rectangle
        
    الإرجاع:
    -------
    dict
        قاموس يحتوي على الإحصائيات
    """
    from .excel_reader import get_excel_summary as _get_excel_summary
    return _get_excel_summary(carpets)


def analyze_remaining_items(remaining: List[Rectangle]) -> Dict[str, any]:
    """
    تحليل العناصر المتبقية وإعطاء إحصائيات مفيدة.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
        
    الإرجاع:
    -------
    Dict[str, any]
        قاموس يحتوي على الإحصائيات
    """
    from .suggestion_generator import analyze_remaining_items as _analyze_remaining_items
    return _analyze_remaining_items(remaining)


def get_optimization_recommendations(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[str]:
    """
    الحصول على توصيات لتحسين تشكيل المجموعات.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
        
    الإرجاع:
    -------
    List[str]
        قائمة من التوصيات النصية
    """
    from .suggestion_generator import get_optimization_recommendations as _get_optimization_recommendations
    return _get_optimization_recommendations(remaining, min_width, max_width, tolerance_length)


def calculate_group_efficiency(group: Group) -> Dict[str, float]:
    """
    حساب كفاءة المجموعة بناءً على عدة معايير.
    
    المعاملات:
    ----------
    group : Group
        المجموعة المراد حساب كفاءتها
        
    الإرجاع:
    -------
    Dict[str, float]
        قاموس يحتوي على معايير الكفاءة
    """
    from .remainder_optimizer import calculate_group_efficiency as _calculate_group_efficiency
    return _calculate_group_efficiency(group)

    # tolerance_length: int,
    # start_group_id: int = 10000
def optimize_group_formation(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    max_groups: int = 100
) -> Tuple[List[Group], List[Rectangle]]:
    """
    تحسين تشكيل المجموعات باستخدام خوارزمية متقدمة.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
    max_groups : int, optional
        الحد الأقصى لعدد المجموعات (افتراضي: 100)
        
    الإرجاع:
    -------
    Tuple[List[Group], List[Rectangle]]
        - قائمة المجموعات المحسنة
        - قائمة العناصر المتبقية
    """
    from .remainder_optimizer import optimize_group_formation as _optimize_group_formation
    return _optimize_group_formation(remaining, min_width, max_width, tolerance_length, max_groups)


# =============================================================================
# LEGACY FUNCTIONS (for backward compatibility)
# =============================================================================

def regroup_residuals_advanced(
    residuals: List[Dict],
    min_width: int,
    max_width: int,
    tolerance: int,
    max_depth: int = 6
) -> Tuple[List[Dict], List[Dict]]:
    """
    خوارزمية متقدمة لإعادة تجميع البواقي (للتوافق مع الإصدارات السابقة).
    
    تحذير: هذه الدالة محتفظ بها للتوافق مع الإصدارات السابقة فقط.
    يُنصح باستخدام create_enhanced_remainder_groups بدلاً منها.
    """
    # تحويل من dict إلى Rectangle
    rectangles = []
    for r in residuals:
        rectangles.append(Rectangle(
            id=r['id'],
            width=r['width'],
            length=r['length'],
            qty=r.get('remaining', r.get('qty', 0))
        ))
    
    # استخدام الخوارزمية الجديدة
    groups, final_remaining = create_enhanced_remainder_groups(
        rectangles, min_width, max_width, tolerance
    )
    
    # تحويل النتائج إلى الشكل المطلوب
    result_groups = []
    for g in groups:
        group_dict = {
            'items': [
                {
                    'id': it.rect_id,
                    'width': it.width,
                    'length': it.length,
                    'used': it.used_qty
                }
                for it in g.items
            ],
            'total_width': g.total_width(),
            'ref_length': g.ref_length(),
            'count_types': len(g.items)
        }
        result_groups.append(group_dict)
    
    # تحويل البواقي إلى الشكل المطلوب
    result_remaining = []
    for r in final_remaining:
        result_remaining.append({
            'id': r.id,
            'width': r.width,
            'length': r.length,
            'remaining': r.qty
        })
    
    return result_groups, result_remaining