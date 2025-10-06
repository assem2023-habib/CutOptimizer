import copy
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Rectangle:
    id: Optional[int]
    width: int
    length: int
    qty: int
    group: str = field(default=None)

    def copy(self):
        return copy.deepcopy(self)
    
@dataclass
class UsedItem:
    rect_id: Optional[int]
    width: int
    length: int
    used_qty: int
    original_qty: int

@dataclass
class Group:
    id: int
    items: List[UsedItem]

    # def total_width(self)->int:
    #     # return sum(item.width for item in self.items)# per spec: sum of widths of types
    #     return sum(item.width * item.used_qty for item in self.items)
    def total_width(self) -> int:
    # مجموع العرض كما في التقرير — نحتسب العرض لكل عنصر مرة واحدة (أو لكل entry)
        return sum(item.width for item in self.items)
    
    def ref_length(self)->int:
        # choose the length reference as the first item's total length (length * used_qty)
        if not self.items:
            return 0
        return self.items[0].length * self.items[0].used_qty
    
    def total_area(self)->int:
        # total area = sum(length * used_qty * width)
        return sum(item.length * item.used_qty * item.width for item in self.items)
