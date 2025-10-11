"""
وحدة كتابة تقارير إعادة التجميع
===============================

هذه الوحدة مسؤولة عن إنشاء ملف Excel يعرض نتائج عملية تجميع البواقي
بما في ذلك المجموعات المشكلة، العناصر المستخدمة، والكميات المتبقية.
"""

import pandas as pd
from typing import List, Optional
from core.models import Rectangle, Group, UsedItem
from pandas.api.types import is_numeric_dtype
from xlsxwriter.utility import xl_col_to_name


def write_regroup_excel(
    path: str,
    formed_groups: List[Group],
    leftover: List[Rectangle],
    iteration_count: int,
    min_width: int,
    max_width: int,
    tolerance: int
):
    """
    كتابة تقرير تجميع البواقي إلى ملف Excel.
    """
    df_details = _create_regroup_details_sheet(formed_groups)
    df_summary = _create_regroup_summary_sheet(formed_groups)
    df_leftover = _create_leftover_sheet(leftover)
    df_settings = _create_settings_sheet(iteration_count, min_width, max_width, tolerance)

    _write_all_sheets_to_excel(path, df_details, df_summary, df_leftover, df_settings)


def _create_regroup_details_sheet(groups: List[Group]) -> pd.DataFrame:
    """ورقة التفاصيل — تعرض كل مجموعة وما تحتويه."""
    rows = []
    for g in groups:
        for it in g.items:
            rows.append({
                "رقم المجموعة": f"مجموعة_{g.id}",
                "معرف السجادة": it.rect_id,
                "العرض": it.width,
                "الطول": it.length,
                "الكمية المستخدمة": it.used_qty,
                "الكمية الأصلية": it.original_qty,
            })
    
    # إنشاء DataFrame
    df = pd.DataFrame(rows)
    
    # إضافة سطر فارغ ثم سطر المجموع
    if not df.empty:
        # سطر فارغ
        empty_row = {col: '' for col in df.columns}
        df = pd.concat([df, pd.DataFrame([empty_row])], ignore_index=True)
        
        # سطر المجموع
        totals_row = {}
        for col in df.columns:
            if col in ['العرض', 'الطول', 'الكمية المستخدمة', 'الكمية الأصلية']:
                # حساب المجموع للأعمدة الرقمية فقط
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                totals_row[col] = numeric_data.sum()
            else:
                totals_row[col] = 'المجموع'
        
        df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
    
    return df


def _create_regroup_summary_sheet(groups: List[Group]) -> pd.DataFrame:
    """ورقة ملخص المجموعات."""
    summary = []
    for g in groups:
        summary.append({
            "رقم المجموعة": f"مجموعة_{g.id}",
            "عدد العناصر": len(g.items),
            "العرض الإجمالي": g.total_width(),
            "الطول المرجعي": g.ref_length(),
            "المساحة الإجمالية": g.total_area()
        })
    
    # إنشاء DataFrame
    df = pd.DataFrame(summary)
    
    # إضافة سطر فارغ ثم سطر المجموع
    if not df.empty:
        # سطر فارغ
        empty_row = {col: '' for col in df.columns}
        df = pd.concat([df, pd.DataFrame([empty_row])], ignore_index=True)
        
        # سطر المجموع
        totals_row = {}
        for col in df.columns:
            if col in ['عدد العناصر', 'العرض الإجمالي', 'الطول المرجعي', 'المساحة الإجمالية']:
                # حساب المجموع للأعمدة الرقمية فقط
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                totals_row[col] = numeric_data.sum()
            else:
                totals_row[col] = 'المجموع'
        
        df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
    
    return df


def _create_leftover_sheet(remaining: List[Rectangle]) -> pd.DataFrame:
    """ورقة البواقي المتبقية."""
    rows = []
    for r in remaining:
        rows.append({
            "معرف السجادة": r.id,
            "العرض": r.width,
            "الطول": r.length,
            "الكمية المتبقية": r.qty
        })
    
    # إنشاء DataFrame
    df = pd.DataFrame(rows)
    
    # إضافة سطر فارغ ثم سطر المجموع
    if not df.empty:
        # سطر فارغ
        empty_row = {col: '' for col in df.columns}
        df = pd.concat([df, pd.DataFrame([empty_row])], ignore_index=True)
        
        # سطر المجموع
        totals_row = {}
        for col in df.columns:
            if col in ['العرض', 'الطول', 'الكمية المتبقية']:
                # حساب المجموع للأعمدة الرقمية فقط
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                totals_row[col] = numeric_data.sum()
            else:
                totals_row[col] = 'المجموع'
        
        df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
    
    return df


def _create_settings_sheet(iter_count: int, min_width: int, max_width: int, tol: int) -> pd.DataFrame:
    """ورقة إعدادات العملية."""
    data = {
        "عدد الجولات": [iter_count],
        "الحد الأدنى للعرض": [min_width],
        "الحد الأقصى للعرض": [max_width],
        "سماحية الطول": [tol],
    }
    
    # إنشاء DataFrame
    df = pd.DataFrame(data)
    
    # إضافة سطر فارغ ثم سطر المجموع
    if not df.empty:
        # سطر فارغ
        empty_row = {col: '' for col in df.columns}
        df = pd.concat([df, pd.DataFrame([empty_row])], ignore_index=True)
        
        # سطر المجموع
        totals_row = {}
        for col in df.columns:
            if col in ['عدد الجولات', 'الحد الأدنى للعرض', 'الحد الأقصى للعرض', 'سماحية الطول']:
                # حساب المجموع للأعمدة الرقمية فقط
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                totals_row[col] = numeric_data.sum()
            else:
                totals_row[col] = 'المجموع'
        
        df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
    
    return df


def _write_all_sheets_to_excel(path, df1, df2, df3, df4):
    """كتابة جميع الأوراق إلى ملف Excel."""
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df1.to_excel(writer, sheet_name="تفاصيل التجميع", index=False)
        df2.to_excel(writer, sheet_name="ملخص التجميع", index=False)
        df3.to_excel(writer, sheet_name="البواقي المتبقية", index=False)
        df4.to_excel(writer, sheet_name="إعدادات العملية", index=False)
