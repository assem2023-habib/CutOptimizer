from dataclasses import dataclass, field

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
        """إرجاع المساحة"""
        return self.width * self.height

    def consume(self, qty_used: int) -> None:
        """خصم عدد القطع المستخدمة"""
        if qty_used > self.rem_qty:
            raise ValueError(f"Cannot consume {qty_used}, only {self.rem_qty} left for {self.id}")
        self.rem_qty -= qty_used

    def is_available(self) -> bool:
        """التحقق إن كانت السجادة متاحة بعد الاستهلاك"""
        return self.rem_qty > 0
