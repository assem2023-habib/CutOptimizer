from dataclasses import dataclass, field

@dataclass
class CarpetUsed:
    carpet_id: int
    width: int
    height: int
    qty_used: int
    qty_rem: int
    client_order: int
    
    repeated: list[dict] = field(default_factory=list)
                                 
    def length_ref(self) -> int:
        """الطول المرجعي = الارتفاع * العدد المستخدم"""
        return self.height * self.qty_used

    def area(self) -> int:
        """حساب المساحة الكلية"""
        return self.width * self.height * self.qty_used

    def to_dict(self) -> dict:
        """تحويل إلى قاموس (dict)"""
        return {
            "carpet_id": self.carpet_id,
            "width": self.width,
            "height": self.height,
            "qty_used": self.qty_used,
            "qty_rem": self.qty_rem,
            "length_ref": self.length_ref(),
            "client_order": self.client_order,
        }

    def summary(self) -> str:
        """نص مختصر لوصف السجادة المستخدمة"""
        return f"id:{self.carpet_id} | {self.width}*{self.height}"
