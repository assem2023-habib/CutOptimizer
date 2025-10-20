"""
وحدة الفلاتر لملفات Excel
=========================

هذه الوحدة تحتوي على الدوال المسؤولة عن إضافة الفلاتر
للجداول في ملفات Excel لتحسين تجربة المستخدم.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple


def add_filters_to_details_sheet(writer, sheet_name: str, df: pd.DataFrame) -> None:
    """إضافة فلاتر للأعمدة المحددة في جدول تفاصيل المجموعات."""
    if df.empty:
        return

    worksheet = writer.sheets[sheet_name]

    # تحديد أعمدة الفلاتر
    # رقم المجموعة (العمود الأول)
    group_number_col = 0

    # العرض (العمود الرابع)
    width_col = 3

    # الكمية المستخدمة (العمود السادس)
    used_qty_col = 5

    # تحديد موقع الفلاتر - بعد خمسة أعمدة من آخر عمود في الجدول
    last_data_col = len(df.columns) - 1  # آخر عمود في البيانات (7)
    filter_start_col = last_data_col + 5  # العمود 12

    # إضافة عناوين الفلاتر
    filter_headers = ["فلتر رقم المجموعة", "فلتر العرض", "فلتر الكمية المستخدمة"]

    # إضافة عناوين الفلاتر في الصف الثاني
    filter_row = 1
    for i, header in enumerate(filter_headers):
        col_index = filter_start_col + i
        worksheet.write(filter_row, col_index, header, create_filter_header_format(writer))

    # إضافة خلايا الفلاتر في الصف الثالث
    filter_data_row = 2

    # فلتر رقم المجموعة - قائمة منسدلة لاختيار رقم المجموعة
    worksheet.data_validation(
        filter_data_row, filter_start_col, filter_data_row, filter_start_col,
        {
            'validate': 'list',
            'source': f'={sheet_name}!${chr(65 + group_number_col)}$3:${chr(65 + group_number_col)}${len(df) + 2}',
            'input_title': 'اختر رقم المجموعة',
            'input_message': 'اختر رقم المجموعة من القائمة'
        }
    )

    # فلتر العرض - قائمة منسدلة للقيم الفريدة من عمود العرض
    worksheet.data_validation(
        filter_data_row, filter_start_col + 1, filter_data_row, filter_start_col + 1,
        {
            'validate': 'list',
            'source': f'={sheet_name}!${chr(65 + width_col)}$3:${chr(65 + width_col)}${len(df) + 2}',
            'input_title': 'اختر العرض',
            'input_message': 'اختر العرض من القائمة'
        }
    )

    # فلتر الكمية المستخدمة - قائمة منسدلة للقيم الفريدة من عمود الكمية المستخدمة
    worksheet.data_validation(
        filter_data_row, filter_start_col + 2, filter_data_row, filter_start_col + 2,
        {
            'validate': 'list',
            'source': f'={sheet_name}!${chr(65 + used_qty_col)}$3:${chr(65 + used_qty_col)}${len(df) + 2}',
            'input_title': 'اختر الكمية المستخدمة',
            'input_message': 'اختر الكمية المستخدمة من القائمة'
        }
    )

    # إضافة فلاتر Excel للأعمدة الأصلية
    # فلتر لعمود رقم المجموعة
    worksheet.autofilter(0, group_number_col, len(df) + 10, group_number_col)

    # فلتر لعمود العرض
    worksheet.autofilter(0, width_col, len(df) + 10, width_col)

    # فلتر لعمود الكمية المستخدمة
    worksheet.autofilter(0, used_qty_col, len(df) + 10, used_qty_col)

    # ضبط عرض أعمدة الفلاتر
    for i in range(3):
        col_index = filter_start_col + i
        worksheet.set_column(col_index, col_index, 20)  # عرض ثابت لأعمدة الفلاتر


def create_filter_header_format(writer) -> any:
    """إنشاء تنسيق لعناوين الفلاتر."""
    return writer.book.add_format({
        'bold': True,
        'font_size': 11,
        'font_name': 'Arial',
        'bg_color': '#E6E6FA',  # أزرق فاتح مميز
        'font_color': '#000080',  # أزرق داكن
        'border': 1,
        'border_color': 'black',
        'align': 'center',
        'valign': 'vcenter'
    })


def create_filter_cell_format(writer) -> any:
    """إنشاء تنسيق لخلايا الفلاتر."""
    return writer.book.add_format({
        'font_size': 10,
        'font_name': 'Arial',
        'bg_color': '#F0F8FF',  # أزرق فاتح جداً
        'border': 1,
        'border_color': '#CCCCCC',
        'align': 'center',
        'valign': 'vcenter'
    })

