"""
اختبار أساسي لحزمة معالجة ملفات Excel
====================================

هذا الملف يحتوي على اختبارات أساسية للتأكد من عمل
جميع الوحدات بشكل صحيح.

المؤلف: نظام تحسين القطع
التاريخ: 2024
"""

import sys
import os

# إضافة المسار الحالي إلى Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_io import (
    create_enhanced_remainder_groups_from_rectangles,
    analyze_remaining_items,
    get_optimization_recommendations,
    calculate_group_efficiency
)
from core.models import Rectangle, Group, UsedItem


def test_remainder_optimization():
    """
    اختبار تحسين تجميع البواقي.
    """
    print("اختبار تحسين تجميع البواقي...")
    
    # إنشاء بيانات اختبار
    remaining_items = [
        Rectangle(1, 120, 200, 3),
        Rectangle(2, 80, 150, 5),
        Rectangle(3, 60, 180, 4),
        Rectangle(4, 40, 160, 8)
    ]
    
    print(f"العناصر المتبقية: {len(remaining_items)}")
    
    # تحليل العناصر
    analysis = analyze_remaining_items(remaining_items)
    print(f"إجمالي الكمية: {analysis['total_quantity']}")
    print(f"المجموعات المحتملة: {analysis['potential_groups']}")
    
    # تشكيل المجموعات
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
    
    return len(enhanced_groups) > 0


def test_group_efficiency():
    """
    اختبار حساب كفاءة المجموعات.
    """
    print("\nاختبار حساب كفاءة المجموعات...")
    
    # إنشاء مجموعة اختبار
    group_items = [
        UsedItem(1, 120, 200, 2, 3),
        UsedItem(2, 80, 150, 3, 5)
    ]
    group = Group(1, group_items)
    
    # حساب الكفاءة
    efficiency = calculate_group_efficiency(group)
    
    print(f"استغلال العرض: {efficiency['width_utilization']:.2%}")
    print(f"اتساق الأطوال: {efficiency['length_consistency']:.2%}")
    print(f"كفاءة المساحة: {efficiency['area_efficiency']:.2%}")
    print(f"النقاط الإجمالية: {efficiency['overall_score']:.2%}")
    
    return efficiency['overall_score'] > 0


def test_analysis():
    """
    اختبار تحليل العناصر المتبقية.
    """
    print("\nاختبار تحليل العناصر المتبقية...")
    
    # إنشاء بيانات اختبار
    remaining_items = [
        Rectangle(1, 120, 200, 3),
        Rectangle(2, 80, 150, 5),
        Rectangle(3, 60, 180, 4)
    ]
    
    # تحليل العناصر
    analysis = analyze_remaining_items(remaining_items)
    
    print(f"إجمالي العناصر: {analysis['total_items']}")
    print(f"إجمالي الكمية: {analysis['total_quantity']}")
    print(f"إجمالي المساحة: {analysis['total_area']}")
    print(f"المجموعات المحتملة: {analysis['potential_groups']}")
    
    # الحصول على توصيات التحسين
    recommendations = get_optimization_recommendations(remaining_items, 370, 400, 100)
    
    print(f"عدد التوصيات: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec}")
    
    return analysis['total_items'] > 0


def run_all_tests():
    """
    تشغيل جميع الاختبارات.
    """
    print("بدء الاختبارات الأساسية...")
    print("=" * 40)
    
    tests = [
        ("تحسين تجميع البواقي", test_remainder_optimization),
        ("حساب كفاءة المجموعات", test_group_efficiency),
        ("تحليل العناصر المتبقية", test_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\nاختبار: {test_name}")
            result = test_func()
            if result:
                print(f"✅ نجح اختبار: {test_name}")
                passed += 1
            else:
                print(f"❌ فشل اختبار: {test_name}")
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
    
    print("\n" + "=" * 40)
    print(f"النتائج: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت!")
    else:
        print("⚠️ بعض الاختبارات فشلت")
    
    return passed == total


if __name__ == "__main__":
    """
    تشغيل الاختبارات.
    """
    success = run_all_tests()
    sys.exit(0 if success else 1)
