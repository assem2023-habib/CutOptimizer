
from models.group_carpet import Carpet
from core.algorithm import build_groups


def main():
    """مثال على الاستخدام"""
    
    # إنشاء السجاد
    carpets = [
        Carpet(id=1, width=50, height=100, qty=20),
        Carpet(id=2, width=30, height=150, qty=15),
        Carpet(id=3, width=40, height=120, qty=18),
        Carpet(id=4, width=60, height=80, qty=25),
        Carpet(id=5, width=20, height=200, qty=10),
    ]
    
    print("📦 السجاد المتاح:")
    for carpet in carpets:
        print(f"  ID={carpet.id}, {carpet.width}x{carpet.height}, qty={carpet.qty}")
    
    # الإعدادات
    min_width = 80
    max_width = 150
    max_partner = 3
    tolerance = 300
    
    print(f"\n⚙️ الإعدادات:")
    print(f"   Width : [{min_width}, {max_width}]")
    print(f"  Tolerance: {tolerance}")
    print(f" Max Tolerance : {max_partner}")
    
    # بناء المجموعات
    print("\n🚀 Build groups..")
    groups = build_groups(
        carpets=carpets,
        min_width=min_width,
        max_width=max_width,
        max_partner=max_partner,
        tolerance=tolerance
    )
    
    # طباعة النتائج
    print(f"\n✅ Group build successfuly counts: {len(groups)}")
    print("\n" + "="*70)
    
    total_qty_consumed = 0
    
    for group in groups:
        print(f"\n{group.summary()}")
        print(f"  total group:  {group.total_width()}")
        print(f"  •  total_quantity: {group.total_qty()}")
        print(f"  •  length_ref: [{group.min_length_ref()}, {group.max_length_ref()}]")
        print(f"  • (tolerance): {group.max_length_ref() - group.min_length_ref()}")
        print(f"  •  total area: {group.total_area()}")
        
        total_qty_consumed += group.total_qty()
        
        print("  • details:")
        for item in group.items:
            print(f"    - {item.summary()}, qty={item.qty_used}, length_ref={item.length_ref()}")
    
    print("\n" + "="*70)
    print(f"🎯   total quantity consumed: {total_qty_consumed}")
    
    print("\n📊  qty rem :")
    for carpet in carpets:
        consumed = carpet.qty - carpet.rem_qty
        percentage = (consumed / carpet.qty * 100) if carpet.qty > 0 else 0
        print(f"  ID={carpet.id}: consume {consumed}/{carpet.qty} ({percentage:.1f}%), "
              f"rem_qty={carpet.rem_qty}")


if __name__ == "__main__":
    main()