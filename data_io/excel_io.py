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
from models.data_models import Rectangle, Group, UsedItem
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
    process_remainder_complete,
    generate_size_suggestions,
    analyze_remaining_for_optimization
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
