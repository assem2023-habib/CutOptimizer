from typing import List, Optional, Tuple, Iterator
from models.data_models import Carpet, CarpetUsed, GroupCarpet
from math import floor, ceil 
from collections import Counter
from itertools import combinations, combinations_with_replacement

# ------------------------
# 1️⃣ توابع رياضية مساعدة
# ------------------------

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def lcm(a:int, b:int)->int:
    return abs(a*b) // gcd(a, b) if a and b else 0

def gcd_list(lst: List[int])->int:
    if not lst:
        return 0
    result = lst[0]
    for num in lst[1:]:
        result = gcd(result,num)
    return result

def lcm_list(lst: List[int])->int:
    if not lst:
        return 0
    result = lst[0]
    for num in lst[1:]:
        result = lcm(result, num)
    return result

# ------------------------
# 2️⃣ تابع اختيار n شركاء
# ------------------------

def equal_products_solution(a: List[int], Xmax:List[int])->Tuple[Optional[List[int]], int]:
    n = len(a)
    if n == 0 or n!=len(Xmax):
        return None,0
    g = gcd_list(a)
    if g == 0:
        return None, 0
    A = [ai // g for ai in a]

    l = lcm_list(A)
    if l == 0:
        return None, 0
    
    limits = []
    for Ai, Xmi in zip(A, Xmax):
        if Ai == 0:
            limits.append(0)
        else:
            limit = (Xmi * Ai) / l
            limits.append(limit)
    k_max = int(floor(min(limits))) if limits else 0

    if k_max <= 0:
        return None, 0

    x_list = []
    for Ai in A:
        xi = (l * k_max) // Ai
        x_list.append(int(xi))
    
    return x_list, k_max

def equal_products_solution_with_tolerance(a: List[int],
                             Xmax:List[int],
                             delta : int)->Tuple[Optional[List[int]], int]:
    n = len(a)
    if n == 0 or n!=len(Xmax):
        return None,0
    if any (ai <= 0 for ai in a):
        return None, 0
    if any(xm < 0 for xm in Xmax):
        return None, 0
    if n == 1 :
        return [Xmax[0]], Xmax[0]
    
    a_ref = a[0]
    x0_max = Xmax[0]

    for i in range(1, n):
        limit = floor((a[i] * Xmax[i] + delta) /a_ref )
        x0_max = min(x0_max,limit)
    if x0_max < 0:
        return None, 0  

    for x0 in range(x0_max, -1, -1):
        target = a_ref * x0
        x_candidate = [x0]
        valid = True
        for i in range(1, n):
            x_i_min_raw = (target - delta) / a[i]
            x_i_min = max(0, ceil(x_i_min_raw))

            x_i_max = floor((target + delta) / a[i])
            x_i = min(x_i_max, Xmax[i])
            if x_i < x_i_min or x_i < 0:
                valid = False
                break

            if abs(a[i] * x_i - target) > delta:
                valid = False
                break

            x_candidate.append(x_i)
        
        if not valid:
            continue

        all_pairs_valid = True
        for i in range(n):
            for j in range(i + 1, n):
                diff = abs(a[i] * x_candidate[i] - a[j] * x_candidate[j])
                if diff > delta:
                    all_pairs_valid = False
                    break
            if not all_pairs_valid:
                break
        if all_pairs_valid:
            k_max = x_candidate[0]
            return x_candidate, k_max
    return None, 0


def generate_combinations(candidates: List[Carpet], n: int)-> Iterator[List[Carpet]]:
    for combo in combinations(candidates, n):
        yield list(combo)

def generate_combinations_with_repetition(candidates: List[Carpet], n: int)->Iterator[List[Carpet]]:
    for combo in combinations_with_replacement(candidates, n):
        counts = Counter(c.id for c in combo)
        valid = True
        for cid, cnt in counts.items():
            carpet = next((cand for cand in candidates if cand.id == cid), None)
            if not carpet or carpet.rem_qty < cnt:
                valid = False
                break
        if valid:
            yield list(combo)

def generate_combinations_exclude_main(
        candidates: List[Carpet],
        n: int,
        main: Carpet
    )->Iterator[List[Carpet]]:

    filtered_candidates = [
        c for c in candidates
        if c.id != main.id and c.is_available() and c.width != main.width
    ]
    for combo in combinations(filtered_candidates, n):
        yield list(combo)

def generate_combinations_with_repetition_exclude_main(
        candidates: List[Carpet],
        n: int,
        main: Carpet,    
    )->Iterator[List[Carpet]]:
    filtered_candidates = [
        c for c in candidates
        if c.id != main.id and c.is_available() and c.width != main.width
    ]
    for combo in combinations_with_replacement(filtered_candidates, n):
        counts= Counter(c.id for c in combo)
        valid = True
        for cid, cnt in counts.items():
            carpet= next((cand for cand in filtered_candidates if cand.id == cid), None)
            if not carpet or carpet.rem_qty < cnt:
                valid = False
                break
        if valid:
            yield list(combo)

def generate_valid_partner_combinations(
        main: Carpet,
        candidates: List[Carpet],
        n: int,
        min_width: int,
        max_width: int,
        allow_repetation: bool = False,
        start_index: int =0,
        exclude_main: bool = False,
    )->List[List[Carpet]]:
    valid_group = []
    filtered_candidates = [
        c for c in candidates[start_index:]
        if c.is_available() and (main.width + c.width) <= max_width
    ]
    if not filtered_candidates:
        return valid_group

    if allow_repetation:
        if exclude_main:
            iterator  = generate_combinations_with_repetition_exclude_main(filtered_candidates, n, main)
        else:
            iterator  = generate_combinations_with_repetition(filtered_candidates, n)
    else:
        if exclude_main:
            iterator  = generate_combinations_exclude_main(filtered_candidates, n, main)
        else:
            iterator  = generate_combinations(filtered_candidates, n) 

    for partners in iterator :
        total_width = main.width + sum(p.width for p in partners)
        if min_width <= total_width <= max_width:
            valid_group.append(partners)
    return valid_group
