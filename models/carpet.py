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
    qty_original_before_pair_mode: int = field(init=False)

    def __post_init__(self):
        self.rem_qty = self.qty
        self.qty_original_before_pair_mode = self.qty

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

        for rep in list(self.repeated):
            if remaining <= 0:
                break

            take = min(rep["qty_rem"], remaining)

            if take > 0:
                consumed.append({
                    "id": rep["id"],
                    "qty": take,
                    "qty_original":rep["qty_original"] ,
                    "qty_rem": rep["qty_rem"] - take,
                    "client_order": rep["client_order"]
                })

                rep["qty_rem"] -= take
                remaining -= take

            if rep["qty_rem"] == 0:
                self.repeated.remove(rep)
        return consumed
    
    def restore_repeated(self, consumed_list: list[dict]) -> None:
        """
        ✅ إعادة الكميات المستهلكة من repeated
        تُستخدم عند التراجع عن استهلاك فاشل
        """
        for consumed_item in consumed_list:
            consumed_id = consumed_item["id"]
            qty_to_restore = consumed_item["qty"]
            
            # البحث عن العنصر في repeated
            found = False
            for rep in self.repeated:
                if rep["id"] == consumed_id:
                    rep["qty_rem"] += qty_to_restore
                    found = True
                    break
            
            # إذا لم يُعثر عليه (تم حذفه لأن qty_rem كان 0)، نعيد إضافته
            if not found:
                self.repeated.append({
                    "id": consumed_id,
                    "qty_original": consumed_item["qty_original"],
                    "qty_rem": qty_to_restore,
                    "client_order": consumed_item["client_order"]
                })