import os
import pandas as pd
from typing import List
from models.data_models import Carpet

def read_input_excel(path: str, sheet_name: int = 0)-> List[Carpet]:
    if not os.path.exists(path):
        raise FileExistsError(f"❌ الملف غير موجود: {path}")
    
    try:
        ext= os.path.splitext(path)[1].lower()
        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine=engine)
    except Exception as e:
        raise Exception(f"فشل في قراءة الملف: {e}")
    
    carpets = []
    invalid_rows = []

    prep_offset = {"A": 8, "B": 6, "C": 1, "D": 3}

    for idx, row in df.iterrows():
        try:
            size_str = str(row[0]).strip()
            qty_raw = int(row[1])
            single_pair = str(row[2]).strip().upper() if len(row) > 2 else ""
            texture_type = str(row[3]).strip().upper() if len(row) > 3 else ""
            prep_code = str(row[4]).strip().upper() if len(row) > 4 else ""

            if "*" not in size_str:
                invalid_rows.append({
                    "size_str": size_str,
                    "qty_raw": qty_raw,
                    "single_pair": single_pair,
                    "texture_type": texture_type,
                    "prep_code": prep_code
                })
                continue

            part1, part2 = size_str.split("*")
            width = int(part1.strip())
            height = int(part2.strip())

            if single_pair in ["A"]:
                qty = max(1 , qty_raw // 2)

            else:
                qty = qty_raw

            if texture_type in ["B"]:
                width, height = height, width

            if prep_code in prep_offset:
                height += prep_offset[prep_code]

            if width <= 0 or height <= 0 or qty <= 0:
                invalid_rows.append(idx + 1)
                continue

            carpet = Carpet(
                id=idx + 1,
                width=width,
                height=height,
                qty=qty,
            )
            carpets.append(carpet)
        except Exception as e:
            invalid_rows.append(idx + 1)
            continue
    
    for item in carpets:
        print(item, "\n")

    return carpets