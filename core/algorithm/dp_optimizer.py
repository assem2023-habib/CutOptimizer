import math
from itertools import combinations
from typing import List, Tuple, Optional
from models.group_carpet import Carpet, CarpetUsed, GroupCarpet

class DPOptimizer:
    def __init__(
            self,
            carpets: List[Carpet],
            min_width: int,
            max_width: int,
            tolerance: int,
            max_partner: int=7
    ):
        self.carpets= carpets
        self.min_width= min_width
        self.max_width= max_width
        self.tolerance= tolerance
        self.max_partner= max_partner
        self.valid_groups_cache= []
        
    def optimize(self)->List[GroupCarpet]:
        self._generate_valid_groups()
        if not self.valid_groups_cache:
            return []
        
        best_group_indices= self._solve_dp()

        result_groups= self._build_result_groups(best_group_indices)

        return result_groups
    
    def _generate_valid_groups(self)->None:
        self.valid_groups_cache= []
        n= len(self.carpets)

        for size in range(1, min(self.max_partner + 1, n + 1)):
            for combo in combinations(range(n), size):
                total_width= sum(self.carpets[i].width for i in combo)
                if self.min_width <= total_width <= self.max_width:
                    quantities= self._find_optimal_quantities(combo)

                    if quantities:
                        group_info= {
                            'carpet_indices': combo,
                            'quantities': quantities,
                            'total_consumed': sum(quantities),
                            'total_width': total_width
                        }
                        self.valid_groups_cache.append(group_info)

    def _find_optimal_quantities(self, carpet_indices: Tuple[int])-> Optional[List[int]]:
        selected_carpets= [self.carpets[i] for i in carpet_indices]
        possible_length_refs= set()
        for carpet in selected_carpets:
            for q in range(1, carpet.rem_qty + 1):
                possible_length_refs.add(q * carpet.height)

        possible_length_refs= sorted(possible_length_refs)

        best_quantities= None
        max_total= 0

        for min_ref in possible_length_refs:
            max_ref= min_ref + self.tolerance

            quantities= []
            length_refs= []
            valid= True

            for carpet in selected_carpets:
                max_possible_q= int(max_ref / carpet.height)
                max_q= min(carpet.rem_qty, max_possible_q)

                min_possible_q= math.ceil(min_ref / carpet.height)

                if min_possible_q <= max_q:
                    q= max_q
                    quantities.append(q)
                    length_refs.append(q * carpet.height)
                else:
                    valid= False
                    break

            if valid and length_refs:
                if max(length_refs) - min(length_refs) <= self.tolerance:
                    total= sum(quantities)
                    if total > max_total:
                        max_total= total
                        best_quantities= quantities

        return best_quantities

    def _solve_dp(self)->List[int]:
        initial_state= tuple(carpet.rem_qty for carpet in self.carpets)
        dp= {initial_state: (0, [])}

        max_iterations= 1000
        iteration= 0

        while iteration < max_iterations:
            new_dp= {}
            improved= False

            for state, (consumed, groups_used) in dp.items():
                for group_idx, group_info in enumerate(self.valid_groups_cache):
                    carpet_indices= group_info['carpet_indices']
                    quantities= group_info['quantities']

                    new_state= list(state)
                    can_use= True

                    for idx, q in zip(carpet_indices, quantities):
                        if new_state[idx] >= q:
                            new_state[idx] -= q
                        else:
                            can_use= False
                            break
                    
                    if can_use:
                        new_state_tuple= tuple(new_state)
                        new_consumed= consumed + group_info['total_consumed']
                        new_groups= groups_used + [group_idx]

                        if (new_state_tuple not in new_dp or
                            new_dp[new_state_tuple][0] < new_consumed):
                            new_dp[new_state_tuple]= (new_consumed, new_groups)
                            improved= True
            
            if not improved or not new_dp:
                break

            dp.update(new_dp)
            iteration += 1

        best_consumed= 0
        best_groups= []

        for state, (consumed, groups) in dp.items():
            if consumed > best_consumed:
                best_consumed= consumed
                best_groups= groups
        
        return best_groups
    
    def _build_result_groups(self, group_indices: List[int])->List[GroupCarpet]:

        result_groups= []
        for group_id, group_idx in enumerate(group_indices, start= 1):
            group_info= self.valid_groups_cache[group_idx]
            carpet_indices= group_info['carpet_indices']
            quantities= group_info['quantities']

            items= []
            for carpet_idx, qty_used in zip(carpet_indices, quantities):
                carpet= self.carpets[carpet_idx]

                carpet_used= CarpetUsed(
                    carpet_id= carpet.id,
                    width= carpet.width,
                    height= carpet.height,
                    qty_used= qty_used,
                    qty_rem= carpet.rem_qty - qty_used
                )
                items.append(carpet_used)

                carpet.consume(qty_used)
            
            group= GroupCarpet(group_id= group_id, items= items)
            result_groups.append(group)
        return result_groups