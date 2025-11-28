import pandas as pd
from typing import List, Optional
from models.group_carpet import GroupCarpet
from models.carpet import Carpet


def _waste_sheet_table(
        group_id= '',
        total_width= '',
        waste_width= '',
        max_length_ref= '',
        sum_path_loss= '',
        result= '',
    ):
    return ({
            'رقم القصة': group_id,
            'العرض الإجمالي': total_width,
            'الهادر في العرض':  waste_width,
            'المسار المرجعي': max_length_ref,
            'هادر المسارات': sum_path_loss,
            'نسبة الهدر': result,
        })


def _generate_waste_sheet(
    groups: List[GroupCarpet],
    originals: Optional[List[Carpet]],
    max_width: int,
) -> pd.DataFrame:
    total= 0
    summary = []
    total_width= 0
    total_wasteWidth= 0
    total_pathLoss= 0
    total_maxPath= 0
    total_waste_maxPath= 0
    total_sumPathLoss= 0
    total_result= 0
    group_id= 0

    for c in originals:
        total+= c.area() + c.qty

    for g in groups:
        group_id+= 1
        sumPathLoss= 0
        wasteWidth = max_width - g.total_width()
        
        for item in g.items:
            
            sumPathLoss += (g.max_length_ref() - item.length_ref()) * item.width

        sumPathLoss+= wasteWidth

        result = sumPathLoss * 100 / total
        total_result+= result

        summary.append(
            _waste_sheet_table(
                f'القصة_{group_id}',
                g.total_width(),
                wasteWidth,
                g.max_length_ref(),
                sumPathLoss,
                result
            )
        )

        total_width+= g.total_width()
        total_wasteWidth+= wasteWidth
        total_pathLoss+= sumPathLoss
        total_maxPath+= g.max_length_ref()

    summary.append(
        _waste_sheet_table()
    )
    
    summary.append(
        _waste_sheet_table(
            "المجموع",
            total_width,
            total_wasteWidth,
            total_maxPath,
            total_pathLoss,
            total_result
        )
    )

    df = pd.DataFrame(summary)

    return df
