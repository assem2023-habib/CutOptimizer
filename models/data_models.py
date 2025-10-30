from dataclasses import dataclass, field
from typing import List

@dataclass
class Carpet:
    id: int
    width: int
    height: int
    qty: int
    rem_qty: int = field(init=False)

    def __post_init__(self):
        self.rem_qty = self.qty

    def area(self) -> int:
        return self.width * self.height
    
    def consume(self, qty_used: int) ->None:
        if qty_used > self.rem_qty:
            raise ValueError(f"Cannot consume {qty_used}, only {self.rem_qty} left for {self.id}")
        self.rem_qty -= qty_used

    def is_available(self) -> bool:
        return self.rem_qty > 0

@dataclass
class CarpetUsed:
    carpet_id: int
    width: int
    height: int
    qty_used: int
    qty_rem:int

    def length_ref(self) -> int:
        return self.height * self.qty_used
    
    def area (self) -> int:
        return self.width * self.height * self.qty_used
    
    def to_dict(self) -> dict:
        return {
            "carpet_id" : self.carpet_id,
            "width" : self.width,
            "height" : self.height,
            "qty_used" : self.qty_used,
            "qty_rem" : self.qty_rem,
            "length_ref": self.length_ref(),
        }

    def summary(self) -> str:
        """نص مختصر لوصف السجادة المستخدمة"""
        return f"Carpet {self.carpet_id} | w={self.width} h={self.height} qty={self.qty_used}"

@dataclass
class GroupCarpet:
    group_id: int
    items: List[CarpetUsed] = field(default_factory=list)
    
    def total_width(self)->int:
        return sum(item.width for item in self.items)
    
    def total_height(self)->int:
        return sum(item.height for item in self.items)
    
    def total_height(self)->int:
        return max(item.height for item in self.items)
    
    def total_qty(self)->int:
        return sum(item.qty_used for item in self.items)
    
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
        """إرجاع الطول المرجعي (طول أول عنصر في المجموعة)"""
        if not self.items:
            return 0  # أو يمكنك رفع استثناء إذا كانت القائمة فارغة
        return self.items[0].length_ref()