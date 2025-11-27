
import pandas as pd
from typing import List, Dict, Optional, Tuple
from models.carpet import Carpet
from models.group_carpet import GroupCarpet
import traceback
from core.config.config_manager import ConfigManager

# استيراد دوال إنشاء الصفحات من الملف المنفصل
from .excel_sheets import (
    _create_group_details_sheet,
    _create_group_summary_sheet,
    _create_remaining_sheet,
    _create_totals_sheet,
    _create_audit_sheet,
    _generate_waste_sheet,
    _create_remaining_suggestion_sheet,
    _create_enhanset_remaining_suggestion_sheet,
    _generate_detailed_waste_sheet
)

from .excel_formatting import (
    _create_header_format,
    _create_normal_format,
    _create_number_format,
    _create_summary_row_format,
    _create_border_format_for_first_column,
    add_conditional_formatting,
    _apply_row_highlight_on_selection,
    _is_summary_row
)

# =============================================================================
# COLOR GENERATION - توليد الألوان
# =============================================================================

def _generate_readable_colors(num_colors):
    """
    توليد ألوان متنوعة وقابلة للقراءة لكل قصة.
    
    المعاملات:
    ----------
    num_colors : int
        عدد الألوان المطلوبة
        
    Returns:
    --------
    list
        قائمة من الألوان بصيغة hex
    """
    import colorsys
    
    colors = []
    for i in range(num_colors):
        # استخدام HSL لتوليد ألوان متنوعة
        # Hue: توزيع متساوي على دائرة الألوان
        hue = i / num_colors
        # Saturation: تشبع متوسط لألوان هادئة
        saturation = 0.35 + (i % 3) * 0.1  # تنويع بسيط بين 0.35 و 0.55
        # Lightness: فاتح للخلفية مع قابلية القراءة
        lightness = 0.85 + (i % 2) * 0.05  # بين 0.85 و 0.90
        
        # تحويل HSL إلى RGB
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        
        # تحويل إلى hex
        hex_color = '#{:02X}{:02X}{:02X}'.format(
            int(r * 255),
            int(g * 255),
            int(b * 255)
        )
        colors.append(hex_color)
    
    return colors


# =============================================================================
# MAIN FUNCTION - الدالة الرئيسية
# =============================================================================

def write_output_excel(
    path: str,
    groups: List[GroupCarpet],
    remaining: List[Carpet],
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    tolerance_length: Optional[int] = None,
    originals: Optional[List[Carpet]] = None,
    suggested_groups: Optional[List[List[GroupCarpet]]]= None,
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
    df1 = _create_group_details_sheet(groups)

    # إنشاء ورقة ملخص المجموعات
    df2 = _create_group_summary_sheet(groups)

    # إنشاء ورقة السجاد المتبقي
    df3 = _create_remaining_sheet(remaining)

    # إنشاء ورقة الإجماليات
    totals_df = _create_totals_sheet(originals ,groups, remaining)

    # إنشاء ورقة إحصائيات المجموعات الإضافية
    waste_df = _generate_waste_sheet(groups, max_width) 

    # إنشاء ورقة التدقيق
    df_audit = _create_audit_sheet(groups, remaining, originals)

    df_suggestion_group= _create_remaining_suggestion_sheet(remaining, min_width, max_width, tolerance_length)

    df_enhanset_remaining_suggestion_sheet= _create_enhanset_remaining_suggestion_sheet(suggested_groups= suggested_groups, min_width=min_width, max_width= max_width, tolerance= tolerance_length)
    
    # إنشاء ورقة الهادر التفصيلي الجديدة
    df_detailed_waste = _generate_detailed_waste_sheet(groups)

    # Apply Unit Conversion
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        unit = config.get("measurement_unit", "cm")
        
        if unit in ['m', 'm2']:
            dfs = [df1, df2, df3, totals_df, df_audit, waste_df, df_suggestion_group, df_enhanset_remaining_suggestion_sheet, df_detailed_waste]
            _convert_dfs_units(dfs, unit)
    except Exception as e:
        print(f"Error applying unit conversion: {e}")
        traceback.print_exc()

    _write_all_sheets_to_excel(
        path, df1, df2, df3, totals_df, df_audit, waste_df, df_suggestion_group, df_enhanset_remaining_suggestion_sheet, df_detailed_waste
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
    waste_df: pd.DataFrame,
    df_suggestion_group: pd.DataFrame,
    df_enhanset_remaining_suggestion_sheet: pd.DataFrame,
    df_detailed_waste: pd.DataFrame
) -> None:
    """كتابة جميع الأوراق إلى ملف Excel مع ضبط تلقائي لعرض الأعمدة."""
    try:
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            if not df1.empty:
                df1.to_excel(writer, sheet_name='تفاصيل القصات', index=False)

            if not df2.empty:
                df2.to_excel(writer, sheet_name='ملخص القصات', index=False)

            if not df3.empty:
                df3.to_excel(writer, sheet_name='السجاد المتبقي', index=False)

            if not totals_df.empty:
                totals_df.to_excel(writer, sheet_name='الإجماليات', index=False)

            # كتابة ورقة التدقيق
            if not df_audit.empty:
                df_audit.to_excel(writer, sheet_name='تدقيق الكميات', index=False)

            if not waste_df.empty:
                waste_df.to_excel(writer, sheet_name='الهادر', index=False)
                
            if not df_detailed_waste.empty:
                df_detailed_waste.to_excel(writer, sheet_name='تحليل الهادر', index=False)

            if not df_suggestion_group.empty:
                df_suggestion_group.to_excel(writer, sheet_name='اقتراحات المتبقيات', index=False)

            if not df_enhanset_remaining_suggestion_sheet.empty:
                df_enhanset_remaining_suggestion_sheet.to_excel(writer, sheet_name='اقتراحات المتبقيات المحسنة', index=False)

            _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit, waste_df, df_suggestion_group, df_enhanset_remaining_suggestion_sheet, df_detailed_waste)

    except Exception as e2:
        raise


def _auto_adjust_column_width(writer, df1, df2, df3, totals_df, df_audit, waste_df, df_suggestion_group, df_enhanset_remaining_suggestion_sheet, df_detailed_waste):
    workbook = writer.book

    header_format = _create_header_format(workbook)
    normal_format = _create_normal_format(workbook)
    number_format = _create_number_format(workbook)
    summary_row_format = _create_summary_row_format(workbook)
    first_col_border = _create_border_format_for_first_column(workbook)
    
    sheet_dataframes = {}

    if not df1.empty:
        sheet_dataframes['تفاصيل القصات'] = df1

    if not df2.empty:
        sheet_dataframes['ملخص القصات'] = df2

    if not df3.empty:
        sheet_dataframes['السجاد المتبقي'] = df3

    if not totals_df.empty:
        sheet_dataframes['الإجماليات'] = totals_df

    if not df_audit.empty:
        sheet_dataframes['تدقيق الكميات'] = df_audit

    if not waste_df.empty:
        sheet_dataframes['الهادر'] = waste_df
        
    if not df_detailed_waste.empty:
        sheet_dataframes['تحليل الهادر'] = df_detailed_waste

    if not df_suggestion_group.empty:
        sheet_dataframes['اقتراحات المتبقيات'] = df_suggestion_group
        
    if not df_enhanset_remaining_suggestion_sheet.empty:
        sheet_dataframes['اقتراحات المتبقيات المحسنة'] = df_enhanset_remaining_suggestion_sheet

    for sheet_name, df in sheet_dataframes.items():
        if sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            try:
                _apply_advanced_formatting(
                    writer,
                    sheet_name,
                    df,
                    header_format,
                    normal_format,
                    number_format,
                    summary_row_format,
                    first_col_border
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

def _apply_advanced_formatting(
        writer, 
        sheet_name, 
        df, 
        header_format, 
        normal_format, 
        number_format, 
        summary_row_format,
        first_col_border):
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

        total_rows_found = set()
        
        # إعداد ألوان القصات (فقط لورقة تفاصيل القصات)
        cut_colors = {}
        cut_formats = {}
        cut_number_formats = {}
        
        if sheet_name == 'تفاصيل القصات' and 'رقم القصة' in df.columns:
            # استخراج أرقام القصات الفريدة
            cut_col_idx = df.columns.get_loc('رقم القصة')
            unique_cuts = []
            for val in df.iloc[:, cut_col_idx]:
                val_str = str(val).strip()
                if val_str and val_str not in ['', 'nan', 'المجموع'] and val_str not in unique_cuts:
                    unique_cuts.append(val_str)
            
            # توليد ألوان لكل قصة
            num_cuts = len(unique_cuts)
            if num_cuts > 0:
                colors = _generate_readable_colors(num_cuts)
                
                # ربط كل قصة بلون
                for idx, cut_name in enumerate(unique_cuts):
                    bg_color = colors[idx]
                    cut_colors[cut_name] = bg_color
                    
                    # إنشاء format خاص لكل قصة (للنص العادي)
                    cut_formats[cut_name] = writer.book.add_format({
                        'bold': True,
                        'font_size': 10,
                        'font_name': 'Arial',
                        'border': 2,
                        'border_color': '#006400',
                        'bg_color': bg_color,
                        'font_color': '#2C3E50',  # لون نص داكن للقراءة
                        'align': 'center',
                        'valign': 'vcenter'
                    })
                    
                    # إنشاء format للأرقام
                    cut_number_formats[cut_name] = writer.book.add_format({
                        'bold': True,
                        'font_size': 10,
                        'font_name': 'Arial',
                        'border': 2,
                        'border_color': '#006400',
                        'bg_color': bg_color,
                        'font_color': '#2C3E50',
                        'align': 'center',
                        'valign': 'vcenter',
                    })

        for row_num in range(len(df)):
            if row_num in total_rows_found:
                continue

            is_summary = _is_summary_row(df, row_num)
            if is_summary:
                excel_row = row_num + 1
                for col_num in range(len(df.columns)):
                    col_name = df.columns[col_num]
                    cell_value = df.iloc[row_num, col_num]
                    
                    if col_name in numeric_cols:
                        numeric_value = float(cell_value)
                        worksheet.write(excel_row, col_num, numeric_value, summary_row_format)
                    else:
                        worksheet.write(excel_row, col_num, cell_value, summary_row_format)
                
                total_rows_found.add(row_num)
                continue
            
            # تحديد لون القصة الحالية
            current_cut = None
            current_cut_format = normal_format
            current_cut_number_format = number_format
            
            if sheet_name == 'تفاصيل القصات' and 'رقم القصة' in df.columns:
                cut_col_idx = df.columns.get_loc('رقم القصة')
                cut_value = str(df.iloc[row_num, cut_col_idx]).strip()
                if cut_value in cut_formats:
                    current_cut = cut_value
                    current_cut_format = cut_formats[cut_value]
                    current_cut_number_format = cut_number_formats[cut_value]
            
            excel_row = row_num + 1
            num_cols = len(df.columns)
            for col_num in range(num_cols):
                col_name = df.columns[col_num]
                cell_value = df.iloc[row_num, col_num]
                if col_name in numeric_cols:
                    try:
                        numeric_value = float(cell_value)
                        worksheet.write(excel_row, col_num, numeric_value, current_cut_number_format)
                    except (ValueError, TypeError):
                        worksheet.write(excel_row, col_num, cell_value, current_cut_format)
                else:
                    worksheet.write(excel_row, col_num, cell_value, current_cut_format)


        excel_rows = 1 + len(df)
        max_col = len(df.columns)



        for row_num in range(excel_rows):
            for col_num in range(max_col):
                if row_num == 0 or row_num == excel_rows or col_num == 0 or col_num == max_col:
                    if row_num == 0:
                        continue
                    else:
                        if row_num >= 1 and row_num - 1 < len(df):
                            cell_value = df.iloc[row_num - 1, col_num]
                        else:
                            cell_value = ''
                        worksheet.write(row_num, col_num, cell_value, first_col_border)

        add_conditional_formatting(writer, worksheet, df)
        _apply_row_highlight_on_selection(writer, worksheet, df)

    except Exception as e:
        raise


def _convert_dfs_units(dfs: List[pd.DataFrame], unit: str):
    """
    Convert values in DataFrames based on the selected unit.
    cm -> m: divide linear by 100, area by 10000
    """
    linear_factor = 100.0
    area_factor = 10000.0
    
    # Columns representing linear dimensions (cm)
    linear_cols = [
        'العرض', 'الطول', 'الارتفاع', 
        'الطول الاجمالي للسجادة', 'العرض الإجمالي', 
        'الطول الإجمالي المرجعي (التقريبي)', 
        'طول المسار', 'أقصى ارتفاع', 
        'الهادر في العرض', 'اطول مسار'
    ]
    
    # Columns representing area (cm2)
    area_cols = [
        'المساحة الإجمالية', 
        'الإجمالي الأصلي (cm²)', 
        'المستهلك (cm²)', 
        'المتبقي (cm²)',
        'المساحة الكلية للعناصر',
        'قيمة الهادر'
    ]
    
    # Map for renaming columns to reflect new unit
    rename_map = {
        'الإجمالي الأصلي (cm²)': 'الإجمالي الأصلي (m²)',
        'المستهلك (cm²)': 'المستهلك (m²)',
        'المتبقي (cm²)': 'المتبقي (m²)'
    }

    for df in dfs:
        if df.empty:
            continue
            
        # Convert Linear Columns
        for col in linear_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: _safe_convert(x, linear_factor))
                
        # Convert Area Columns
        for col in area_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: _safe_convert(x, area_factor))
        
        # Rename columns
        df.rename(columns=rename_map, inplace=True)


def _safe_convert(val, factor):
    """Safely convert a value by dividing by factor, handling non-numeric values."""
    try:
        if val == "" or val is None:
            return val
        f = float(val)
        return round(f / factor, 2)
    except (ValueError, TypeError):
        return val
