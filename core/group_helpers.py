from typing import List, Optional, Tuple, Iterator
from models.data_models import Carpet, CarpetUsed, GroupCarpet
from math import floor 
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

# def test_candidate_group(elements: List[Carpet], min_width:int, max_width:int) ->bool:
#     a = [int(e.height) for e in elements]
#     XMax = [int(e.rem_qty) for e in elements]

#     x_vals, k_max = equal_products_solution(a, XMax)
#     if not x_vals :
#         return  False
#     total_width = sum(int(e.width) for e in elements)

#     if not (min_width <= total_width <= max_width):
#         return False
    
#     return True

def generate_combinations(candidates: List[Carpet], n: int)-> Iterator[List[Carpet]]:
    for combo in combinations(candidates, n):
        yield list(combo)

def generate_combinations_with_repetition(candidates: List[Carpet], n: int)->Iterator[List[Carpet]]:
    for combo in combinations_with_replacement(candidates, n):
        counts = Counter(c.id for c in combo)
        valid = all(
            next((cand for cand in candidates if cand.id == cid)).rem_qty >= cnt
            for cid, cnt in counts.items()
        )
        if valid:
            yield list(combo)

def generate_valid_partner_combinations(
        main: Carpet,
        candidates: List[Carpet],
        n: int,
        min_width: int,
        max_width: int,
        allow_repetation: bool = False
    )->List[List[Carpet]]:
    valid_group = []
    generator = (
        generate_combinations_with_repetition if allow_repetation
        else generate_combinations
    )
    for partners in generator(candidates, n):
        total_width = main.width + sum(p.width for p in partners)
        if min_width <= total_width <= max_width:
            valid_group.append(partners)
    return valid_group


