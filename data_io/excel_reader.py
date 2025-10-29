import os
import pandas as pd
from typing import List
from models.data_models import Carpet


def read_input_excel(path: str, sheet_name: int = 0) -> List[Carpet]:

    if not os.path.exists(path):
        raise FileExistsError(f"❌ الملف غير موجود: {path}")
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx":
            engine = "openpyxl"
        elif ext == ".xls":
            engine = "xlrd"
        else:
            engine = "openpyxl"
        
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine=engine)
        
    except Exception as e:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        except Exception as e2:
            raise Exception(f"فشل في قراءة الملف: {e2}")

    carpets = []
    invalid_rows = []
    for idx, row in df.iterrows():
        try:
            width = int(row[0])    
            height = int(row[1])   
            qty = int(row[2]) 
            if width <= 0 or height <= 0 or qty <= 0:
                invalid_rows.append(idx)
                continue
            
            carpet = Carpet(
                id=idx + 1,  
                width=width,
                height=height,
                qty=qty,
            )
            carpets.append(carpet)
            
        except (ValueError, TypeError, KeyError) as e:
            invalid_rows.append(idx + 1)

            continue
            
    return carpets


def validate_excel_data(carpets: List[Carpet]) -> bool:
    if not carpets:
        return False
        
    invalid_items = []
    for carpet in carpets:
        if carpet.width <= 0 or carpet.height <= 0 or carpet.qty <= 0:
            invalid_items.append(carpet.id)
    
    if invalid_items:
        return False
        
    return True


def get_excel_summary(carpets: List[Carpet]) -> dict:

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
    total_area = sum(carpet.area() * carpet.qty for carpet in carpets)
    
    # إيجاد الأحجام الفريدة
    unique_sizes = len(set((carpet.width, carpet.height) for carpet in carpets))
    
    # نطاقات الأبعاد
    widths = [carpet.width for carpet in carpets]
    heights = [carpet.height for carpet in carpets]
    
    return {
        'total_items': len(carpets),
        'total_quantity': total_quantity,
        'total_area': total_area,
        'unique_sizes': unique_sizes,
        'width_range': (min(widths), max(widths)),
        'length_range': (min(heights), max(heights))
    }
