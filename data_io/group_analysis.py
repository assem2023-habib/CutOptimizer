"""
وحدة تحليل المجموعات
=====================

تحتوي على الدوال المتعلقة بتحليل المجموعات، حساب الكفاءة،
وتوليد اقتراحات للتحسين.
"""

from typing import List, Dict, Any
from models.data_models import Carpet, CarpetUsed, GroupCarpet


def calculate_group_efficiency(group: GroupCarpet, max_width: int = 400) -> Dict[str, float]:
    """
    حساب كفاءة المجموعة بناءً على عدة معايير.
    
    المعاملات:
    ----------
    group : GroupCarpet
        المجموعة المراد تحليلها
    max_width : int
        الحد الأقصى للعرض (افتراضي: 400)
        
    الإرجاع:
    -------
    Dict[str, float]
        قاموس يحتوي على مؤشرات الكفاءة:
        - width_utilization: استغلال العرض (0-1)
        - height_consistency: اتساق الارتفاعات (0-1)
        - area_efficiency: كفاءة المساحة (0-1)
        - quantity_balance: توازن الكميات (0-1)
        - overall_score: النقاط الإجمالية (0-1)
        
    أمثلة:
    -------
    >>> efficiency = calculate_group_efficiency(group, 400)
    >>> print(f"الكفاءة الإجمالية: {efficiency['overall_score']*100:.1f}%")
    """
    if not group.items:
        return {
            'width_utilization': 0.0,
            'height_consistency': 0.0,
            'area_efficiency': 0.0,
            'quantity_balance': 0.0,
            'overall_score': 0.0
        }

    # حساب استغلال العرض
    total_width = group.total_width()
    width_utilization = min(total_width / max_width, 1.0)

    # 2️⃣ حساب اتساق الارتفاعات (tolerance)
    # نستخدم length_ref() لكل عنصر = height × qty_used
    ref_lengths = [item.length_ref() for item in group.items]
    if ref_lengths and len(ref_lengths) > 1:
        avg_ref_length = sum(ref_lengths) / len(ref_lengths)
        # حساب الانحراف المعياري النسبي
        variance = sum((rl - avg_ref_length) ** 2 for rl in ref_lengths) / len(ref_lengths)
        std_dev = variance ** 0.5
        # تحويل إلى نسبة اتساق (كلما قلت الانحراف، زاد الاتساق)
        height_consistency = max(0, 1 - (std_dev / avg_ref_length)) if avg_ref_length > 0 else 1.0
    else:
        height_consistency = 1.0

    # حساب كفاءة المساحة
    total_area = group.total_area()
    theoretical_max_area = total_width * group.total_area()
    area_efficiency = total_area / theoretical_max_area if theoretical_max_area > 0 else 0

    # 4️⃣ حساب توازن الكميات
    # كلما كانت الكميات متقاربة، كان التوازن أفضل
    quantities = [item.qty_used for item in group.items]
    if quantities and len(quantities) > 1:
        avg_qty = sum(quantities) / len(quantities)
        qty_variance = sum((q - avg_qty) ** 2 for q in quantities) / len(quantities)
        qty_std_dev = qty_variance ** 0.5
        quantity_balance = max(0, 1 - (qty_std_dev / avg_qty)) if avg_qty > 0 else 1.0
    else:
        quantity_balance = 1.0

    # النقاط الإجمالية
    overall_score = (
        width_utilization * 0.3 +      # 30% للعرض
        height_consistency * 0.4 +     # 40% للاتساق (أهم معيار)
        area_efficiency * 0.2 +        # 20% للمساحة
        quantity_balance * 0.1         # 10% للتوازن
    )

    return {
        'width_utilization': round(width_utilization, 3),
        'height_consistency': round(height_consistency, 3),
        'area_efficiency': round(area_efficiency, 3),
        'quantity_balance': round(quantity_balance, 3),
        'overall_score': round(overall_score, 3)
    }

def analyze_groups_quality(
    groups: List[GroupCarpet],
    max_width: int = 400
)->Dict[str, Any]:
    """
    تحليل جودة جميع المجموعات.
    
    المعاملات:
    ----------
    groups : List[GroupCarpet]
        قائمة المجموعات
    max_width : int
        الحد الأقصى للعرض
        
    الإرجاع:
    -------
    Dict[str, Any]
        تحليل شامل لجودة المجموعات
        
    أمثلة:
    -------
    >>> quality = analyze_groups_quality(groups, 400)
    >>> print(f"متوسط الكفاءة: {quality['average_efficiency']*100:.1f}%")
    """
    if not groups:
        return {
            'total_groups': 0,
            'average_efficiency': 0.0,
            'excellent_groups': 0,
            'good_groups': 0,
            'poor_groups': 0,
            'best_group': None,
            'worst_group': None,
            'efficiency_distribution': {}
        }
    # حساب كفاءة كل مجموعة
    efficiencies = []
    for group in groups:
        eff = calculate_group_efficiency(group, max_width)
        efficiencies.append({
            'group_id': group.group_id,
            'score': eff['overall_score'],
            'details': eff
        })
    # التصنيف
    excellent = sum(1 for e in efficiencies if e['score'] >= 0.8)
    good = sum(1 for e in efficiencies if 0.6 <= e['score'] < 0.8)
    poor = sum(1 for e in efficiencies if e['score'] < 0.6)

    # أفضل وأسوأ مجموعة
    best = max(efficiencies, key=lambda x: x['score']) if efficiencies else None
    worst = min(efficiencies, key=lambda x: x['score']) if efficiencies else None

    # متوسط الكفاءة
    avg_efficiency = sum(e['score'] for e in efficiencies) / len(efficiencies)

    return {
        'total_groups': len(groups),
        'average_efficiency': round(avg_efficiency, 3),
        'excellent_groups': excellent,  # ≥ 80%
        'good_groups': good,            # 60-79%
        'poor_groups': poor,            # < 60%
        'best_group': best,
        'worst_group': worst,
        'efficiency_distribution': {
            'excellent': excellent,
            'good': good,
            'poor': poor
        },
        'all_efficiencies': efficiencies
    }



def analyze_remaining_for_optimization(
    remaining: List[Carpet],
    min_width: int,
    max_width: int,
    tolerance_length: int = 0
) -> Dict[str, Any]:
    """
    تحليل شامل للمتبقيات لتحديد إمكانيات التحسين.
    
    المعاملات:
    ----------
    remaining : List[Carpet]
        قائمة السجاد المتبقي
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        السماحية للطول (افتراضي: 100)
        
    الإرجاع:
    -------
    Dict[str, Any]
        تحليل شامل مع توصيات
        
    أمثلة:
    -------
    >>> analysis = analyze_remaining_for_optimization(remaining, 370, 400)
    >>> print(f"إمكانية التحسين: {analysis['utilization_potential']:.1f}%")
    """
    if not remaining:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'potential_groups': 0,
            'optimization_recommendations': [],
            'utilization_potential': 0.0,
            'critical_items': []
        }
    remaining_items = [r for r in remaining if r.rem_qty > 0]

    if not remaining_items:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'potential_groups': 0,
            'optimization_recommendations': [],
            'utilization_potential': 0.0,
            'critical_items': []
        }

    # إحصائيات أساسية
    total_items = len(remaining_items)
    total_quantity = sum(r.rem_qty for r in remaining_items)
    total_area = sum(r.width * r.height * r.rem_qty for r in remaining_items)

    # تحليل إمكانيات التجميع
    potential_groups = 0
    recommendations = []
    critical_items = []

    for rect in remaining_items:
        if rect.rem_qty <= 0:
            continue

        # حساب إمكانية التجميع
        can_form_group = False
        potential_partners = []

        for other_rect in remaining_items:
            if other_rect.id == rect.id or other_rect.rem_qty <= 0:
                continue

            combined_width = rect.width + other_rect.width
            
            if min_width <= combined_width <= max_width:
                # التحقق من تقارب الأطوال
                ref1 = rect.height * rect.rem_qty
                ref2 = other_rect.height * other_rect.rem_qty
                length_diff = abs(ref1 - ref2)
                
                if length_diff <= tolerance_length:
                    can_form_group = True
                    potential_partners.append({
                        'id': other_rect.id,
                        'size': f"{other_rect.width}x{other_rect.height}",
                        'qty': other_rect.rem_qty,
                        'combined_width': combined_width
                    })

        if can_form_group:
            potential_groups += 1
            recommendations.append({
                'item': f"Carpet {rect.id} ({rect.width}x{rect.height})",
                'quantity': rect.rem_qty,
                'status': '✅ يمكن تجميعه',
                'partners': potential_partners[:3],  # أفضل 3 شركاء
                'suggestion': f'يمكن دمجه مع {len(potential_partners)} عنصر آخر'
            })
        else:
            # عنصر صعب التجميع
            critical_items.append({
                'id': rect.id,
                'size': f"{rect.width}x{rect.height}",
                'quantity': rect.rem_qty,
                'area': rect.width * rect.height * rect.rem_qty
            })
            
            recommendations.append({
                'item': f"Carpet {rect.id} ({rect.width}x{rect.height})",
                'quantity': rect.rem_qty,
                'status': '⚠️ صعوبة في التجميع',
                'partners': [],
                'suggestion': f'يحتاج مقاس بعرض {min_width - rect.width}-{max_width - rect.width} cm'
            })

    # حساب إمكانية الاستغلال
    utilization_potential = (potential_groups / total_items * 100) if total_items > 0 else 0

    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_area': total_area,
        'potential_groups': potential_groups,
        'optimization_recommendations': recommendations,
        'utilization_potential': round(utilization_potential, 2),
        'critical_items': critical_items,
        'summary': {
            'can_be_grouped': potential_groups,
            'difficult_to_group': len(critical_items),
            'grouping_rate': f"{utilization_potential:.1f}%"
        }
    }


def generate_grouping_suggestions(
    remaining: List[Carpet],
    min_width: int,
    max_width: int,
    tolerance_length: int = 100,
    max_suggestions: int = 10
) -> List[Dict[str, Any]]:
    """
    توليد اقتراحات محددة لتشكيل مجموعات من المتبقيات.
    
    المعاملات:
    ----------
    remaining : List[Carpet]
        المتبقيات
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        السماحية
    max_suggestions : int
        الحد الأقصى للاقتراحات
        
    الإرجاع:
    -------
    List[Dict[str, Any]]
        قائمة الاقتراحات
        
    أمثلة:
    -------
    >>> suggestions = generate_grouping_suggestions(remaining, 370, 400)
    >>> for s in suggestions[:3]:
    >>>     print(f"اقتراح {s['id']}: {s['description']}")
    """
    suggestions = []
    remaining_items = [r for r in remaining if r.rem_qty > 0]
    
    suggestion_id = 1
    
    for i, main in enumerate(remaining_items):
        if len(suggestions) >= max_suggestions:
            break
            
        for j, partner in enumerate(remaining_items[i+1:], start=i+1):
            if len(suggestions) >= max_suggestions:
                break
            
            combined_width = main.width + partner.width
            
            if min_width <= combined_width <= max_width:
                ref1 = main.height * main.rem_qty
                ref2 = partner.height * partner.rem_qty
                diff = abs(ref1 - ref2)
                
                if diff <= tolerance_length:
                    efficiency = (combined_width / max_width) * 100
                    
                    suggestions.append({
                        'id': suggestion_id,
                        'main': {
                            'carpet_id': main.id,
                            'size': f"{main.width}x{main.height}",
                            'qty': main.rem_qty
                        },
                        'partner': {
                            'carpet_id': partner.id,
                            'size': f"{partner.width}x{partner.height}",
                            'qty': partner.rem_qty
                        },
                        'combined_width': combined_width,
                        'tolerance_diff': diff,
                        'efficiency': round(efficiency, 2),
                        'description': f"دمج Carpet {main.id} مع Carpet {partner.id}",
                        'quality': '⭐⭐⭐' if efficiency >= 90 else '⭐⭐' if efficiency >= 75 else '⭐'
                    })
                    
                    suggestion_id += 1
    
    # ترتيب حسب الكفاءة
    suggestions.sort(key=lambda x: x['efficiency'], reverse=True)
    
    return suggestions
