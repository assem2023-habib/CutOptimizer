#!/usr/bin/env python3
"""
اختبار بسيط للتحقق من إصلاح مشكلة التكرار في حساب الكميات
"""

import sys
import os

# إضافة المجلد الحالي للمسار
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from models.data_models import Rectangle

def simple_repetition_test():
    """اختبار بسيط للتحقق من حساب التكرار."""
    print("🔄 اختبار التكرار في حساب الكميات...")

    # بيانات بسيطة مع عنصر واحد لاختبار التكرار
    carpets = [
        Rectangle(id=1, width=100, length=200, qty=10),  # عرض مناسب للتكرار (2x100=200, 3x100=300)
    ]

    print("\n📊 البيانات:")
    for carpet in carpets:
        print(f"  العنصر {carpet.id}: عرض={carpet.width}, طول={carpet.length}, كمية={carpet.qty}")

    # نطاق عرض يسمح بالتكرار
    min_width = 200  # يسمح بتكرار 2 مرات
    max_width = 300  # يسمح بتكرار 3 مرات

    print(f"\n🔧 نطاق العرض: {min_width} - {max_width}")

    try:
        from core.width_based_grouper import WidthBasedGrouper

        grouper = WidthBasedGrouper(min_width=min_width, max_width=max_width, tolerance_length=10)
        groups, remaining, stats = grouper.group_carpets(carpets)

        print("
📈 النتائج:"        print(f"  المجموعات المُشكلة: {len(groups)}")
        print(f"  الأصلية: {stats['total_original_quantity']}")
        print(f"  المستخدمة: {stats['total_used_quantity']}")
        print(f"  المتبقية: {stats['total_remaining_quantity']}")
        print(f"  نسبة الاستغلال: {stats['utilization_percentage']:.1f}%")

        # التحقق من صحة الكميات
        expected_total = stats['total_original_quantity']
        actual_total = stats['total_used_quantity'] + stats['total_remaining_quantity']

        print("
🔍 التحقق من الكميات:"        print(f"  المتوقع: {expected_total}")
        print(f"  الفعلي: {actual_total}")

        if actual_total == expected_total:
            print("  ✅ الكميات صحيحة!")

            # عرض تفاصيل كل عنصر
            print("
📋 إحصائيات كل عنصر:"            for item_id, item_stats in stats['per_item_stats'].items():
                calculated_remaining = item_stats['original_qty'] - item_stats['used_qty']
                status = "✅" if calculated_remaining == item_stats['remaining_qty'] else "❌"
                print(f"  {status} العنصر {item_id}: {item_stats['used_qty']}/{item_stats['original_qty']} (متبقي: {item_stats['remaining_qty']})")

            # عرض تفاصيل المجموعات
            print("
📋 تفاصيل المجموعات:"            for group in groups:
                print(f"\n  مجموعة {group.id}: عرض إجمالي = {group.total_width()}")
                print(f"    الكمية المستخدمة: {group.total_used_qty()}")

                unique_items = {}
                for item in group.items:
                    if item.rect_id not in unique_items:
                        unique_items[item.rect_id] = {'count': 0, 'qty': 0, 'width': item.width, 'length': item.length}
                    unique_items[item.rect_id]['count'] += 1
                    unique_items[item.rect_id]['qty'] += item.used_qty

                for rect_id, info in unique_items.items():
                    print(f"    - العنصر {rect_id}: عرض={info['width']}, طول={info['length']}")
                    print(f"      التكرار: {info['count']} مرة, الكمية: {info['qty']}")

            return True
        else:
            print(f"  ❌ خطأ في الكميات: {actual_total} ≠ {expected_total}")
            return False

    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_repetition_test()
    print(f"\n{'='*50}")
    if success:
        print("✅ تم حل مشكلة التكرار!")
    else:
        print("❌ ما زالت هناك مشكلة في التكرار!")
    print(f"{'='*50}")
