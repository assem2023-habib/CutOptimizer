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
            width_height = int(row[0])    
            qty = int(row[1])   
            is_even = int(row[2]) 
            type_car = int(row[3]) 
            code = int(row[4]) 
            
            carpet = {
                "width_height": width_height,
                "qty": qty,
                "is_even": is_even,
                "type_car": type_car,
                "code": code
            }
            carpets.append(carpet)
            print(carpet, "\n")
        except (ValueError, TypeError, KeyError) as e:
            invalid_rows.append(idx + 1)

            continue