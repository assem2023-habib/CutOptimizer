"""
وحدة قراءة ملفات Excel
=====================

هذه الوحدة تحتوي على الدوال المسؤولة عن قراءة ملفات Excel
وتحويلها إلى كائنات Rectangle للاستخدام في نظام تحسين القطع.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import os
import pandas as pd
from typing import List
from core.models import Rectangle


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
    # تحديد محرك القراءة المناسب حسب امتداد الملف
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx":
            engine = "openpyxl"
        elif ext == ".xls":
            engine = "xlrd"
        else:
            # محاولة استخدام openpyxl للملفات غير المعروفة
            engine = "openpyxl"
        
        # قراءة الملف باستخدام المحرك المحدد
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine=engine)
        
    except Exception as e:
        # محاولة بديلة بدون تحديد المحرك
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        except Exception as e2:
            raise Exception(f"فشل في قراءة الملف: {e2}")

    # تحويل البيانات إلى كائنات Rectangle
    carpets = []
    for idx, row in df.iterrows():
        try:
            # استخراج البيانات من الأعمدة الثلاثة الأولى
            width = int(row[0])    # العرض
            length = int(row[1])   # الطول
            quantity = int(row[2]) # الكمية
            
            # إنشاء كائن Rectangle جديد
            carpet = Rectangle(
                id=idx + 1,  # معرف فريد يبدأ من 1
                width=width,
                length=length,
                qty=quantity
            )
            carpets.append(carpet)
            
        except (ValueError, TypeError) as e:
            # تجاهل الصفوف التي تحتوي على بيانات غير صحيحة
            continue
            
    return carpets


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
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> if validate_excel_data(carpets):
    >>>     print("البيانات صحيحة")
    """
    if not carpets:
        return False
        
    # فحص القيم السالبة أو الصفرية
    invalid_items = []
    for carpet in carpets:
        if carpet.width <= 0 or carpet.length <= 0 or carpet.qty <= 0:
            invalid_items.append(carpet.id)
    
    if invalid_items:
        return False
        
    return True


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
        قاموس يحتوي على الإحصائيات التالية:
        - total_items: إجمالي عدد العناصر
        - total_quantity: إجمالي الكمية
        - total_area: إجمالي المساحة
        - unique_sizes: عدد الأحجام الفريدة
        - width_range: نطاق العرض (min, max)
        - length_range: نطاق الطول (min, max)
        
    أمثلة:
    -------
    >>> carpets = read_input_excel("data.xlsx")
    >>> summary = get_excel_summary(carpets)
    >>> print(f"إجمالي الكمية: {summary['total_quantity']}")
    """
    if not carpets:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'unique_sizes': 0,
            'width_range': (0, 0),
            'length_range': (0, 0)
        }
    
    # حساب الإحصائيات
    total_quantity = sum(carpet.qty for carpet in carpets)
    total_area = sum(carpet.width * carpet.length * carpet.qty for carpet in carpets)
    
    # إيجاد الأحجام الفريدة
    unique_sizes = len(set((carpet.width, carpet.length) for carpet in carpets))
    
    # نطاقات الأبعاد
    widths = [carpet.width for carpet in carpets]
    lengths = [carpet.length for carpet in carpets]
    
    return {
        'total_items': len(carpets),
        'total_quantity': total_quantity,
        'total_area': total_area,
        'unique_sizes': unique_sizes,
        'width_range': (min(widths), max(widths)),
        'length_range': (min(lengths), max(lengths))
    }
