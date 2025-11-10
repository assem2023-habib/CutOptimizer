
import pandas as pd
from typing import List, Dict, Optional, Tuple
from models.data_models import Carpet, GroupCarpet, CarpetUsed
import traceback

# استيراد دوال إنشاء الصفحات من الملف المنفصل
from .excel_sheets import (
    _create_group_details_sheet,
    _create_group_summary_sheet,
    _create_remaining_sheet,
    _create_totals_sheet,
    _create_audit_sheet,
    _generate_waste_sheet
)


# =============================================================================
# MAIN FUNCTION - الدالة الرئيسية
# =============================================================================

def write_output_excel(
    path: str,
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    remainder_groups: Optional[List[GroupCarpet]] = None,
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None,
    originals: Optional[List[Carpet]] = None,
    enhanced_remainder_groups: Optional[List[GroupCarpet]] = None
) -> None:
    """
    كتابة النتائج إلى ملف Excel مع صفحات متعددة.
    
    المعاملات:
    ----------
    path : str
        مسار ملف Excel الناتج
    groups : List[GroupCarpet]
        المجموعات الأصلية
    remaining : List[Carpet]
        العناصر المتبقية
    remainder_groups : Optional[List[GroupCarpet]]
        مجموعات البواقي العادية
    enhanced_remainder_groups : Optional[List[GroupCarpet]]
        مجموعات البواقي المحسنة
    min_width : Optional[int]
        الحد الأدنى للعرض
    max_width : Optional[int]
        الحد الأقصى للعرض
    tolerance_length : Optional[int]
        السماحية للطول
    originals : Optional[List[Carpet]]
        البيانات الأصلية للتدقيق
    """
    # إنشاء ورقة تفاصيل المجموعات
    df1 = _create_group_details_sheet(groups, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة ملخص المجموعات
    df2 = _create_group_summary_sheet(groups, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة السجاد المتبقي
    df3 = _create_remaining_sheet(remaining)

    # إنشاء ورقة الإجماليات
    totals_df = _create_totals_sheet(originals ,groups, remaining, remainder_groups, enhanced_remainder_groups)

    # إنشاء ورقة إحصائيات المجموعات الإضافية
    waste_df = _generate_waste_sheet(groups, max_width) 

    # إنشاء ورقة التدقيق
    df_audit = _create_audit_sheet(groups, remaining, remainder_groups, enhanced_remainder_groups, originals)

    _write_all_sheets_to_excel(
        path, df1, df2, df3, totals_df, df_audit, waste_df
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
    df_audit: pd.DataFrame,
    waste_df: pd.DataFrame
) -> None:
    """كتابة جميع الأوراق إلى ملف Excel مع ضبط تلقائي لعرض الأعمدة."""
    try:
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            if not df1.empty:
                df1.to_excel(writer, sheet_name='تفاصيل المجموعات', index=False)

            if not df2.empty:
                df2.to_excel(writer, sheet_name='ملخص المجموعات', index=False)

            if not df3.empty:
                df3.to_excel(writer, sheet_name='السجاد المتبقي', index=False)

            if not totals_df.empty:
                totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)

            # كتابة ورقة التدقيق
            if not df_audit.empty:
                df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)

            if not waste_df.empty:
                waste_df.to_excel(writer, sheet_name='الهادر', index=False)
            # ضبط عرض الأعمدة تلقائياً لكل ورقة
            _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit, waste_df)

    except Exception as e2:
        raise


def _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit, waste_df):
    workbook = writer.book

    header_format = _create_header_format(workbook)
    total_format = _create_total_format(workbook)
    normal_format = _create_normal_format(workbook)
    number_format = _create_number_format(workbook)

    sheet_dataframes = {}

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

    if not waste_df.empty:
        sheet_dataframes['الهادر'] = waste_df

    for sheet_name, df in sheet_dataframes.items():
        if sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            try:
                _apply_advanced_formatting(
                    writer,
                    sheet_name,
                    df,
                    header_format,
                    total_format,
                    normal_format,
                    number_format
                )

                for i, col in enumerate(df.columns):
                    try:
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))  
                        )
                        column_width = min(max_length + 2, 50)
                        worksheet.set_column(i, i, column_width)
                    except Exception as e:
                        worksheet.set_column(i, i, 15)

            except Exception as e:
                traceback.print_exc()

def _apply_advanced_formatting(writer, sheet_name, df, header_format, total_format, normal_format, number_format):
    worksheet = writer.sheets[sheet_name]

    try:
        numeric_cols = ['العرض', 'الطول','الارتفاع', 'الكمية المستخدمة', 'الكمية الأصلية',
                                  'الطول الاجمالي للسجادة', 'العرض الإجمالي', 'الطول الإجمالي المرجعي (التقريبي)',
                                  'المساحة الإجمالية', 'الكمية المتبقية', 'الإجمالي قبل العملية',
                                  'الإجمالي بعد العملية', 'المستهلك', 'الكفاءة (%)']
        
        for col_num, col_name in enumerate(df.columns, start=0):
            col_data = df[col_name].astype(str)
            max_len = max(col_data.str.len().max(), len(str(col_name)))
            column_width = min(max_len + 3, 60)
            worksheet.set_column(col_num, col_num, column_width)

        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)

        df_with_summary = _add_summary_row(df)

        total_rows_found = set()

        for row_num in range(len(df_with_summary)):
            if row_num == len(df_with_summary) - 1 and len(df_with_summary) > 0:
                excel_row = row_num + 1
                num_cols = len(df_with_summary.columns)

                for col_num in range(num_cols):
                    col_name = df_with_summary.columns[col_num]
                    cell_value = df_with_summary.iloc[row_num, col_num]

                    summary_format = writer.book.add_format({
                        'bold': True,
                        'font_size': 11,
                        'font_name': 'Arial',
                        'bg_color': '#E6F3FF',
                        'font_color': '#0066CC',
                        'border': 2,
                        'border_color': '#006400',
                        'align': 'center',
                        'valign': 'vcenter',
                        'num_format': '#,##0.00'
                    })

                    if col_name in numeric_cols:
                        try:
                            numeric_value = float(cell_value)
                            worksheet.write(excel_row, col_num, numeric_value, summary_format)
                        except (ValueError, TypeError):
                            worksheet.write(excel_row, col_num, cell_value, summary_format)
                    else:
                        worksheet.write(excel_row, col_num, cell_value, summary_format)
            else:
                if row_num in total_rows_found:
                    continue

                is_total_row = _is_total_row_simple(df_with_summary, row_num)

                if is_total_row:
                    _apply_total_row_formatting(worksheet, df_with_summary, row_num, total_format, total_rows_found)
                else:
                    excel_row = row_num + 1
                    num_cols = len(df_with_summary.columns)

                    for col_num in range(num_cols):
                        col_name = df_with_summary.columns[col_num]
                        cell_value = df_with_summary.iloc[row_num, col_num]

                        if col_name in numeric_cols:
                            try:
                                numeric_value = float(cell_value)
                                worksheet.write(excel_row, col_num, numeric_value, number_format)
                            except (ValueError, TypeError):
                                worksheet.write(excel_row, col_num, cell_value, normal_format)
                        else:
                            worksheet.write(excel_row, col_num, cell_value, normal_format)

        excel_rows = 1 + len(df_with_summary)
        max_col = len(df.columns)

        border_format = writer.book.add_format({
            'border': 3,  
            'border_color': '#006400',  
            'bg_color': '#E8F5E8'  
        })

        for row_num in range(excel_rows):
            for col_num in range(max_col):
                if row_num == 0 or row_num == excel_rows - 1 or col_num == 0 or col_num == max_col:
                    if row_num == 0:
                        continue
                    else:
                        if row_num >= 1 and row_num - 1 < len(df):
                            cell_value = df.iloc[row_num - 1, col_num]
                        else:
                            cell_value = ''
                        worksheet.write(row_num, col_num, cell_value, border_format)

        add_conditional_formatting(writer, worksheet, df)

    except Exception as e:
        traceback.print_exc()
        raise

def _add_summary_row(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    
    df_with_summary= df.copy()

    summary_row= {}

    for col in df.columns:
        if col == df.columns[0]:
            summary_row[col] = "المجموع"
        else:
            if pd.api.types.is_numeric_dtype(df[col]):
                total = df[col].sum()
                summary_row[col] = total
            else:
                summary_row[col]= ""

    df_with_summary= pd.concat([df_with_summary, pd.DataFrame([summary_row])], ignore_index=True)
    return df_with_summary

# =============================================================================
# FORMAT CREATION FUNCTIONS - دوال إنشاء التنسيقات
# =============================================================================

def add_conditional_formatting(writer, worksheet, df: pd.DataFrame) -> None:
    """إضافة تنسيقات شرطية لتمييز البيانات."""
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
        pass
    
def _create_header_format(workbook):
    """إنشاء تنسيق لعناوين الأعمدة."""
    return workbook.add_format({
        'bold': True,
        'font_size': 12,
        'font_name': 'Arial',
        'bg_color': '#4F81BD',
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
    })


# =============================================================================
# HELPER FUNCTIONS - دوال مساعدة
# =============================================================================

def _is_total_row_simple(df, row_num):
    """تحقق إذا كان الصف صف مجاميع."""
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

            if isinstance(cell_value, str):
                total_keywords = ['مجموع', 'total', 'sum', 'إجمالي', 'كلي']
                if any(keyword in cell_value.lower() for keyword in total_keywords):
                    return True

        except Exception:
            continue

    return False

def _apply_total_row_formatting(worksheet, df, row_num, total_format, total_rows_found):
    if row_num >= len(df):
        return

    total_rows_found.add(row_num)

    excel_row = row_num + 1
    
    for col_num in range(len(df.columns)):
        try:
            cell_value = df.iloc[row_num, col_num]

            if pd.notna(cell_value) and cell_value != '':
                try:
                    numeric_value = float(cell_value)
                    worksheet.write(excel_row, col_num, numeric_value, total_format)
                except (ValueError, TypeError):
                    worksheet.write(excel_row, col_num, str(cell_value), total_format)
            else:
                worksheet.write(excel_row, col_num, '', total_format)
        except Exception:
            try:
                worksheet.write(excel_row, col_num, str(cell_value), total_format)
            except:
                worksheet.write(excel_row, col_num, '', total_format)

