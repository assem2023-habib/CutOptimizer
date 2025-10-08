"""
مثال شامل لاستخدام حزمة معالجة ملفات Excel
==========================================

هذا الملف يحتوي على أمثلة شاملة لكيفية استخدام جميع الوحدات
في حزمة معالجة ملفات Excel.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

from data_io import (
    read_input_excel,
    write_output_excel,
    create_enhanced_remainder_groups_from_rectangles,
    generate_partner_suggestions,
    analyze_remaining_items,
    get_optimization_recommendations,
    calculate_group_efficiency,
    validate_excel_data,
    get_excel_summary
)


def example_basic_usage():
    """
    مثال أساسي لاستخدام الحزمة.
    """
    print("=== المثال الأساسي ===")
    
    # قراءة البيانات من ملف Excel
    try:
        carpets = read_input_excel("input.xlsx")
        print(f"تم قراءة {len(carpets)} عنصر من الملف")
        
        # التحقق من صحة البيانات
        if validate_excel_data(carpets):
            print("البيانات صحيحة")
        else:
            print("تحذير: هناك مشاكل في البيانات")
            
        # الحصول على ملخص البيانات
        summary = get_excel_summary(carpets)
        print(f"إجمالي الكمية: {summary['total_quantity']}")
        print(f"إجمالي المساحة: {summary['total_area']}")
        print(f"عدد الأحجام الفريدة: {summary['unique_sizes']}")
        
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")


def example_remainder_optimization():
    """
    مثال على تحسين تجميع البواقي.
    """
    print("\n=== مثال تحسين البواقي ===")
    
    # محاكاة بيانات البواقي
    from core.models import Rectangle
    
    remaining_items = [
        Rectangle(1, 120, 200, 3),
        Rectangle(2, 80, 150, 5),
        Rectangle(3, 60, 180, 4),
        Rectangle(4, 40, 160, 8)
    ]
    
    print(f"العناصر المتبقية: {len(remaining_items)}")
    
    # تحليل العناصر المتبقية
    analysis = analyze_remaining_items(remaining_items)
    print(f"إجمالي الكمية: {analysis['total_quantity']}")
    print(f"المجموعات المحتملة: {analysis['potential_groups']}")
    
    # الحصول على توصيات التحسين
    recommendations = get_optimization_recommendations(remaining_items, 370, 400, 100)
    print("التوصيات:")
    for rec in recommendations:
        print(f"- {rec}")
    
    # تشكيل مجموعات إضافية من البواقي
    enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
        remaining_items, 370, 400, 100
    )
    
    print(f"تم تشكيل {len(enhanced_groups)} مجموعة إضافية")
    print(f"العناصر المتبقية بعد التجميع: {len(final_remaining)}")
    
    # حساب كفاءة المجموعات
    for i, group in enumerate(enhanced_groups):
        efficiency = calculate_group_efficiency(group)
        print(f"المجموعة {i+1}:")
        print(f"  - استغلال العرض: {efficiency['width_utilization']:.2%}")
        print(f"  - اتساق الأطوال: {efficiency['length_consistency']:.2%}")
        print(f"  - النقاط الإجمالية: {efficiency['overall_score']:.2%}")


def example_suggestions():
    """
    مثال على توليد الاقتراحات.
    """
    print("\n=== مثال توليد الاقتراحات ===")
    
    # محاكاة بيانات البواقي
    from core.models import Rectangle
    
    remaining_items = [
        Rectangle(1, 120, 200, 2),
        Rectangle(2, 80, 150, 3),
        Rectangle(3, 60, 180, 4),
        Rectangle(4, 40, 160, 6)
    ]
    
    # توليد الاقتراحات
    suggestions = generate_partner_suggestions(remaining_items, 370, 400, 100)
    
    print(f"تم توليد {len(suggestions)} اقتراح")
    
    # عرض أفضل 5 اقتراحات
    for i, suggestion in enumerate(suggestions[:5]):
        print(f"الاقتراح {i+1}:")
        print(f"  - العنصر الأساسي: {suggestion['معرف الأساسي']}")
        print(f"  - التوصية: {suggestion['توصية مختصرة']}")
        print(f"  - العرض المقترح: {suggestion['العرض المقترح الكلي']}")
        print(f"  - التفصيل: {suggestion['تفصيل التوليفة']}")
        print()


def example_complete_workflow():
    """
    مثال على سير العمل الكامل.
    """
    print("\n=== مثال سير العمل الكامل ===")
    
    # 1. قراءة البيانات
    try:
        carpets = read_input_excel("input.xlsx")
        print(f"تم قراءة {len(carpets)} عنصر من الملف")
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")
        return
    
    # 2. التحقق من صحة البيانات
    if not validate_excel_data(carpets):
        print("تحذير: هناك مشاكل في البيانات")
        return
    
    # 3. الحصول على ملخص البيانات
    summary = get_excel_summary(carpets)
    print(f"ملخص البيانات:")
    print(f"  - إجمالي العناصر: {summary['total_items']}")
    print(f"  - إجمالي الكمية: {summary['total_quantity']}")
    print(f"  - إجمالي المساحة: {summary['total_area']}")
    
    # 4. محاكاة تشكيل المجموعات الأصلية (من الكود الرئيسي)
    # هنا يجب استدعاء الكود الرئيسي لتشكيل المجموعات الأصلية
    original_groups = []  # المجموعات الأصلية
    remaining_items = carpets  # البواقي (محاكاة)
    
    # 5. تشكيل مجموعات إضافية من البواقي
    enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
        remaining_items, 370, 400, 100
    )
    
    print(f"تم تشكيل {len(enhanced_groups)} مجموعة إضافية من البواقي")
    
    # 6. كتابة النتائج
    try:
        write_output_excel(
            "output.xlsx",
            groups=original_groups,
            remaining=final_remaining,
            enhanced_remainder_groups=enhanced_groups,
            min_width=370,
            max_width=400,
            tolerance_length=100
        )
        print("تم كتابة النتائج إلى ملف output.xlsx")
    except Exception as e:
        print(f"خطأ في كتابة الملف: {e}")


def example_advanced_analysis():
    """
    مثال على التحليل المتقدم.
    """
    print("\n=== مثال التحليل المتقدم ===")
    
    # محاكاة بيانات البواقي
    from core.models import Rectangle
    
    remaining_items = [
        Rectangle(1, 120, 200, 3),
        Rectangle(2, 80, 150, 5),
        Rectangle(3, 60, 180, 4),
        Rectangle(4, 40, 160, 8),
        Rectangle(5, 100, 190, 2),
        Rectangle(6, 70, 170, 6)
    ]
    
    # تحليل شامل للعناصر المتبقية
    analysis = analyze_remaining_items(remaining_items)
    
    print("تحليل العناصر المتبقية:")
    print(f"  - إجمالي العناصر: {analysis['total_items']}")
    print(f"  - إجمالي الكمية: {analysis['total_quantity']}")
    print(f"  - إجمالي المساحة: {analysis['total_area']}")
    print(f"  - المجموعات المحتملة: {analysis['potential_groups']}")
    
    print("\nتوزيع الأعراض:")
    for width, count in analysis['width_distribution'].items():
        print(f"  - عرض {width}: {count} قطعة")
    
    print("\nتوزيع الأطوال:")
    for length, count in analysis['length_distribution'].items():
        print(f"  - طول {length}: {count} قطعة")
    
    # الحصول على توصيات التحسين
    recommendations = get_optimization_recommendations(remaining_items, 370, 400, 100)
    
    print("\nتوصيات التحسين:")
    for rec in recommendations:
        print(f"  - {rec}")
    
    # توليد الاقتراحات
    suggestions = generate_partner_suggestions(remaining_items, 370, 400, 100)
    
    print(f"\nتم توليد {len(suggestions)} اقتراح")
    
    # عرض أفضل 3 اقتراحات
    print("\nأفضل 3 اقتراحات:")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"  {i+1}. العنصر {suggestion['معرف الأساسي']}: {suggestion['توصية مختصرة']}")


if __name__ == "__main__":
    """
    تشغيل جميع الأمثلة.
    """
    print("أمثلة شاملة لاستخدام حزمة معالجة ملفات Excel")
    print("=" * 50)
    
    # تشغيل الأمثلة
    example_basic_usage()
    example_remainder_optimization()
    example_suggestions()
    example_complete_workflow()
    example_advanced_analysis()
    
    print("\n" + "=" * 50)
    print("انتهت جميع الأمثلة")
    print("للمزيد من المعلومات، راجع ملف README.md")
