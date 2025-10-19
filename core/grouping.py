from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from .models import Rectangle, UsedItem, Group
import time


def group_carpets_greedy(carpets: List[Rectangle],
                         min_width: int,
                         max_width: int,
                         tolerance_length: int,  # قيمة السماحية المطلقة (مثلاً 20 سم)
                         start_with_largest: bool = True,
                         start_group_id: int = 1
                         ) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية جشعة محسّنة لتجميع السجاد:
    
    الاستراتيجية:
    1. تشكيل مجموعات ثنائية (عنصرين مختلفين) مع أعظم كمية ممكنة
    2. استغلال العرض للعناصر المتبقية
    3. زيادة عدد العناصر (3، 4، ...) عند الحاجة
    4. التكرار الذكي لملء العرض (نفس العنصر عدة مرات)
    5. منع تكرار المجموعات المتطابقة
    
    الأولوية: العرض أولاً، ثم الكمية
    
    ملاحظة: الطول المرجعي يُحسب ديناميكياً لكل مجموعة من العنصر الأول
              السماحية هي قيمة مطلقة ثابتة لجميع المجموعات
    """
    
    # ترتيب حسب العرض والطول
    carpets_sorted = sorted(carpets, key=lambda r: (r.width, r.length), reverse=start_with_largest)
    id_map = {r.id: r for r in carpets_sorted}
    original_qty_map: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}
    remaining_qty: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}
    
    # خريطة العروض
    widths_map = defaultdict(list)
    for r in carpets_sorted:
        widths_map[r.width].append(r.id)
    
    groups: List[Group] = []
    group_id = start_group_id
    
    # لتتبع المجموعات المستخدمة (منع التكرار)
    used_group_signatures: Set[str] = set()
    
    def get_group_signature(items: List[UsedItem]) -> str:
        """إنشاء توقيع فريد للمجموعة لمنع التكرار"""
        sorted_items = sorted(items, key=lambda x: (x.rect_id, x.width, x.length, x.used_qty))
        return "|".join([f"{it.rect_id}:{it.width}:{it.length}:{it.used_qty}" for it in sorted_items])
    
    def calculate_tolerance(ref_length_value: int) -> int:
        """إرجاع السماحية المطلقة الثابتة"""
        return tolerance_length
    
    def find_best_qty_pair(rect1: Rectangle, rect2: Rectangle, 
                          avail1: int, avail2: int) -> Tuple[int, int]:
        """
        إيجاد أعظم كمية ممكنة للزوج تحقق شرط tolerance
        الطول المرجعي = length1 * qty1
        الشرط: abs((length1 * qty1) - (length2 * qty2)) <= tolerance
        """
        best_qty1, best_qty2 = 0, 0
        best_total_qty = 0
        
        # نبدأ من أعظم كمية ممكنة
        max_qty1 = min(avail1, max_width // rect1.width) if rect1.width > 0 else avail1
        
        for qty1 in range(max_qty1, 0, -1):
            ref_length_value = rect1.length * qty1  # الطول المرجعي
            tolerance = calculate_tolerance(ref_length_value)
            
            # حساب الكمية المثالية للشريك
            if rect2.length > 0:
                ideal_qty2 = ref_length_value / rect2.length
                
                # تجربة كميات حول القيمة المثالية
                search_range = max(3, int(ideal_qty2 * 0.2))  # نطاق بحث 20%
                for qty2 in range(max(1, int(ideal_qty2 - search_range)), 
                                 min(avail2, int(ideal_qty2 + search_range) + 1)):
                    if qty2 <= 0 or qty2 > avail2:
                        continue
                    
                    tolerance_ref2 = rect2.length * qty2
                    diff = abs(ref_length_value - tolerance_ref2)
                    
                    if diff <= tolerance:
                        # تحقق من العرض
                        total_w = rect1.width + rect2.width
                        if min_width <= total_w <= max_width:
                            total_qty = qty1 + qty2
                            if total_qty > best_total_qty:
                                best_qty1, best_qty2 = qty1, qty2
                                best_total_qty = total_qty
        
        return best_qty1, best_qty2
    
    # ============================================
    # المرحلة 1: تشكيل مجموعات ثنائية
    # ============================================
    print("المرحلة 1: تشكيل مجموعات ثنائية...")
    
    safety_counter = 0
    max_iterations = 5000
    
    while safety_counter < max_iterations:
        safety_counter += 1
        group_created = False
        
        # اختيار عنصر أساسي
        primary = None
        for r in carpets_sorted:
            if remaining_qty.get(r.id, 0) > 0 and r.width <= max_width:
                primary = r
                break
        
        if primary is None:
            break
        
        primary_avail = remaining_qty[primary.id]
        
        # البحث عن شريك من الأعرض
        candidate_widths = sorted([w for w in widths_map.keys() 
                                  if w <= max_width - primary.width], reverse=True)
        
        best_partner = None
        best_qty_primary, best_qty_cand = 0, 0
        
        for cand_width in candidate_widths:
            for cand_id in widths_map[cand_width]:
                if cand_id == primary.id:
                    continue
                
                cand_avail = remaining_qty.get(cand_id, 0)
                if cand_avail <= 0:
                    continue
                
                cand = id_map[cand_id]
                
                # إيجاد أعظم كمية ممكنة
                qty_primary, qty_cand = find_best_qty_pair(
                    primary, cand, primary_avail, cand_avail
                )
                
                if qty_primary > 0 and qty_cand > 0:
                    if qty_primary + qty_cand > best_qty_primary + best_qty_cand:
                        best_partner = cand_id
                        best_qty_primary = qty_primary
                        best_qty_cand = qty_cand
        
        if best_partner is not None:
            cand = id_map[best_partner]
            
            # إنشاء المجموعة
            items = [
                UsedItem(primary.id, primary.width, primary.length, best_qty_primary, original_qty_map[primary.id]),
                UsedItem(best_partner, cand.width, cand.length, best_qty_cand, original_qty_map[best_partner])
            ]
            
            signature = get_group_signature(items)
            if signature not in used_group_signatures:
                # خصم الكميات
                remaining_qty[primary.id] -= best_qty_primary
                remaining_qty[best_partner] -= best_qty_cand
                
                groups.append(Group(group_id, items))
                used_group_signatures.add(signature)
                group_id += 1
                group_created = True
        
        if not group_created:
            # لم نجد شريكاً، نزيل العنصر مؤقتاً
            remaining_qty[primary.id] = 0
    
    # إعادة الكميات المتبقية الفعلية
    remaining_qty = {r.id: r.qty for r in carpets_sorted}
    for group in groups:
        for item in group.items:
            remaining_qty[item.rect_id] -= item.used_qty
    
    print(f"تم تشكيل {len(groups)} مجموعة ثنائية")
    
    # ============================================
    # المرحلة 2: استغلال العرض للمتبقيات
    # ============================================
    print("المرحلة 2: استغلال العرض للمتبقيات...")
    
    iteration = 0
    max_iterations_phase2 = 1000
    
    while iteration < max_iterations_phase2:
        iteration += 1
        group_created = False
        
        # اختيار عنصر أساسي
        primary = None
        for r in carpets_sorted:
            if remaining_qty.get(r.id, 0) > 0 and r.width <= max_width:
                primary = r
                break
        
        if primary is None:
            break
        
        primary_avail = remaining_qty[primary.id]
        best_combination = None
        best_width_utilization = 0
        
        # محاولة بناء مجموعة تستغل العرض الأقصى
        max_primary_qty = min(primary_avail, max_width // primary.width) if primary.width > 0 else primary_avail
        
        for use_primary in range(max_primary_qty, 0, -1):
            ref_length_value = primary.length * use_primary  # الطول المرجعي للمجموعة
            tolerance = calculate_tolerance(ref_length_value)
            
            current_items = [UsedItem(primary.id, primary.width, primary.length, use_primary, original_qty_map[primary.id])]
            current_width = primary.width
            temp_qty = dict(remaining_qty)
            temp_qty[primary.id] -= use_primary
            
            # البحث عن شركاء لملء العرض
            partners_added = True
            max_partners = 10  # حد أقصى للشركاء
            
            while partners_added and current_width < max_width and len(current_items) < max_partners:
                partners_added = False
                
                # البحث عن أفضل شريك
                best_partner = None
                best_partner_width_gain = 0
                best_partner_qty = 0
                
                for cand_id, cand_qty in temp_qty.items():
                    if cand_qty <= 0:
                        continue
                    
                    cand = id_map[cand_id]
                    
                    if cand.width > max_width - current_width:
                        continue
                    
                    # حساب الكمية المثالية
                    if cand.length <= 0:
                        continue
                    
                    ideal_qty = ref_length_value / cand.length
                    search_range = max(3, int(ideal_qty * 0.2))
                    
                    for qty in range(max(1, int(ideal_qty - search_range)), 
                                    min(int(ideal_qty + search_range) + 1, cand_qty + 1)):
                        if qty <= 0 or qty > cand_qty:
                            continue
                        
                        tolerance_ref_cand = cand.length * qty
                        diff = abs(tolerance_ref_cand - ref_length_value)
                        
                        if diff <= tolerance:
                            new_width = current_width + cand.width
                            if new_width <= max_width:
                                width_gain = cand.width
                                if width_gain > best_partner_width_gain:
                                    best_partner = cand_id
                                    best_partner_width_gain = width_gain
                                    best_partner_qty = qty
                                break
                
                if best_partner:
                    cand = id_map[best_partner]
                    current_items.append(UsedItem(best_partner, cand.width, cand.length, best_partner_qty, original_qty_map[best_partner]))
                    current_width += cand.width
                    temp_qty[best_partner] -= best_partner_qty
                    partners_added = True
            
            # تقييم التركيبة - يجب أن تحتوي على عنصرين مختلفين على الأقل
            unique_ids = set(it.rect_id for it in current_items)
            if min_width <= current_width <= max_width and len(unique_ids) >= 2:
                width_utilization = current_width / max_width
                if width_utilization > best_width_utilization:
                    best_width_utilization = width_utilization
                    best_combination = (current_items, temp_qty)
        
        # إضافة أفضل مجموعة
        if best_combination:
            items, temp_qty = best_combination
            signature = get_group_signature(items)
            
            if signature not in used_group_signatures:
                for item in items:
                    remaining_qty[item.rect_id] -= item.used_qty
                
                groups.append(Group(group_id, items))
                used_group_signatures.add(signature)
                group_id += 1
                group_created = True
        
        if not group_created:
            # لم نستطع تشكيل مجموعة
            remaining_qty[primary.id] = 0
    
    # إعادة حساب الكميات المتبقية
    remaining_qty = {r.id: r.qty for r in carpets_sorted}
    for group in groups:
        for item in group.items:
            remaining_qty[item.rect_id] -= item.used_qty
    
    print(f"إجمالي المجموعات بعد المرحلة 2: {len(groups)}")
    
    # ============================================
    # المرحلة 3: التكرار الذكي لملء العرض
    # ============================================
    print("المرحلة 3: التكرار الذكي...")
    
    for r in carpets_sorted:
        avail = remaining_qty.get(r.id, 0)
        if avail <= 0 or r.width <= 0:
            continue
        
        # محاولة تكرار العنصر لملء العرض
        max_repeats = min(avail, max_width // r.width)
        
        for num_repeats in range(max_repeats, 1, -1):
            total_w = r.width * num_repeats
            
            if min_width <= total_w <= max_width:
                # توزيع الكمية على التكرارات بشكل متساوٍ قدر الإمكان
                items = []
                remaining_for_repeat = avail
                qty_per_repeat = max(1, avail // num_repeats)
                
                # الطول المرجعي = length * qty_per_repeat
                ref_length_value = r.length * qty_per_repeat
                tolerance = calculate_tolerance(ref_length_value)
                
                valid_repeat = True
                for i in range(num_repeats):
                    if remaining_for_repeat <= 0:
                        valid_repeat = False
                        break
                    
                    qty_this_repeat = min(qty_per_repeat, remaining_for_repeat)
                    
                    # التحقق من tolerance بين التكرارات
                    tolerance_ref_this = r.length * qty_this_repeat
                    if abs(tolerance_ref_this - ref_length_value) > tolerance:
                        # نحاول تعديل الكمية
                        ideal_qty = ref_length_value / r.length if r.length > 0 else qty_this_repeat
                        qty_this_repeat = max(1, min(int(round(ideal_qty)), remaining_for_repeat))
                        tolerance_ref_this = r.length * qty_this_repeat
                        
                        if abs(tolerance_ref_this - ref_length_value) > tolerance:
                            valid_repeat = False
                            break
                    
                    items.append(UsedItem(r.id, r.width, r.length, qty_this_repeat, original_qty_map[r.id]))
                    remaining_for_repeat -= qty_this_repeat
                
                if valid_repeat and len(items) == num_repeats:
                    signature = get_group_signature(items)
                    if signature not in used_group_signatures:
                        total_used = sum(item.used_qty for item in items)
                        remaining_qty[r.id] -= total_used
                        
                        groups.append(Group(group_id, items))
                        used_group_signatures.add(signature)
                        group_id += 1
                        break
    
    print(f"إجمالي المجموعات النهائية: {len(groups)}")
    
    # إعداد القائمة المتبقية
    remaining = []
    for r in carpets_sorted:
        q = remaining_qty.get(r.id, 0)
        if q > 0:
            remaining.append(Rectangle(r.id, r.width, r.length, q))
    
    return groups, remaining


def group_carpets_optimized(
    carpets: List[Rectangle],
    min_width: int,
    max_width: int,
    tolerance_length: int,
    start_with_largest: bool = True,
    beam_width: int = 5,
    max_combo_types: int = 4,
    time_budget_sec: Optional[float] = None,
    start_group_id: int = 1
) -> Tuple[List[Group], List[Rectangle]]:
    """
    خوارزمية محسنة لتجميع السجاد.
    مزيج من greedy + local mini-search (beam-like) لاختيار أفضل "primary" و"partners".
    الهدف: تقليل البواقي وتحسين الاستغلال (width utilization & length consistency).
    
    المعاملات:
    - beam_width: عدد المرشحين الأفضل للاحتفاظ بها عند اختيار الحلول المؤقتة.
    - max_combo_types: حد أقصى لعدد أنواع مختلفة في التوليفة (يشابه كودك الأصلي).
    - time_budget_sec: لم تحدده => تعمل بدون حدود زمنية؛ إن عيّنت قيمة سيتوقف التنفيذ بعد انقضاءها.
    
    الإرجاع:
    - groups: قائمة Group المشكلة
    - remaining: قائمة Rectangle متبقية (بكميات)
    """

    t_start = time.time()
    # فرز حسب العرض
    carpets_sorted = sorted(carpets, key=lambda r: r.width, reverse=start_with_largest)
    id_map = {r.id: r for r in carpets_sorted}
    original_qty_map: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}
    remaining_qty: Dict[int, int] = {r.id: r.qty for r in carpets_sorted}

    # map: width -> list of ids (desc widths)
    widths_map = defaultdict(list)
    for r in carpets_sorted:
        widths_map[r.width].append(r.id)
    candidate_widths_desc = sorted(widths_map.keys(), reverse=True)

    groups: List[Group] = []
    group_id = start_group_id

    # Precompute ideal width midpoint (for scoring)
    ideal_width = (min_width + max_width) / 2.0

    # helper: compute score for a candidate group (lower is better)
    def group_score(chosen_items: List[UsedItem], ref_total_len: int) -> float:
        total_width = sum(it.width for it in chosen_items)
        # width closeness (prefer closer to ideal and closer to upper bound)
        width_pen = abs(total_width - ideal_width)
        # length consistency: compute max/min of total lengths per type (length * used_qty)
        lengths = [it.length * it.used_qty for it in chosen_items] if chosen_items else [0]
        length_variance = (max(lengths) - min(lengths)) if lengths else 0
        # penalty for violating tolerance (large penalty)
        len_pen = max(0, length_variance - tolerance_length) * 0.001  # scale down
        # prefer using more quantity (reduce leftover): negative of sum used relative to original
        used_sum = sum(it.used_qty for it in chosen_items)
        orig_sum = sum(original_qty_map.get(it.rect_id, 0) for it in chosen_items) or 1
        usage_bonus = - (used_sum / orig_sum)
        # combine
        return width_pen + len_pen + usage_bonus

    # helper generate candidate qty options for a rectangle given ref_total_len
    def qty_candidates_for(rect: Rectangle, ref_total_len: int, avail_qty: int, max_allowed_by_width: int):
        # desired qty approximates ref_total_len / rect.length
        if rect.length <= 0:
            return [1] if avail_qty > 0 else []
        desired = max(1, int(round(ref_total_len / rect.length)))
        # limit by availability and width ceiling
        max_by_width = max(1, max_allowed_by_width // rect.width) if rect.width > 0 else avail_qty
        high = min(avail_qty, max_by_width)
        low = 1
        # create a small range around desired but clipped
        cand_low = max(low, desired - 2)
        cand_high = min(high, desired + 2)
        # ensure we return at least some candidates
        cands = sorted(set(range(cand_low, cand_high + 1)))
        if not cands and high >= 1:
            cands = [1]
        return [q for q in cands if 1 <= q <= avail_qty]

    # main loop
    safety_counter = 0
    max_iterations = 10000
    while True:
        # time budget check
        if time_budget_sec is not None and (time.time() - t_start) > time_budget_sec:
            # stop due to budget
            break

        safety_counter += 1
        if safety_counter > max_iterations:
            break

        # pick top-K primaries (to allow exploring choices)
        primaries = []
        for r in carpets_sorted:
            if remaining_qty.get(r.id, 0) > 0 and r.width <= max_width:
                primaries.append(r)
            if len(primaries) >= beam_width:
                break
        if not primaries:
            break

        best_overall = None  # tuple (score, chosen_items, chosen_width, primary, use_primary)
        # try each primary candidate but allow deeper search for each
        for primary in primaries:
            avail_primary = remaining_qty.get(primary.id, 0)
            # try using different counts of primary (from max -> 1)
            for use_primary in range(min(avail_primary, max_width // primary.width), 0, -1):
                ref_total_len = primary.length * use_primary
                chosen_items = [UsedItem(primary.id, primary.width, primary.length, use_primary,
                                         original_qty_map.get(primary.id, 0))]
                chosen_width = primary.width * 1  # note: we treat entry as block (width counted once per used entry)
                # NOTE: to support repeating entries as separate rows (1 per piece), we will later expand used_qty -> repeated items
                # For width accounting we count width per block entry; we consider blocks, not per-piece width sum.
                # To keep behavior consistent with earlier request (repeat as separate rows), we'll produce repeated UsedItem entries at the end.

                # remaining width to fill
                rem_min = min_width - chosen_width
                rem_max = max_width - chosen_width
                if rem_max < 0:
                    continue

                # temp quantities
                temp_qty = dict(remaining_qty)
                temp_qty[primary.id] = max(0, temp_qty.get(primary.id, 0) - use_primary)

                # Candidate set: restrict to top M rectangles by width (to limit branching)
                candidate_ids = []
                for w in candidate_widths_desc:
                    for cid in widths_map[w]:
                        if cid == primary.id:
                            continue
                        if temp_qty.get(cid, 0) > 0 and id_map[cid].width + chosen_width <= max_width:
                            candidate_ids.append(cid)
                    # cap candidate list size to limit work
                    if len(candidate_ids) >= 20:
                        break

                # mini beam: keep top N partial solutions
                partials = [ (0.0, chosen_items, chosen_width, temp_qty) ]  # (score, items, width, temp_qty)
                # expand up to max_combo_types steps
                for depth in range(max_combo_types):
                    new_partials = []
                    for score_so_far, items_so_far, width_so_far, qty_map_so_far in partials:
                        # try adding each candidate type (one block)
                        for cid in candidate_ids:
                            if qty_map_so_far.get(cid, 0) <= 0:
                                continue
                            cand = id_map[cid]
                            # compute plausible qty candidates for this cand
                            max_allowed_by_width = max_width - width_so_far
                            q_cands = qty_candidates_for(cand, ref_total_len, qty_map_so_far[cid], max_allowed_by_width)
                            for q in q_cands:
                                # check width feasibility
                                if width_so_far + cand.width > max_width:
                                    continue
                                # check length tolerance
                                cand_total_len = cand.length * q
                                diff = abs(cand_total_len - ref_total_len)
                                # allow within tolerance (we penalize otherwise but still can consider)
                                # we'll treat > tolerance as high-penalty (but allow if needed)
                                new_items = list(items_so_far)
                                new_items.append(UsedItem(cid, cand.width, cand.length, q, original_qty_map.get(cid, 0)))
                                new_width = width_so_far + cand.width
                                sc = group_score(new_items, ref_total_len)
                                # add to partials
                                new_qty_map = dict(qty_map_so_far)
                                new_qty_map[cid] = max(0, new_qty_map.get(cid, 0) - q)
                                new_partials.append((sc, new_items, new_width, new_qty_map))
                    if not new_partials:
                        break
                    # prune: keep best beam_width partials
                    new_partials.sort(key=lambda x: x[0])
                    partials = new_partials[:max(beam_width, 3)]

                # evaluate partials and keep best that satisfy width min condition
                for sc, items_candidate, width_candidate, qty_map_candidate in partials:
                    if min_width <= width_candidate <= max_width:
                        # final score combine
                        final_sc = sc
                        if best_overall is None or final_sc < best_overall[0]:
                            best_overall = (final_sc, items_candidate, width_candidate, primary, use_primary, qty_map_candidate)

                # if we already found very good solution (close to ideal and uses many pieces) break early
                if best_overall and best_overall[0] < 1e-6:
                    break
            if best_overall and best_overall[0] < 1e-6:
                break

        # if a best solution found -> commit it
        if best_overall:
            _, chosen_items, chosen_width, primary_used, primary_qty_used, final_qty_map = best_overall
            # commit: update remaining_qty using the final_qty_map and chosen_items
            # BUT note: chosen_items contains UsedItem blocks with used_qty possibly >1.
            # We will record groups using repeated UsedItem(entries with used_qty=1) for each unit if desired (per request).
            # First, apply reductions
            for it in chosen_items:
                remaining_qty[it.rect_id] = max(0, remaining_qty.get(it.rect_id, 0) - it.used_qty)
                # update id_map.qty for external visibility
                id_map[it.rect_id].qty = remaining_qty[it.rect_id]
            # create group entries: explode multi-qty into single-unit UsedItem rows
            exploded = []
            for it in chosen_items:
                # explode into units of 1 for representation (keeps original_qty in each)
                for _ in range(it.used_qty):
                    exploded.append(UsedItem(it.rect_id, it.width, it.length, 1, original_qty_map.get(it.rect_id, 0)))

    # if no group formed from any primary -> try fallback: use maximum quantity of the same rectangle
    fallback_done = False
    for r in carpets_sorted:
        avail = remaining_qty.get(r.id, 0)
        if avail <= 0 or r.width <= 0:
            continue
            
        # Calculate maximum possible repeats within width constraints
        max_repeats_by_width = max_width // r.width
        max_possible = min(avail, max_repeats_by_width)
        
        if max_possible == 0:
            continue
            
        # Calculate how many full groups we can make with max_possible repeats
        if max_possible * r.width >= min_width:
            # We can make at least one valid group with max_possible repeats
            group_size = max_possible
            groups_to_make = avail // group_size
            
            for _ in range(groups_to_make):
                if group_size * r.width > max_width or group_size * r.width < min_width:
                    break
                    
                # Create the group with maximum possible quantity
                remaining_qty[r.id] = max(0, remaining_qty.get(r.id, 0) - group_size)
                id_map[r.id].qty = remaining_qty.get(r.id, 0)
                
                # Create a single UsedItem with the actual quantity instead of exploding
                groups.append(Group(
                    group_id, 
                    [UsedItem(r.id, r.width, r.length, group_size, original_qty_map.get(r.id, 0))]
                ))
                group_id += 1
                fallback_done = True
            
            if fallback_done:
                break
        
        # If we couldn't make full groups, try with smaller quantities
        if not fallback_done and max_possible > 1:
            for repeat in range(max_possible, 0, -1):
                total_w = r.width * repeat
                if min_width <= total_w <= max_width and avail >= repeat:
                    remaining_qty[r.id] = max(0, remaining_qty.get(r.id, 0) - repeat)
                    id_map[r.id].qty = remaining_qty.get(r.id, 0)
                    groups.append(Group(
                        group_id,
                        [UsedItem(r.id, r.width, r.length, repeat, original_qty_map.get(r.id, 0))]
                    ))
                    group_id += 1
                    fallback_done = True
                    break
            
        if fallback_done:
            break

    # prepare remaining rectangles
    remaining = []
    for r in carpets_sorted:
        q = remaining_qty.get(r.id, 0)
        if q > 0:
            remaining.append(Rectangle(r.id, r.width, r.length, q))

    # Try to combine similar groups if possible
    if groups:
        combined = combine_similar_groups(groups, min_width, max_width, tolerance_length)
    
    return combined, remaining

def combine_similar_groups(groups: List[Group], min_width: int, max_width: int, tolerance: int) -> List[Group]:
    """
    دمج المجموعات المتشابهة في معرفات العناصر وعددها (بغض النظر عن الكميات).
    يتم دمج الكميات والتحقق من شرط السماحية والعرض.
    """
    if not groups:
        return []

    # المرحلة الأولى: تجميع حسب معرفات العناصر فقط (تجاهل الكميات)
    groups_by_rects = {}
    
    for group in groups:
        # ترتيب العناصر حسب المعرف للمقارنة المتسقة
        sorted_items = sorted(group.items, key=lambda x: x.rect_id)
        rect_ids = tuple(item.rect_id for item in sorted_items)
        
        if rect_ids not in groups_by_rects:
            groups_by_rects[rect_ids] = []
            
        groups_by_rects[rect_ids].append({
            'group': group,
            'items': sorted_items,
            'total_width': sum(item.width for item in sorted_items),  # العرض = مجموع عرض كل نوع
            'total_lengths': [item.length * item.used_qty for item in sorted_items]
        })
    
    # المرحلة الثانية: دمج المجموعات المتشابهة
    combined_groups = []
    
    for rect_ids, group_list in groups_by_rects.items():
        if len(group_list) <= 1:
            # مجموعة واحدة فقط، لا حاجة للدمج
            combined_groups.append(group_list[0]['group'])
            continue
        
        # دمج جميع المجموعات المتشابهة في مجموعة واحدة
        # الشرط الوحيد: نفس معرفات العناصر ونفس عدد العناصر
        base_group = group_list[0]
        
        # جمع الكميات من جميع المجموعات المتشابهة
        for other_group in group_list[1:]:
            # دمج الكميات مباشرة بدون شرط السماحية
            for base_item, other_item in zip(base_group['items'], other_group['items']):
                base_item.used_qty += other_item.used_qty
            
            # تحديث الأطوال الإجمالية
            combined_lengths = [bl + ol for bl, ol in 
                              zip(base_group['total_lengths'], other_group['total_lengths'])]
            base_group['total_lengths'] = combined_lengths
        
        # إضافة المجموعة المدمجة
        combined_groups.append(base_group['group'])
    
    # تحديث معرفات المجموعات
    for i, group_data in enumerate(combined_groups, 1):
        group_data.id = i
    
    return combined_groups

def regroup_residuals(residuals, min_width, max_width, tolerance):
    """
    خوارزمية إعادة تجميع البواقي لتكوين مجموعات جديدة قابلة للاستخدام
    """
    # ترتيب البواقي حسب العرض تنازليًا
    residuals = sorted(residuals, key=lambda x: x['width'], reverse=True)
    new_groups = []

    while residuals:
        base = residuals[0]
        base_width = base['width']
        base_length = base['length']
        base_count = base['remaining']
        group = []
        total_width = base_width
        group_length = base_length

        # نبدأ بالمستطيل الأكبر عرضًا
        group.append({
            'id': base['id'],
            'width': base_width,
            'length': base_length,
            'used': base_count
        })
        residuals[0]['remaining'] = 0  # استُخدم بالكامل

        # نبحث عن قطع تكمل النطاق
        for i in range(1, len(residuals)):
            item = residuals[i]
            if item['remaining'] <= 0:
                continue

            new_width = total_width + item['width']
            if min_width <= new_width <= max_width:
                if abs(item['length'] - group_length) <= tolerance:
                    group.append({
                        'id': item['id'],
                        'width': item['width'],
                        'length': item['length'],
                        'used': item['remaining']
                    })
                    total_width += item['width']
                    residuals[i]['remaining'] = 0

        # إذا تشكّلت مجموعة فعالة وتحقق الشروط
        if len(group) > 1 and min_width <= total_width <= max_width:
            new_groups.append({
                'items': group,
                'total_width': total_width,
                'ref_length': group_length,
                'count_types': len(group)
            })

        # حذف العناصر المستخدمة
        residuals = [r for r in residuals if r['remaining'] > 0]

    return new_groups