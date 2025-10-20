"""
وحدة كتابة ملفات Excel
=====================

هذه الوحدة تحتوي على الدوال المسؤولة عن كتابة النتائج إلى ملفات Excel
بشكل منظم ومفصل مع إحصائيات شاملة.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from core.models import Rectangle, Group, UsedItem
from pandas.api.types import is_numeric_dtype

# استيراد دوال إنشاء الصفحات من الملف المنفصل
from .excel_sheets import (
    _create_group_details_sheet,
    _create_group_summary_sheet,
    _create_remaining_sheet,
    _create_totals_sheet,
    _create_audit_sheet,
    _create_enhanced_stats_sheet,
    _create_ui_summary_sheet,
    _create_optimized_remainder_groups_sheet,
    _create_suggestions_sheet,
    _create_size_suggestions_sheet,
    _suggest_additional_items
)


# =============================================================================
# MAIN FUNCTION - الدالة الرئيسية
# =============================================================================

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
    # إنشاء ورقة تفاصيل المجموعات
    df1 = _create_group_details_sheet(groups, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة ملخص المجموعات
    df2 = _create_group_summary_sheet(groups, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة السجاد المتبقي
    df3 = _create_remaining_sheet(remaining)

    # إنشاء ورقة الإجماليات
    totals_df = _create_totals_sheet(groups, remaining, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة إحصائيات المجموعات الإضافية
    df_enhanced_stats = _create_enhanced_stats_sheet(enhanced_remainder_groups)

    # إنشاء ورقة التدقيق
    df_audit = _create_audit_sheet(groups, remaining, remainder_groups, enhanced_remainder_groups, originals)

    # إنشاء ورقة اقتراحات تشكيل المجموعات المحسنة
    df_optimized = _create_optimized_remainder_groups_sheet(
        remaining, originals, min_width, max_width, tolerance_length
    )

    # كتابة جميع الأوراق إلى الملف
    _write_all_sheets_to_excel(
        path, df1, df2, df3, totals_df, df_enhanced_stats, df_audit, df_optimized
    )

# =============================================================================
# WRITING & FORMATTING FUNCTIONS - دوال الكتابة والتنسيق
# =============================================================================

def _write_all_sheets_to_excel(
    path: str,
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df3: pd.DataFrame,
    totals_df: pd.DataFrame,
    df_enhanced_stats: pd.DataFrame,
    df_audit: pd.DataFrame,
    df_optimized: pd.DataFrame,
) -> None:
    """كتابة جميع الأوراق إلى ملف Excel مع ضبط تلقائي لعرض الأعمدة."""
    try:
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            # كتابة الأوراق الأساسية فقط لتجنب المشاكل
            if not df1.empty:
                df1.to_excel(writer, sheet_name='تفاصيل المجموعات', index=False)

            if not df2.empty:
                df2.to_excel(writer, sheet_name='ملخص المجموعات', index=False)

            if not df3.empty:
                df3.to_excel(writer, sheet_name='السجاد المتبقي', index=False)

            if not totals_df.empty:
                totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)

            # كتابة ورقة التدقيق
            try:
                if not df_audit.empty:
                    df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)
            except Exception as e:
                # Silent error handling for audit sheet
                pass

            # ضبط عرض الأعمدة تلقائياً لكل ورقة
            _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit)

    except Exception as e:
        # Silent error handling for production - attempt simplified file creation
        # محاولة كتابة ملف مبسط جداً في حالة الخطأ
        try:
            with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
                df1.to_excel(writer, sheet_name='تفاصيل المجموعات', index=False)
                df2.to_excel(writer, sheet_name='ملخص المجموعات', index=False)
                df3.to_excel(writer, sheet_name='السجاد المتبقي', index=False)
                totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)
                df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)

                # ضبط عرض الأعمدة تلقائياً للنسخة المبسطة
                _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit)

        except Exception as e2:
            # If even the simplified version fails, just pass silently
            pass


def _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit):
    """ضبط عرض الأعمدة تلقائياً وتطبيق التنسيقات الجمالية لجميع الأوراق في ملف Excel."""
    # الحصول على workbook وإنشاء التنسيقات
    workbook = writer.book

    # إنشاء التنسيقات
    header_format = _create_header_format(workbook)
    total_format = _create_total_format(workbook)
    normal_format = _create_normal_format(workbook)
    number_format = _create_number_format(workbook)

    # قاموس يربط أسماء الأوراق بـ DataFrames الخاصة بها
    sheet_dataframes = {}

    # إضافة الأوراق المكتوبة فقط
    if not df1.empty:
        sheet_dataframes['تفاصيل المجموعات'] = df1

    if not df2.empty:
        sheet_dataframes['ملخص المجموعات'] = df2

    if not df3.empty:
        sheet_dataframes['السجاد المتبقي'] = df3

    if not totals_df.empty:
        sheet_dataframes['الإجماليات'] = totals_df

    if not df_audit.empty:
        sheet_dataframes['تدقيق الكميات'] = df_audit


    # تطبيق التنسيقات لكل ورقة
    for sheet_name, df in sheet_dataframes.items():
        if sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            try:
                # تطبيق التنسيقات المتقدمة على الورقة
                _apply_advanced_formatting(
                    writer,
                    sheet_name,
                    df,
                    header_format,
                    total_format,
                    normal_format,
                    number_format
                )

                # ضبط عرض الأعمدة تلقائياً
                for i, col in enumerate(df.columns):
                    try:
                        max_length = max(
                            df[col].astype(str).apply(len).max(),  # أطول قيمة في العمود
                            len(str(col))  # عنوان العمود
                        )
                        # تحديد عرض عمود معقول
                        column_width = min(max_length + 2, 50)  # حد أقصى للعرض 50 حرف
                        worksheet.set_column(i, i, column_width)
                    except Exception as e:
                        # في حالة حدوث خطأ في ضبط عرض العمود، استمر بالعمود التالي
                        worksheet.set_column(i, i, 15)  # عرض افتراضي
                        continue

            except Exception as e:
                import traceback
                traceback.print_exc()


def _add_summary_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    إضافة صف مجاميع في نهاية الجدول.

    المعاملات:
    -----------
    df : pd.DataFrame
        الجدول الأصلي

    الإرجاع:
    --------
    pd.DataFrame: الجدول مع صف المجاميع المضاف
    """
    if df.empty:
        return df

    # نسخ الجدول لتجنب التعديل على الأصلي
    df_with_summary = df.copy()

    # إنشاء صف المجاميع
    summary_row = {}

    for col in df.columns:
        if col == df.columns[0]:  # العمود الأول يكون "المجموع"
            summary_row[col] = "المجموع"
        else:
            # محاولة حساب مجموع القيم الرقمية فقط
            try:
                # محاولة تحويل العمود إلى أرقام مع تجاهل القيم النصية
                numeric_values = pd.to_numeric(df[col], errors='coerce')
                # حساب مجموع القيم الرقمية الصالحة فقط
                valid_numeric = numeric_values.dropna()
                if len(valid_numeric) > 0:  # إذا كان هناك قيم رقمية صالحة
                    total = valid_numeric.sum()
                    # تنسيق العدد بحيث يظهر بطريقة مناسبة
                    if total == int(total):
                        summary_row[col] = int(total)
                    else:
                        summary_row[col] = round(total, 2)
                else:
                    summary_row[col] = ""  # عمود نصي فارغ
            except:
                summary_row[col] = ""  # في حالة فشل الحساب

    # إضافة صف المجاميع في النهاية
    df_with_summary = pd.concat([df_with_summary, pd.DataFrame([summary_row])], ignore_index=True)

    return df_with_summary


def _apply_advanced_formatting(writer, sheet_name, df, header_format, total_format, normal_format, number_format):
    """تطبيق التنسيقات المتقدمة على الورقة مع حل مشكلة الصفوف المكررة."""
    worksheet = writer.sheets[sheet_name]

    try:
        # ضبط عرض الأعمدة تلقائياً
        for col_num, col_name in enumerate(df.columns, start=0):
            # الحصول على أطول محتوى في العمود
            col_data = df[col_name].astype(str)
            # حساب أطول طول للمحتوى في العمود
            max_len = max(col_data.str.len().max(), len(str(col_name)))
            # ضبط عرض العمود بناءً على أطول محتوى
            column_width = min(max_len + 3, 60)
            worksheet.set_column(col_num, col_num, column_width)

        # تطبيق تنسيق العناوين (الصف الأول)
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(1, col_num, col_name, header_format)

        # إضافة صف مجاميع في نهاية الجدول
        df = _add_summary_row(df)

        # تطبيق تنسيقات للبيانات - حل مشكلة الصفوف المكررة
        total_rows_found = set()  # لتتبع الصفوف التي تم التعامل معها كصفوف مجاميع

        for row_num in range(len(df)):
            # الصف الأخير هو صف المجاميع - تعامله بشكل خاص
            if row_num == len(df) - 1 and len(df) > 0:
                # صف المجاميع - تطبيق التنسيق الخاص مع الخط المغمق والمحاذاة في المنتصف
                excel_row = row_num + 1
                for col_num in range(len(df.columns)):
                    cell_value = df.iloc[row_num, col_num]
                    col_name = df.columns[col_num]

                    # إنشاء تنسيق خاص لصف المجاميع مع خط مغمق ومحاذاة في المنتصف
                    summary_format = writer.book.add_format({
                        'bold': True,  # خط مغمق
                        'font_size': 11,
                        'font_name': 'Arial',
                        'bg_color': '#E6F3FF',  # أزرق فاتح مميز
                        'font_color': '#0066CC',  # أزرق داكن
                        'border': 2,
                        'border_color': '#006400',
                        'align': 'center',  # محاذاة في المنتصف
                        'valign': 'vcenter',
                        'num_format': '#,##0.00'
                    })

                    if col_name in ['العرض', 'الطول', 'الكمية المستخدمة', 'الكمية الأصلية',
                                  'الطول الاجمالي للسجادة', 'العرض الإجمالي', 'الطول الإجمالي المرجعي (التقريبي)',
                                  'المساحة الإجمالية', 'الكمية المتبقية', 'الإجمالي قبل العملية',
                                  'الإجمالي بعد العملية', 'المستهلك', 'الكفاءة (%)']:
                        # تنسيق خاص للأرقام في صف المجاميع
                        try:
                            numeric_value = float(cell_value) if cell_value != '' else 0
                            worksheet.write(excel_row, col_num, numeric_value, summary_format)
                        except (ValueError, TypeError):
                            worksheet.write(excel_row, col_num, cell_value, summary_format)
                    else:
                        # تنسيق خاص للنصوص في صف المجاميع
                        worksheet.write(excel_row, col_num, cell_value, summary_format)
            else:
                # تجنب معالجة نفس الصف مرتين كصفوف مجاميع
                if row_num in total_rows_found:
                    continue

                # تحقق بسيط وبديهي لتحديد صفوف المجاميع
                is_total_row = _is_total_row_simple(df, row_num)

                if is_total_row:
                    # تطبيق تنسيق صف المجاميع على هذا الصف والصف التالي إذا كان فارغاً
                    _apply_total_row_formatting(worksheet, df, row_num, total_format, total_rows_found)
                else:
                    # تطبيق التنسيقات العادية للبيانات مع الحواف واللون الأخضر
                    # كتابة البيانات في السطر row_num + 1 (بعد العناوين في السطر 1)
                    excel_row = row_num + 1
                    for col_num in range(len(df.columns)):
                        cell_value = df.iloc[row_num, col_num]
                        col_name = df.columns[col_num]

                        if col_name in ['العرض', 'الطول', 'الكمية المستخدمة', 'الكمية الأصلية',
                                      'الطول الاجمالي للسجادة', 'العرض الإجمالي', 'الطول الإجمالي المرجعي (التقريبي)',
                                      'المساحة الإجمالية', 'الكمية المتبقية', 'الإجمالي قبل العملية',
                                      'الإجمالي بعد العملية', 'المستهلك', 'الكفاءة (%)']:
                            # تنسيق خاص للأرقام مع الحواف واللون الأخضر
                            try:
                                numeric_value = float(cell_value) if cell_value != '' else 0
                                worksheet.write(excel_row, col_num, numeric_value, number_format)
                            except (ValueError, TypeError):
                                worksheet.write(excel_row, col_num, cell_value, normal_format)
                        else:
                            # تنسيق عام للنصوص مع الحواف واللون الأخضر
                            worksheet.write(excel_row, col_num, cell_value, normal_format)

        
        # إضافة حواف خارجية قوية للجدول بالكامل
        # حساب عدد الصفوف في Excel (عناوين الأعمدة + البيانات + صف المجاميع)
        excel_rows = 1 + len(df)  # عناوين (1) + البيانات (len(df))
        max_col = len(df.columns) - 1

        # إضافة حافة خارجية للجدول بالكامل
        border_format = writer.book.add_format({
            'border': 3,  # حافة خارجية سميكة جداً
            'border_color': '#006400',  # أخضر داكن
            'bg_color': '#E8F5E8'  # نفس اللون الأخضر الفاتح
        })

        # تطبيق الحافة الخارجية على الجدول بالكامل
        for row_num in range(excel_rows):
            for col_num in range(max_col + 1):
                # الحواف الخارجية فقط (استثناء العناوين في الصف الأول)
                if row_num == 0 or row_num == excel_rows - 1 or col_num == 0 or col_num == max_col:
                    if row_num == 0:
                        # لا نكتب فوق العناوين في الصف الأول
                        continue
                    else:
                        # التأكد من عدم تجاوز حدود DataFrame (يشمل صف المجاميع)
                        if row_num >= 1 and row_num - 1 < len(df):
                            cell_value = df.iloc[row_num - 1, col_num]
                        else:
                            cell_value = ''
                        worksheet.write(row_num, col_num, cell_value, border_format)

        # إضافة تنسيقات شرطية لتحسين المظهر
        add_conditional_formatting(writer, worksheet, df)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


# =============================================================================
# FORMAT CREATION FUNCTIONS - دوال إنشاء التنسيقات
# =============================================================================

def add_conditional_formatting(writer, worksheet, df: pd.DataFrame) -> None:
    """إضافة تنسيقات شرطية لتمييز البيانات."""
    # تنسيق شرطي للكفاءة العالية (أكبر من 80%)
    try:
        efficiency_col = None
        for col_num, col_name in enumerate(df.columns):
            if 'كفاءة' in col_name or 'كفاءة' in str(col_name):
                efficiency_col = col_num
                break

        if efficiency_col is not None:
            worksheet.conditional_format(2, efficiency_col, len(df) + 1, efficiency_col, {
                'type': 'cell',
                'criteria': '>',
                'value': 80,
                'format': writer.book.add_format({
                    'bg_color': '#C6EFCE',  # أخضر فاتح للكفاءة العالية
                    'font_color': '#006100'
                })
            })
    except Exception as e:
        # معالجة أفضل للأخطاء
        print(f"خطأ في التنسيق الشرطي للكفاءة: {e}")
        pass
    
def _create_header_format(workbook):
    """إنشاء تنسيق لعناوين الأعمدة."""
    return workbook.add_format({
        'bold': True,
        'font_size': 12,
        'font_name': 'Arial',
        'bg_color': '#4F81BD',  # أزرق متوسط
        'font_color': 'white',
        'border': 1,
        'border_color': 'black',
        'align': 'center',
        'valign': 'vcenter'
    })


def _create_total_format(workbook):
    """إنشاء تنسيق لصفوف المجاميع."""
    return workbook.add_format({
        'bold': True,
        'font_size': 11,
        'font_name': 'Arial',
        'bg_color': '#C6EFCE',  # أخضر فاتح
        'font_color': '#006100',  # أخضر داكن
        'border': 1,
        'border_color': 'black',
        'align': 'center',
        'num_format': '#,##0.00'
    })


def _create_normal_format(workbook):
    """إنشاء تنسيق عام للبيانات النصية مع لون أخضر فاتح."""
    return workbook.add_format({
        'bold': True,  # خط غامق
        'font_size': 10,
        'font_name': 'Arial',
        'border': 2,  # حواف أكثر سمكاً
        'border_color': '#006400',  # أخضر داكن للحواف
        'bg_color': '#E8F5E8',  # أخضر فاتح جداً للخلفية
        'font_color': '#006400',  # أخضر داكن للنص,
        'align': 'center',
        'valign': 'vcenter'
    })


def _create_number_format(workbook):
    """إنشاء تنسيق خاص للأرقام مع لون أخضر فاتح."""
    return workbook.add_format({
        'bold': True,  # خط غامق
        'font_size': 10,
        'font_name': 'Arial',
        'border': 2,  # حواف أكثر سمكاً
        'border_color': '#006400',  # أخضر داكن للحواف
        'bg_color': '#E8F5E8',  # أخضر فاتح جداً للخلفية
        'font_color': '#006400',  # أخضر داكن للنص
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '#,##0.00'
    })


# =============================================================================
# HELPER FUNCTIONS - دوال مساعدة
# =============================================================================

def _is_total_row_simple(df, row_num):
    """
    تحقق محسّن لتحديد ما إذا كان الصف صف مجاميع.

    الإصلاحات:
    - فصل التحقق من القيم الرقمية عن الكلمات النصية
    - معالجة أفضل للقيم الفارغة
    - التحقق من وجود الأعمدة أولاً
    """
    if row_num >= len(df):
        return False

    # الأعمدة التي تدل على صفوف المجاميع
    total_indicators = [
        'العرض الإجمالي',
        'الطول الإجمالي المرجعي (التقريبي)',
        'المساحة الإجمالية'
    ]

    for col_name in total_indicators:
        if col_name not in df.columns:
            continue

        try:
            cell_value = df.iloc[row_num, df.columns.get_loc(col_name)]

            if pd.isna(cell_value) or cell_value == '':
                continue

            # التحقق من القيم الرقمية الكبيرة
            try:
                numeric_val = float(str(cell_value).replace(',', ''))
                if numeric_val > 1000:
                    return True
            except (ValueError, TypeError):
                pass

            # التحقق من الكلمات الدالة على المجاميع (للخلايا النصية فقط)
            if isinstance(cell_value, str):
                total_keywords = ['مجموع', 'total', 'sum', 'إجمالي', 'كلي']
                if any(keyword in cell_value.lower() for keyword in total_keywords):
                    return True

        except Exception:
            continue

    return False


def _apply_total_row_formatting(worksheet, df, row_num, total_format, total_rows_found):
    """
    تطبيق تنسيق صف المجاميع مع تجنب التكرار.

    المعاملات:
    -----------
    worksheet : xlsxwriter.worksheet
        ورقة Excel
    df : pd.DataFrame
        البيانات
    row_num : int
        رقم الصف (في DataFrame)
    total_format : xlsxwriter.format
        تنسيق المجاميع
    total_rows_found : set
        مجموعة الصفوف المعالجة (لتجنب التكرار)
    """
    if row_num >= len(df):
        return

    # إضافة الصف إلى قائمة الصفوف المعالجة
    total_rows_found.add(row_num)

    # تطبيق التنسيق على جميع الأعمدة في الصف
    # +1 لحساب صف العناوين (1)
    excel_row = row_num + 1

    for col_num in range(len(df.columns)):
        try:
            cell_value = df.iloc[row_num, col_num]

            # محاولة تحويل القيمة لرقم
            if pd.notna(cell_value) and cell_value != '':
                try:
                    numeric_value = float(cell_value)
                    worksheet.write(excel_row, col_num, numeric_value, total_format)
                except (ValueError, TypeError):
                    worksheet.write(excel_row, col_num, str(cell_value), total_format)
            else:
                worksheet.write(excel_row, col_num, '', total_format)
        except Exception:
            # في حالة أي خطأ، كتابة القيمة كنص
            try:
                worksheet.write(excel_row, col_num, str(cell_value), total_format)
            except:
                worksheet.write(excel_row, col_num, '', total_format)

def _add_sheet_header_info(writer, sheet_name, df):
    """إضافة معلومات إضافية في أعلى الورقة."""
    worksheet = writer.sheets[sheet_name]

    # إضافة عنوان الورقة بخط كبير وعريض
    title_format = writer.book.add_format({
        'bold': True,
        'font_size': 14,
        'font_name': 'Arial',
        'font_color': '#4F81BD',
        'align': 'center'
    })

    # إضافة تاريخ الإنشاء
    date_format = writer.book.add_format({
        'font_size': 9,
        'font_name': 'Arial',
        'font_color': '#666666',
        'align': 'right',
        'italic': True
    })

    # إضافة تاريخ الإنشاء في أعلى الورقة
    try:
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # كتابة التاريخ في الصف الأول (بدلاً من إدراج صف جديد)
        worksheet.write(0, len(df.columns) - 1, f'تاريخ الإنشاء: {current_date}', date_format)
    except:
        pass

def _create_optimized_remainder_groups_sheet(
    remaining: List[Rectangle],
    originals: Optional[List[Rectangle]],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None
) -> pd.DataFrame:
    """
    إنشاء ورقة اقتراحات تشكيل المجموعات المحسنة من المتبقيات.
    
    هذه الدالة تشكل مجموعات من المتبقيات، ثم تقترح عناصر إضافية من الأصليات.
    
    ملاحظات مهمة:
    - العرض الكلي = مجموع عرض كل نوع (مرة واحدة فقط، بغض النظر عن الكمية)
    - tolerance_ref لكل عنصر = length * qty
    - الشرط: abs(tolerance_ref1 - tolerance_ref2) <= tolerance_length
    
    المعاملات:
    -----------
    remaining : List[Rectangle]
        العناصر المتبقية.
    originals : Optional[List[Rectangle]]
        العناصر الأصلية للاقتراحات.
    min_width : Optional[int]
        الحد الأدنى للعرض (افتراضي 370).
    max_width : Optional[int]
        الحد الأقصى للعرض (افتراضي 400).
    tolerance_length : Optional[int]
        سماحية الطول (افتراضي 100).
        
    الإرجاع:
    --------
    pd.DataFrame: الورقة الجديدة.
    """
    # تعيين القيم الافتراضية
    eff_min_width = 370 if min_width is None else int(min_width)
    eff_max_width = 400 if max_width is None else int(max_width)
    eff_tolerance = 100 if tolerance_length is None else int(tolerance_length)
    
    # نسخ البيانات لتجنب التعديل
    remaining_copy = [Rectangle(r.id, r.width, r.length, r.qty) for r in remaining]
    originals_copy = [Rectangle(o.id, o.width, o.length, o.qty) for o in originals] if originals else []
    
    # قائمة للصفوف
    rows = []
    group_id = 1
    
    # تجميع المتبقيات حسب المعرف
    remaining_dict: Dict[Tuple[int, int, int], int] = {}
    for r in remaining_copy:
        key = (r.id, r.width, r.length)
        remaining_dict[key] = remaining_dict.get(key, 0) + r.qty
    
    # خوارزمية تشكيل المجموعات (Greedy مع تحسين)
    iteration = 0
    max_iterations = 1000
    
    while remaining_dict and iteration < max_iterations:
        iteration += 1
        group_items = []
        current_width = 0
        ref_length_value = None  # الطول المرجعي (من أول عنصر)
        
        # فرز المتبقيات حسب العرض تنازلياً (لاستغلال العرض أولاً)
        sorted_remaining = sorted(remaining_dict.items(), 
                                 key=lambda x: (x[0][1], x[0][2]), 
                                 reverse=True)
        
        # اختيار العنصر الأول (الأعرض)
        first_added = False
        for key, qty in sorted_remaining[:]:
            if qty <= 0:
                if key in remaining_dict:
                    del remaining_dict[key]
                continue
            
            rect_id, w, l = key
            
            # التحقق من العرض
            if current_width + w > eff_max_width:
                continue
            
            if not first_added:
                # أول عنصر: نحاول أخذ أكبر كمية ممكنة
                max_qty = min(qty, (eff_max_width - current_width) // w) if w > 0 else qty
                
                for test_qty in range(max_qty, 0, -1):
                    ref_length_value = l * test_qty
                    
                    # إضافة العنصر الأول
                    group_items.append((key, test_qty))
                    current_width += w  # العرض يُحسب مرة واحدة فقط
                    remaining_dict[key] -= test_qty
                    if remaining_dict[key] <= 0:
                        del remaining_dict[key]
                    first_added = True
                    break
                
                if first_added:
                    break
        
        if not first_added or ref_length_value is None:
            break
        
        # إضافة عناصر إضافية (شركاء)
        partners_added = True
        max_partners = 10
        
        while partners_added and current_width < eff_max_width and len(group_items) < max_partners:
            partners_added = False
            best_partner = None
            best_qty = 0
            best_new_width = current_width
            
            # البحث عن أفضل شريك
            for key, qty in list(remaining_dict.items()):
                if qty <= 0:
                    continue
                
                rect_id, w, l = key
                
                # التحقق من العرض
                new_width = current_width + w
                if new_width > eff_max_width:
                    continue
                
                # البحث عن أعظم كمية تحقق tolerance
                if l <= 0:
                    continue
                
                ideal_qty = ref_length_value / l
                search_range = max(3, int(ideal_qty * 0.2))
                
                for test_qty in range(max(1, int(ideal_qty - search_range)),
                                     min(int(ideal_qty + search_range) + 1, qty + 1)):
                    if test_qty <= 0 or test_qty > qty:
                        continue
                    
                    tolerance_ref = l * test_qty
                    diff = abs(tolerance_ref - ref_length_value)
                    
                    if diff <= eff_tolerance:
                        # عنصر مقبول: نفضل الذي يعطي أكبر عرض
                        if new_width > best_new_width or (new_width == best_new_width and test_qty > best_qty):
                            best_partner = key
                            best_qty = test_qty
                            best_new_width = new_width
                        break
            
            if best_partner:
                group_items.append((best_partner, best_qty))
                current_width = best_new_width
                remaining_dict[best_partner] -= best_qty
                if remaining_dict[best_partner] <= 0:
                    del remaining_dict[best_partner]
                partners_added = True
        
        # التحقق من صلاحية المجموعة
        if not group_items or current_width < eff_min_width:
            # مجموعة غير صالحة
            break
        
        # التحقق من وجود عنصرين مختلفين على الأقل
        unique_ids = set(item[0][0] for item in group_items)
        if len(unique_ids) < 2:
            # مجموعة من عنصر واحد - ممنوعة
            break
        
        # حساب الكفاءة
        efficiency = (current_width / eff_max_width) * 100 if eff_max_width > 0 else 0
        
        # اقتراح عناصر إضافية
        suggestions = _suggest_additional_items(
            group_items, 
            originals_copy, 
            eff_min_width, 
            eff_max_width, 
            current_width,
            ref_length_value,
            eff_tolerance
        )
        
        # إضافة الصف للورقة
        items_str = ', '.join([f"ID:{k[0]} ({k[1]}x{k[2]}) qty:{q}" for k, q in group_items])
        rows.append({
            'رقم المجموعة': f'مجموعة_{group_id}',
            'العناصر المستخدمة': items_str,
            'العرض الإجمالي': current_width,
            'الطول المرجعي': ref_length_value,
            'الكفاءة (%)': round(efficiency, 2),
            'الاقتراحات الإضافية': ', '.join(suggestions) if suggestions else 'لا توجد اقتراحات',
            'ملاحظات': 'مجموعة صالحة'
        })
        group_id += 1
    
    # إنشاء DataFrame
    df = pd.DataFrame(rows)
    
    # إضافة صف فارغ في حالة عدم وجود بيانات
    if df.empty:
        df = pd.DataFrame([{
            'رقم المجموعة': 'لا توجد مجموعات محسنة',
            'العناصر المستخدمة': 'لا توجد بيانات',
            'العرض الإجمالي': 0,
            'الطول المرجعي': 0,
            'الكفاءة (%)': 0,
            'الاقتراحات الإضافية': 'لا توجد اقتراحات',
            'ملاحظات': 'لا توجد بيانات متاحة للتحسين'
        }])
    
    return df


def _suggest_additional_items(
    group_items: List[Tuple],
    originals: List[Rectangle],
    min_width: int,
    max_width: int,
    current_width: int,
    ref_length_value: int,
    tolerance: int
) -> List[str]:
    """
    اقتراح عناصر إضافية لإكمال المجموعة بناءً على البيانات الموجودة.
    
    يتحقق من:
    1. العرض المتبقي
    2. شرط tolerance
    3. الكمية المتاحة
    
    المعاملات:
    -----------
    group_items : List[Tuple]
        العناصر الحالية في المجموعة
    originals : List[Rectangle]
        العناصر الأصلية المتاحة
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    current_width : int
        العرض الحالي للمجموعة
    ref_length_value : int
        الطول المرجعي للمجموعة
    tolerance : int
        السماحية المسموحة
        
    الإرجاع:
    --------
    List[str]: قائمة الاقتراحات
    """
    suggestions = []
    remaining_width = max_width - current_width
    
    if remaining_width <= 0:
        return suggestions
    
    # تجميع العناصر المقترحة حسب الأولوية
    candidates = []
    
    for orig in originals:
        if orig.qty <= 0 or orig.width > remaining_width:
            continue
        
        # حساب الكمية المثالية لتحقيق tolerance
        if orig.length <= 0:
            continue
        
        ideal_qty = ref_length_value / orig.length
        search_range = max(2, int(ideal_qty * 0.2))
        
        for qty in range(max(1, int(ideal_qty - search_range)),
                        min(int(ideal_qty + search_range) + 1, orig.qty + 1)):
            if qty <= 0 or qty > orig.qty:
                continue
            
            tolerance_ref = orig.length * qty
            diff = abs(tolerance_ref - ref_length_value)
            
            if diff <= tolerance:
                # عنصر مقترح صالح
                new_width = current_width + orig.width
                priority = new_width  # نفضل الذي يملأ العرض أكثر
                
                candidates.append({
                    'id': orig.id,
                    'width': orig.width,
                    'length': orig.length,
                    'qty': qty,
                    'new_width': new_width,
                    'diff': diff,
                    'priority': priority
                })
                break
    
    # ترتيب حسب الأولوية (أكبر عرض أولاً، ثم أقل فرق tolerance)
    candidates.sort(key=lambda x: (-x['priority'], x['diff']))
    
    # أخذ أفضل 3 اقتراحات
    for cand in candidates[:3]:
        suggestions.append(
            f"ID:{cand['id']} ({cand['width']}x{cand['length']}) qty:{cand['qty']} "
            f"→ عرض كلي:{cand['new_width']}"
        )
    
    return suggestions


def _apply_total_row_formatting(worksheet, df, row_num, total_format, total_rows_found):
    """
    تطبيق تنسيق صف المجاميع مع تجنب التكرار.
    
    المعاملات:
    -----------
    worksheet : xlsxwriter.worksheet
        ورقة Excel
    df : pd.DataFrame
        البيانات
    row_num : int
        رقم الصف (في DataFrame)
    total_format : xlsxwriter.format
        تنسيق المجاميع
    total_rows_found : set
        مجموعة الصفوف المعالجة (لتجنب التكرار)
    """
    if row_num >= len(df):
        return
    
    # إضافة الصف إلى قائمة الصفوف المعالجة
    total_rows_found.add(row_num)
    
    # تطبيق التنسيق على جميع الأعمدة في الصف
    # +1 لحساب صف العناوين (1)
    excel_row = row_num + 1
    
    for col_num in range(len(df.columns)):
        try:
            cell_value = df.iloc[row_num, col_num]
            
            # محاولة تحويل القيمة لرقم
            if pd.notna(cell_value) and cell_value != '':
                try:
                    numeric_value = float(cell_value)
                    worksheet.write(excel_row, col_num, numeric_value, total_format)
                except (ValueError, TypeError):
                    worksheet.write(excel_row, col_num, str(cell_value), total_format)
            else:
                worksheet.write(excel_row, col_num, '', total_format)
        except Exception:
            # في حالة أي خطأ، كتابة القيمة كنص
            try:
                worksheet.write(excel_row, col_num, str(cell_value), total_format)
            except:
                worksheet.write(excel_row, col_num, '', total_format)

