import pandas as pd
from xlsxwriter.utility import xl_range

# =============================================================================
# FORMAT CREATION FUNCTIONS - دوال إنشاء التنسيقات
# =============================================================================

def _create_border_format_for_first_column(workbook):
    return workbook.add_format({
        'border': 3,  
        'border_color': '#006400',  
        'bg_color': '#E8F5E8'  
    })

def _create_header_format(workbook):
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

def _create_normal_format(workbook):
    return workbook.add_format({
        'bold': True,
        'font_size': 10,
        'font_name': 'Arial',
        'border': 2,
        'border_color': '#006400',
        'bg_color': '#E8F5E8',
        'font_color': '#006400',
        'align': 'center',
        'valign': 'vcenter'
    })

def _create_number_format(workbook):
    return workbook.add_format({
        'bold': True,
        'font_size': 10,
        'font_name': 'Arial',
        'border': 2,
        'border_color': '#006400',
        'bg_color': '#E8F5E8',
        'font_color': '#006400',
        'align': 'center',
        'valign': 'vcenter',
    })

def _create_summary_row_format(workbook):
    return workbook.add_format({
        'bold': True,
        'font_size': 11,
        'font_name': 'Arial',
        'bg_color': '#C6EFCE',
        'font_color': '#006100',
        'border': 1,
        'border_color': 'black',
        'align': 'center',
    })

# =============================================================================
# CONDITIONAL FORMATTING - التنسيق الشرطي
# =============================================================================

def add_conditional_formatting(writer, worksheet, df: pd.DataFrame) -> None:
    """تمييز الأعمدة مثل الكفاءة بالألوان عند تجاوز القيم 80%."""
    try:
        efficiency_col = None
        for col_num, col_name in enumerate(df.columns):
            if 'كفاءة' in str(col_name):
                efficiency_col = col_num
                break

        if efficiency_col is not None:
            worksheet.conditional_format(2, efficiency_col, len(df) + 1, efficiency_col, {
                'type': 'cell',
                'criteria': '>',
                'value': 80,
                'format': writer.book.add_format({
                    'bg_color': '#C6EFCE',
                    'font_color': '#006100'
                })
            })
    except Exception:
        pass


def _apply_row_highlight_on_selection(writer, worksheet, df):
    """تمييز الصف الذي ينقر عليه المستخدم (تفاعل ديناميكي)."""
    highlight_format = writer.book.add_format({
        'bg_color': '#FFF2CC',  # لون أصفر باهت لتسليط الضوء
    })

    last_row = len(df)
    last_col = len(df.columns) - 1
    cell_range = xl_range(1, 0, last_row, last_col)

    worksheet.conditional_format(cell_range, {
        'type': 'formula',
        'criteria': '=ROW()=CELL("row")',
        'format': highlight_format
    })

# =============================================================================
# HELPER FUNCTION
# =============================================================================

def _is_summary_row(df, row_num):
    """تحقق إذا كان الصف يمثل إجمالي أو مجموع."""
    if row_num >= len(df):
        return False
    
    try:
        val = str(df.iloc[row_num, 0]).strip()
        return val in ['المجموع', 'مجموع', 'الإجمالي', 'إجمالي', 'Total', 'TOTAL']
    except Exception:
        return False