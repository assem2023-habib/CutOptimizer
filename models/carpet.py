from dataclasses import dataclass, field

@dataclass
class Carpet:
    id: int
    width: int
    height: int
    qty: int
    client_order: int
    rem_qty: int = field(init=False)
    repeated: list[dict] = field(default_factory=list)

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

    def consume_from_repeated(self, qty_needed: int) -> list[dict]:
        """
        استهلاك كمية من السجادات المكررة فقط (repeated)
        دون المساس بالسجادة الأصلية.
        ترجع قائمة بالكائنات المستهلكة.
        """
        consumed = []
        remaining = qty_needed

        for rep in list(self.repeated):  # نستخدم list حتى نعدّل أثناء التكرار
            if remaining <= 0:
                break

            take = min(rep["qty"], remaining)

            if take > 0:
                consumed.append({
                    "id": rep["id"],
                    "qty": take,
                    "qty_original":rep["qty"] ,
                    "qty_rem": rep["qty"] - take,
                    "client_order": rep["client_order"]
                })

                rep["qty"] -= take
                remaining -= take

            # إزالة العناصر التي انتهت كميتها
            if rep["qty"] == 0:
                self.repeated.remove(rep)

        return consumed