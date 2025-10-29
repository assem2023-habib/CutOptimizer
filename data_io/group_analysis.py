"""
وحدة تحليل المجموعات
=====================

تحتوي على الدوال المتعلقة بتحليل المجموعات، حساب الكفاءة،
وتوليد اقتراحات للتحسين.
"""

from typing import List, Dict, Any
from models.data_models import Rectangle, Group, UsedItem


def calculate_group_efficiency(group: Group) -> Dict[str, float]:
    """
    حساب كفاءة المجموعة بناءً على عدة معايير.
    """
    if not group.items:
        return {
            'width_utilization': 0.0,
            'length_consistency': 0.0,
            'area_efficiency': 0.0,
            'overall_score': 0.0
        }

    # حساب استغلال العرض
    total_width = group.total_width()
    width_utilization = total_width / 400.0  # افتراض الحد الأقصى 400

    # حساب اتساق الأطوال
    lengths = [item.length * item.used_qty for item in group.items]
    if lengths:
        length_variance = max(lengths) - min(lengths)
        length_consistency = max(0, 1 - length_variance / max(lengths))
    else:
        length_consistency = 1.0

    # حساب كفاءة المساحة
    total_area = sum(item.width * item.length * item.used_qty for item in group.items)
    theoretical_max_area = total_width * max(lengths) if lengths else 0
    area_efficiency = total_area / theoretical_max_area if theoretical_max_area > 0 else 0

    # النقاط الإجمالية
    overall_score = (width_utilization + length_consistency + area_efficiency) / 3

    return {
        'width_utilization': width_utilization,
        'length_consistency': length_consistency,
        'area_efficiency': area_efficiency,
        'overall_score': overall_score
    }


def generate_size_suggestions(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[Dict[str, Any]]:
    """
    توليد اقتراحات للمقاسات المطلوبة لتشكيل مجموعات من البواقي
    """
    suggestions = []

    for rect in remaining:
        if rect.qty <= 0:
            continue

        # حساب العرض المطلوب لإكمال المجموعة
        remaining_width_min = min_width - rect.width
        remaining_width_max = max_width - rect.width

        if remaining_width_min <= 0:
            # العنصر يمكن أن يكون وحده في المجموعة
            suggestions.append({
                'type': 'single_item',
                'current_item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'total_length': rect.length * rect.qty,
                'suggestion': f"يمكن استخدام هذا المقاس وحده ({rect.qty} قطعة)",
                'group_width': rect.width,
                'efficiency': 'عالية'
            })
        else:
            # العنصر يحتاج شريك لإكمال المجموعة
            required_width_min = remaining_width_min
            required_width_max = remaining_width_max

            suggestions.append({
                'type': 'needs_partner',
                'current_item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'total_length': rect.length * rect.qty,
                'required_width_range': f"{required_width_min} - {required_width_max}",
                'suggestion': f"يحتاج مقاس بعرض {required_width_min}-{required_width_max}",
                'group_width': f"{rect.width} + {required_width_min}-{required_width_max}",
                'efficiency': 'متوسطة'
            })

    return suggestions


def analyze_remaining_for_optimization(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> Dict[str, Any]:
    """
    تحليل شامل للبواقي لتحديد إمكانيات التحسين
    """
    if not remaining:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'potential_groups': 0,
            'optimization_recommendations': []
        }

    # إحصائيات أساسية
    total_items = len(remaining)
    total_quantity = sum(rect.qty for rect in remaining)
    total_area = sum(rect.width * rect.length * rect.qty for rect in remaining)

    # تحليل إمكانيات التجميع
    potential_groups = 0
    recommendations = []

    for rect in remaining:
        if rect.qty <= 0:
            continue

        # حساب إمكانية التجميع مع العناصر الأخرى
        can_form_group = False

        for other_rect in remaining:
            if other_rect.id == rect.id or other_rect.qty <= 0:
                continue

            combined_width = rect.width + other_rect.width
            if min_width <= combined_width <= max_width:
                # التحقق من تقارب الأطوال
                length_diff = abs(rect.length * rect.qty - other_rect.length * other_rect.qty)
                if length_diff <= tolerance_length:
                    can_form_group = True
                    potential_groups += 1
                    break

        if not can_form_group:
            recommendations.append({
                'item': f"{rect.width}x{rect.length}",
                'quantity': rect.qty,
                'issue': 'صعوبة في التجميع',
                'suggestion': f'يحتاج مقاس بعرض {min_width - rect.width}-{max_width - rect.width}'
            })

    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_area': total_area,
        'potential_groups': potential_groups,
        'optimization_recommendations': recommendations,
        'utilization_potential': (potential_groups / total_items * 100) if total_items > 0 else 0
    }
