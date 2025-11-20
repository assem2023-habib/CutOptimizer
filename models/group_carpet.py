from dataclasses import dataclass, field
from typing import List
from models.carpet_used import CarpetUsed

@dataclass
class GroupCarpet:
    group_id: int
    items: List[CarpetUsed] = field(default_factory=list)
    
    def total_width(self)->int:
        return sum(item.width for item in self.items)
    
    def total_height(self)->int:
        return sum(item.height for item in self.items)
    
    def total_length_ref(self)->int:
        return sum(item.length_ref() for item in self.items)
    
    def max_height(self)->int:
        return max(item.height for item in self.items)
    
    def max_width(self)->int:
        return max(item.width for item in self.items)    
    
    def min_width(self)->int:
        return min(item.width for item in self.items)
    
    def max_length_ref(self)->int:
        return max(item.length_ref() for item in self.items)
    
    def min_length_ref(self)->int:
        return min(item.length_ref() for item in self.items)    
    
    def total_qty(self)->int:
        return sum(item.qty_used for item in self.items)
    
    def total_rem_qty(self)->int:
        return sum(item.qty_rem for item in self.items)
    
    def total_area(self)->int:
        return sum(item.area() for item in self.items)
    
    def is_valid(self, min_width:int, max_width: int)->bool:
        tw = self.total_width()
        return min_width <= tw <=max_width
    
    def summary(self) -> str:

        items_desc = ", ".join([i.summary() for i in self.items])
        return (
            f"Group {self.group_id}: "
            f"width={self.total_width():.2f}, height={self.total_height():.2f}, "
            f"qty={self.total_qty()}, area={self.total_area():.2f}, "
            f"items=[{items_desc}]"
        )
    
    def ref_height(self) -> int:
        if not self.items:
            return 0
        return self.items[0].length_ref()
    
    def sort_items_by_width(self, reverse: bool = False) -> None:
        self.items.sort(key=lambda item: item.width, reverse=reverse)