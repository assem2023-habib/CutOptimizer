
import pandas as pd
from typing import List, Dict, Optional
from models.data_models import Carpet, GroupCarpet

# استيراد الوحدات المنفصلة
from .excel_writer import write_output_excel as _write_output_excel
# استيراد دوال القراءة
from .excel_reader import (
    read_input_excel as _read_input_excel,
    validate_excel_data as _validate_excel_data,
    get_excel_summary as _get_excel_summary
)

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def read_input_excel(path: str, sheet_name: int = 0) -> List[Carpet]:
    """
    قراءة ملف Excel وتحويله إلى قائمة من كائنات Carpet.
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel
    sheet_name : int, optional
        رقم الورقة (افتراضي: 0)
        
    الإرجاع:
    -------
    List[Carpet]
        قائمة كائنات Carpet
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> print(f"تم قراءة {len(carpets)} نوع من السجاد")
    """
    return _read_input_excel(path, sheet_name)

def validate_excel_data(carpets: List[Carpet]) -> bool:
    """
    التحقق من صحة البيانات المقروءة من Excel.
    
    المعاملات:
    ----------
    carpets : List[Carpet]
        قائمة للتحقق منها
        
    الإرجاع:
    -------
    bool
        True إذا كانت البيانات صحيحة
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> if validate_excel_data(carpets):
    >>>     print("البيانات صحيحة")
    """
    return _validate_excel_data(carpets)


def get_excel_summary(carpets: List[Carpet]) -> dict:
    """
    ملخص إحصائي للبيانات المقروءة.
    
    المعاملات:
    ----------
    carpets : List[Carpet]
        قائمة كائنات Carpet
        
    الإرجاع:
    -------
    dict
        إحصائيات البيانات
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> summary = get_excel_summary(carpets)
    >>> print(f"إجمالي الكمية: {summary['total_quantity']}")
    """
    return _get_excel_summary(carpets)


def write_output_excel(
    path: str,
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None,
    originals: Optional[List[Carpet]] = None,
) -> None:
    """
    كتابة النتائج إلى ملف Excel.
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel الناتج
    groups : List[GroupCarpet]
        المجموعات الأصلية
    remaining : List[Carpet]
        العناصر المتبقية
    remainder_groups : Optional[List[GroupCarpet]]
        مجموعات البواقي
    min_width : Optional[int]
        الحد الأدنى للعرض
    max_width : Optional[int]
        الحد الأقصى للعرض
    originals : Optional[List[Carpet]]
        البيانات الأصلية للتدقيق
        
    أمثلة:
    -------
    >>> write_output_excel(
    >>>     "results.xlsx",
    >>>     groups=groups,
    >>>     remaining=remaining_carpets
    >>> )
    """
    from .excel_writer import write_output_excel as _write_output_excel
    _write_output_excel(
        path, groups, remaining, min_width, max_width,tolerance_length , originals
    )