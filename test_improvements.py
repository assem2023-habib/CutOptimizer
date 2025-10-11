#!/usr/bin/env python3
"""
اختبار التحسينات الجديدة لنظام تحسين القطع
==============================================

هذا الملف يختبر التحسينات الجديدة التي تم إضافتها لنظام تشكيل مجموعات البواقي
"""

from core.models import Rectangle
from data_io.remainder_optimizer import (
    process_remainder_complete,
    generate_size_suggestions,
    analyze_remaining_for_optimization
)

def test_improved_remainder_algorithm():
    """اختبار الخوارزمية المحسنة لتشكيل مجموعات البواقي"""
    
    print("اختبار الخوارزمية المحسنة لتشكيل مجموعات البواقي")
    print("=" * 60)
    
    # إنشاء بيانات اختبار
    test_remaining = [
        Rectangle(1, 240, 340, 100),  # مثال من الشرح
        Rectangle(2, 160, 230, 200),
        Rectangle(3, 130, 200, 50),
        Rectangle(4, 300, 600, 10),  # مثال يحتاج شريك
    ]
    
    print(f"البيانات الأولية:")
    for rect in test_remaining:
        print(f"  - معرف {rect.id}: {rect.width}x{rect.length} (كمية: {rect.qty})")
    
    print(f"\nمعاملات الاختبار:")
    print(f"  - النطاق المطلوب: 370-400")
    print(f"  - هامش التسامح: 100")
    print(f"  - حدود الكمية: 650-700")
    
    # اختبار الخوارزمية المحسنة
    groups, final_remaining, stats = process_remainder_complete(
        test_remaining,
        min_width=370,
        max_width=400,
        tolerance_length=100,
        start_group_id=1000,
        merge_after=True,
        verbose=True,
        min_group_quantity=650,
        max_group_quantity=700
    )
    
    print(f"\nالنتائج:")
    print(f"  - عدد المجموعات المشكلة: {len(groups)}")
    print(f"  - عدد العناصر المتبقية: {len(final_remaining)}")
    print(f"  - نسبة الاستغلال: {stats['utilization_percentage']:.2f}%")
    print(f"  - الكمية المستخدمة: {stats['total_quantity_used']:,}")
    print(f"  - الكمية المتبقية: {stats['total_quantity_after']:,}")
    
    print(f"\nتفاصيل المجموعات:")
    for group in groups:
        print(f"  - المجموعة {group.id}:")
        for item in group.items:
            print(f"    * {item.width}x{item.length} (مستخدم: {item.used_qty})")
        print(f"    * العرض الإجمالي: {group.total_width()}")
        print(f"    * الطول المرجعي: {group.ref_length()}")
    
    if final_remaining:
        print(f"\nالعناصر المتبقية:")
        for rect in final_remaining:
            print(f"  - معرف {rect.id}: {rect.width}x{rect.length} (كمية متبقية: {rect.qty})")
    
    return groups, final_remaining, stats

def test_size_suggestions():
    """اختبار دالة توليد اقتراحات المقاسات"""
    
    print("\n\nاختبار توليد اقتراحات المقاسات")
    print("=" * 60)
    
    # بيانات اختبار للبواقي
    test_remaining = [
        Rectangle(1, 300, 600, 10),  # يحتاج شريك بعرض 70-100
        Rectangle(2, 200, 400, 5),   # يحتاج شريك بعرض 170-200
        Rectangle(3, 380, 500, 3),  # يمكن أن يكون وحده
    ]
    
    print(f"البواقي المراد تحليلها:")
    for rect in test_remaining:
        print(f"  - معرف {rect.id}: {rect.width}x{rect.length} (كمية: {rect.qty})")
    
    # توليد الاقتراحات
    suggestions = generate_size_suggestions(
        test_remaining,
        min_width=370,
        max_width=400,
        tolerance_length=100
    )
    
    print(f"\nالاقتراحات:")
    for suggestion in suggestions:
        print(f"  - المقاس: {suggestion['current_item']}")
        print(f"    الكمية: {suggestion['quantity']}")
        print(f"    النوع: {suggestion['type']}")
        print(f"    العرض المطلوب: {suggestion.get('required_width_range', suggestion['group_width'])}")
        print(f"    الاقتراح: {suggestion['suggestion']}")
        print(f"    الكفاءة: {suggestion['efficiency']}")
        print()
    
    # تحليل شامل
    analysis = analyze_remaining_for_optimization(
        test_remaining,
        min_width=370,
        max_width=400,
        tolerance_length=100
    )
    
    print(f"التحليل الشامل:")
    print(f"  - إجمالي العناصر: {analysis['total_items']}")
    print(f"  - إجمالي الكمية: {analysis['total_quantity']}")
    print(f"  - إجمالي المساحة: {analysis['total_area']:,}")
    print(f"  - المجموعات المحتملة: {analysis['potential_groups']}")
    print(f"  - إمكانية الاستغلال: {analysis['utilization_potential']:.1f}%")
    
    if analysis['optimization_recommendations']:
        print(f"\nالتوصيات:")
        for rec in analysis['optimization_recommendations']:
            print(f"  - {rec['item']}: {rec['suggestion']}")

def main():
    """الدالة الرئيسية للاختبار"""
    
    print("بدء اختبار التحسينات الجديدة لنظام تحسين القطع")
    print("=" * 80)
    
    try:
        # اختبار الخوارزمية المحسنة
        groups, remaining, stats = test_improved_remainder_algorithm()
        
        # اختبار توليد الاقتراحات
        test_size_suggestions()
        
        print("\n\nتم إنجاز جميع الاختبارات بنجاح!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nحدث خطأ أثناء الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
