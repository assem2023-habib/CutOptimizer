import pandas as pd
from typing import List
from models.group_carpet import GroupCarpet


def _waste_sheet_table(
        group_id= '',
        total_width= '',
        waste_width= '',
        max_length_ref= '',
        result_1= '',
        path_loss= '',
        result_2= '',
        sum_path_loss= '',
    ):
    return ({
            'رقم القصة': group_id,
            'العرض الإجمالي': total_width,
            'الهادر في العرض':  waste_width,
            'اطول مسار': max_length_ref,
            'نتيجة الضرب': result_1,
            'الهادر في المسارات': path_loss,
            'نتيجة الجمع': result_2,
            'مجموع هادرالمسارات في المجموعة': sum_path_loss,
        })


def _generate_waste_sheet(
    groups: List[GroupCarpet],
    max_width: int,
) -> pd.DataFrame:
    
    summary = []
    total_width= 0
    total_wasteWidth= 0
    total_pathLoss= 0
    total_maxPath= 0
    total_waste_maxPath= 0
    total_sumPathLoss= 0
    total_result= 0
    group_id= 0

    for g in groups:
        group_id+= 1
        sumPathLoss= 0

        for item in g.items:
            sumPathLoss += g.max_length_ref() - item.length_ref()

        wasteWidth = max_width - g.total_width()
        pathLoss = g.max_length_ref() - g.min_length_ref()

        summary.append({
            'رقم القصة': f'القصة_{group_id}',
            'العرض الإجمالي': g.total_width(),
            'الهادر في العرض':  wasteWidth,
            'اطول مسار': g.max_length_ref(),
            'نتيجة الضرب': wasteWidth * g.max_length_ref(),
            'الهادر في المسارات': pathLoss,
            'نتيجة الجمع': wasteWidth * g.max_length_ref() + pathLoss,
            'مجموع هادرالمسارات في المجموعة': sumPathLoss,
        })

        total_width+= g.total_width()
        total_wasteWidth+= wasteWidth
        total_waste_maxPath+= wasteWidth * g.max_length_ref()
        total_pathLoss+= pathLoss
        total_sumPathLoss+= sumPathLoss
        total_result+= pathLoss * wasteWidth
        total_maxPath+= g.max_length_ref()

    summary.append({
        'رقم القصة': '',
        'العرض الإجمالي': '',
        'الهادر في العرض':  '',
        'اطول مسار': '',
        'نتيجة الضرب': '',
        'الهادر في المسارات': '',
        'نتيجة الجمع':'',
        'مجموع هادرالمسارات في المجموعة': '',
    })
    
    summary.append({
        'رقم القصة': "المجموع",
        'العرض الإجمالي': total_width,
        'الهادر في العرض':  total_wasteWidth,
        'اطول مسار': total_maxPath,
        'نتيجة الضرب': total_waste_maxPath,
        'الهادر في المسارات': total_pathLoss,
        'نتيجة الجمع': total_result,
        'مجموع هادرالمسارات في المجموعة': total_sumPathLoss,
    })

    df = pd.DataFrame(summary)

    return df
