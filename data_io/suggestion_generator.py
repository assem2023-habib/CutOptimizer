"""
وحدة توليد اقتراحات التشكيل
===========================

هذه الوحدة تحتوي على الدوال المسؤولة عن توليد اقتراحات
لتشكيل مجموعات من البواقي المتاحة.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

from typing import List, Dict, Tuple
from core.models import Rectangle


def generate_partner_suggestions(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[Dict]:
    """
    توليد اقتراحات ذكية لتشكيل مجموعات من البواقي.
    
    هذه الدالة تقترح أفضل التوليفات الممكنة لكل عنصر أساسي
    مع مراعاة الشروط المطلوبة والكميات المتاحة.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض المطلوب
    max_width : int
        الحد الأقصى للعرض المسموح
    tolerance_length : int
        حدود السماحية للفرق في الطول
        
    الإرجاع:
    -------
    List[Dict]
        قائمة من القواميس تحتوي على الاقتراحات التالية:
        - معرف الأساسي: معرف العنصر الأساسي
        - عرض الأساسي: عرض العنصر الأساسي
        - طول الأساسي: طول العنصر الأساسي
        - كمية الأساسي المتبقية: الكمية المتاحة من العنصر الأساسي
        - توصية مختصرة: وصف مختصر للتوصية
        - العرض المقترح الكلي: العرض الإجمالي للمجموعة المقترحة
        - أقصى فرق أطوال داخل التوليفة: أقصى فرق في الأطوال
        - تفصيل التوليفة: تفاصيل العناصر والكميات
        
    أمثلة:
    -------
    >>> suggestions = generate_partner_suggestions(remaining_items, 370, 400, 100)
    >>> for suggestion in suggestions:
    >>>     print(f"العنصر {suggestion['معرف الأساسي']}: {suggestion['توصية مختصرة']}")
    """
    # فهرس العناصر المتاحة حسب العرض
    by_width: Dict[int, List[Rectangle]] = {}
    for r in remaining:
        if r.qty <= 0:
            continue
        by_width.setdefault(r.width, []).append(r)
    
    # ترتيب الأعراض تنازلياً
    all_widths_desc = sorted(by_width.keys(), reverse=True)
    
    def lengths_within(items: List[Tuple[int, int, int]], ref_total: int) -> Tuple[bool, int]:
        """
        فحص ما إذا كانت الأطوال ضمن حدود السماحية.
        
        المعاملات:
        ----------
        items : List[Tuple[int, int, int]]
            قائمة من (الطول, الكمية المستخدمة, معرف العنصر)
        ref_total : int
            الطول المرجعي للمقارنة
            
        الإرجاع:
        -------
        Tuple[bool, int]
            - True إذا كانت الأطوال ضمن الحدود، False إذا لم تكن
            - أقصى فرق في الأطوال
        """
        totals = [l * q for (l, q, _) in items]
        if not totals:
            return True, 0
        
        mx = max(totals)
        mn = min(totals)
        return (mx - mn) <= tolerance_length and all(abs(t - ref_total) <= tolerance_length for t in totals), mx - mn

    suggestions: List[Dict] = []
    
    # توليد الاقتراحات لكل عنصر أساسي
    for primary in remaining:
        if primary.qty <= 0:
            continue
            
        p_w, p_l, p_q = primary.width, primary.length, primary.qty
        ref_total = p_l * p_q
        best_rows: List[Dict] = []
        
        # حالة العنصر المنفرد
        if min_width <= p_w <= max_width:
            best_rows.append({
                'معرف الأساسي': primary.id,
                'عرض الأساسي': p_w,
                'طول الأساسي': p_l,
                'كمية الأساسي المتبقية': p_q,
                'توصية مختصرة': 'يمكن منفرداً',
                'العرض المقترح الكلي': p_w,
                'أقصى فرق أطوال داخل التوليفة': 0,
                'تفصيل التوليفة': f"{primary.id}x1"
            })

        # البحث عن شريك واحد مثالي
        min_rem = max(min_width - p_w, 0)
        max_rem = max_width - p_w
        
        for w in all_widths_desc:
            if w < min_rem or w > max_rem:
                continue
                
            for cand in by_width[w]:
                if cand.id == primary.id:
                    continue
                    
                desired = max(1, int(round(ref_total / cand.length)))
                take = min(desired, cand.qty)
                cand_total = cand.length * take
                diff = abs(cand_total - ref_total)
                
                if diff <= tolerance_length:
                    ok, mx_span = lengths_within([(p_l, p_q, primary.id), (cand.length, take, cand.id)], ref_total)
                    if ok:
                        best_rows.append({
                            'معرف الأساسي': primary.id,
                            'عرض الأساسي': p_w,
                            'طول الأساسي': p_l,
                            'كمية الأساسي المتبقية': p_q,
                            'توصية مختصرة': f"شريك {cand.id} بعدد {take}",
                            'العرض المقترح الكلي': p_w + cand.width,
                            'أقصى فرق أطوال داخل التوليفة': mx_span,
                            'تفصيل التوليفة': f"{primary.id}x{p_q} + {cand.id}x{take}"
                        })

        # البحث عن توليفة متعددة العناصر
        current_width = p_w
        items_combo: List[Tuple[int, int, int, int, int]] = []  # (id, width, length, qty_used, available_after)
        remaining_cap: Dict[int, int] = {r.id: r.qty for r in remaining}
        
        for w in all_widths_desc:
            if current_width >= min_width:
                break
            if current_width + w > max_width:
                continue
                
            for cand in by_width[w]:
                if cand.id == primary.id:
                    continue
                    
                avail = remaining_cap.get(cand.id, 0)
                if avail <= 0:
                    continue
                    
                desired_per_block = max(1, int(round(ref_total / cand.length)))
                
                while avail >= desired_per_block and current_width + w <= max_width and current_width < min_width:
                    cand_total = cand.length * desired_per_block
                    if abs(cand_total - ref_total) > tolerance_length:
                        break
                        
                    items_combo.append((cand.id, cand.width, cand.length, desired_per_block, avail - desired_per_block))
                    avail -= desired_per_block
                    remaining_cap[cand.id] = avail
                    current_width += w
                    
                    if current_width >= min_width:
                        break
                        
        if current_width >= min_width and current_width <= max_width and items_combo:
            ok, mx_span = lengths_within([(p_l, p_q, primary.id)] + [(l, q, _id) for (_id, w, l, q, _) in items_combo], ref_total)
            if ok:
                detail = "+ ".join([f"{primary.id}x{p_q}"] + [f"{_id}x{q}" for (_id, w, l, q, _) in items_combo])
                best_rows.append({
                    'معرف الأساسي': primary.id,
                    'عرض الأساسي': p_w,
                    'طول الأساسي': p_l,
                    'كمية الأساسي المتبقية': p_q,
                    'توصية مختصرة': 'توليفة متعددة الشركاء (جشعة)',
                    'العرض المقترح الكلي': current_width,
                    'أقصى فرق أطوال داخل التوليفة': mx_span,
                    'تفصيل التوليفة': detail
                })

        # إذا لم نجد أي توليفة، قدّم توصية افتراضية
        if not best_rows:
            min_rem = max(min_width - p_w, 0)
            max_rem = max_width - p_w
            best_rows.append({
                'معرف الأساسي': primary.id,
                'عرض الأساسي': p_w,
                'طول الأساسي': p_l,
                'كمية الأساسي المتبقية': p_q,
                'توصية مختصرة': f"وفّر عرض ضمن {min_rem}-{max_rem}",
                'العرض المقترح الكلي': p_w,
                'أقصى فرق أطوال داخل التوليفة': None,
                'تفصيل التوليفة': f"مرشح بطول {p_l} وبعدد ≈ {p_q}"
            })

        # إضافة أفضل الصفوف لهذا العنصر الأساسي
        suggestions.extend(best_rows)

    return suggestions


def analyze_remaining_items(remaining: List[Rectangle]) -> Dict[str, any]:
    """
    تحليل العناصر المتبقية وإعطاء إحصائيات مفيدة.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
        
    الإرجاع:
    -------
    Dict[str, any]
        قاموس يحتوي على الإحصائيات التالية:
        - total_items: إجمالي عدد العناصر
        - total_quantity: إجمالي الكمية
        - total_area: إجمالي المساحة
        - width_distribution: توزيع الأعراض
        - length_distribution: توزيع الأطوال
        - potential_groups: عدد المجموعات المحتملة
    """
    if not remaining:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_area': 0,
            'width_distribution': {},
            'length_distribution': {},
            'potential_groups': 0
        }
    
    # حساب الإحصائيات الأساسية
    total_quantity = sum(r.qty for r in remaining)
    total_area = sum(r.width * r.length * r.qty for r in remaining)
    
    # توزيع الأعراض والأطوال
    width_dist = {}
    length_dist = {}
    
    for r in remaining:
        width_dist[r.width] = width_dist.get(r.width, 0) + r.qty
        length_dist[r.length] = length_dist.get(r.length, 0) + r.qty
    
    # تقدير عدد المجموعات المحتملة
    total_width = sum(r.width * r.qty for r in remaining)
    potential_groups = total_width // 400  # افتراض الحد الأقصى 400
    
    return {
        'total_items': len(remaining),
        'total_quantity': total_quantity,
        'total_area': total_area,
        'width_distribution': width_dist,
        'length_distribution': length_dist,
        'potential_groups': potential_groups
    }


def get_optimization_recommendations(
    remaining: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int
) -> List[str]:
    """
    الحصول على توصيات لتحسين تشكيل المجموعات.
    
    المعاملات:
    ----------
    remaining : List[Rectangle]
        قائمة العناصر المتبقية
    min_width : int
        الحد الأدنى للعرض
    max_width : int
        الحد الأقصى للعرض
    tolerance_length : int
        حدود السماحية للطول
        
    الإرجاع:
    -------
    List[str]
        قائمة من التوصيات النصية
    """
    recommendations = []
    
    # تحليل العناصر المتبقية
    analysis = analyze_remaining_items(remaining)
    
    # توصيات بناءً على التحليل
    if analysis['total_quantity'] == 0:
        recommendations.append("لا توجد عناصر متبقية للتجميع")
        return recommendations
    
    if analysis['potential_groups'] == 0:
        recommendations.append("العناصر المتبقية غير كافية لتشكيل مجموعات")
        return recommendations
    
    # توصيات تحسين العرض
    width_dist = analysis['width_distribution']
    if len(width_dist) > 10:
        recommendations.append("تنويع كبير في الأعراض - قد تحتاج لتجميع أكثر تخصصاً")
    
    # توصيات تحسين الطول
    length_dist = analysis['length_distribution']
    if len(length_dist) > 10:
        recommendations.append("تنويع كبير في الأطوال - قد تحتاج لمرونة أكبر في السماحية")
    
    # توصيات الكمية
    if analysis['total_quantity'] < 5:
        recommendations.append("كمية قليلة من العناصر - قد تحتاج لإضافة المزيد")
    
    return recommendations
