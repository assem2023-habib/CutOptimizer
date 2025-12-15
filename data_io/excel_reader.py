import os
import pandas as pd
from typing import List
from models.data_models import Carpet
from core.config.config_manager import ConfigManager

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
    
    # Get pair_mode from config (set from Processing Configuration)
    pair_mode = str(ConfigManager.get_value("pair_mode", "B")).upper()

    for idx, row in df.iterrows():
        try:
            client_order = int(row[0])
            width = int(str(row[1]).strip())
            height = int(str(row[2]).strip())
            qty_raw = int(row[3])
            # Determine texture/prep columns based on new format (no A/B column)
            if len(row) > 6:
                # Legacy format with extra A/B column present at index 4
                texture_type = str(row[5]).strip().upper()
                prep_code = str(row[6]).strip().upper()
            else:
                texture_type = str(row[4]).strip().upper() if len(row) > 4 else ""
                prep_code = str(row[5]).strip().upper() if len(row) > 5 else ""

            # Apply pair_mode to quantity
            if pair_mode == "A":
                qty = max(1, qty_raw // 2)
            else:
                qty = qty_raw

            if prep_code in prep_offset:
                height += prep_offset[prep_code]

            if texture_type == "B":
                width, height = height, width
                
            if width <= 0 or height <= 0 or qty <= 0:
                invalid_rows.append(idx + 1)
                continue

            carpet = Carpet(
                id=idx + 1,
                width=width,
                height=height,
                qty=qty,
                client_order=client_order
            )
            carpet.qty_original_before_pair_mode = qty_raw
            carpets.append(carpet)
        except Exception as e:
            invalid_rows.append(idx + 1)
            continue

    return carpets
