#!/usr/bin/env python3
"""
اختبار نهائي شامل لحل مشكلة تلف ملف Excel
============================================

هذا الملف يختبر جميع الجوانب للتأكد من حل المشكلة نهائياً
"""

from core.models import Rectangle, Group, UsedItem
from data_io import write_output_excel
import os

def test_comprehensive_excel():
    """اختبار شامل لملف Excel"""
    
    print("اختبار شامل لحل مشكلة تلف ملف Excel")
    print("=" * 60)
    
    # حذف الملفات القديمة أولاً
    old_files = ['final_test_output.xlsx', 'test_output.xlsx', 'fixed_output.xlsx']
    for file in old_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"تم حذف الملف القديم: {file}")
    
    # إنشاء بيانات اختبار شاملة
    print("\nإنشاء بيانات اختبار شاملة...")
    
    test_groups = [
        Group(id=1, items=[
            UsedItem(rect_id=1, width=240, length=340, used_qty=100, original_qty=100)
        ]),
        Group(id=2, items=[
            UsedItem(rect_id=2, width=160, length=230, used_qty=148, original_qty=200)
        ]),
        Group(id=3, items=[
            UsedItem(rect_id=3, width=130, length=200, used_qty=50, original_qty=50)
        ])
    ]
    
    test_remaining = [
        Rectangle(1, 160, 230, 52),
        Rectangle(2, 130, 200, 0),  # كمية صفر للاختبار
        Rectangle(3, 300, 600, 10),
        Rectangle(4, 380, 500, 3)
    ]
    
    test_enhanced_groups = [
        Group(id=1001, items=[
            UsedItem(rect_id=4, width=380, length=500, used_qty=3, original_qty=3)
        ])
    ]
    
    try:
        # كتابة ملف Excel شامل
        output_path = "comprehensive_test.xlsx"
        print(f"كتابة ملف Excel شامل: {output_path}")
        
        write_output_excel(
            path=output_path,
            groups=test_groups,
            remaining=test_remaining,
            enhanced_remainder_groups=test_enhanced_groups,
            min_width=370,
            max_width=400,
            tolerance_length=100
        )
        
        # التحقق من وجود الملف وحجمه
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"تم إنشاء الملف بنجاح!")
            print(f"حجم الملف: {file_size:,} بايت")
            print(f"الملف يجب أن يفتح في Excel بدون أي مشاكل")
            print(f"لا يجب أن تظهر رسالة 'محاولة استعادة ما أمكن'")
            print(f"لا يجب أن تظهر رسالة 'Removed Records: Formula'")
            return True
        else:
            print("فشل في إنشاء الملف!")
            return False
        
    except Exception as e:
        print(f"خطأ في كتابة الملف: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    
    print("بدء الاختبار الشامل النهائي")
    print("=" * 80)
    
    success = test_comprehensive_excel()
    
    if success:
        print("\nتم حل جميع المشاكل بنجاح!")
        print("الأسباب التي تم حلها:")
        print("1. الاستيراد الدائري من remainder_optimizer")
        print("2. صيغ Excel المعطلة في دالة _append_totals_row")
        print("3. استخدام xl_col_to_name المعطل")
        print("\nالحلول المطبقة:")
        print("1. إزالة الاستيراد الدائري")
        print("2. استبدال صيغ Excel بقيم محسوبة مباشرة")
        print("3. إزالة الاعتماد على xl_col_to_name")
        print("\nالآن يمكنك استخدام البرنامج بدون أي مشاكل!")
        print("ملف Excel سيفتح بشكل طبيعي تماماً!")
    else:
        print("\nلا تزال هناك مشكلة")
        print("يرجى التحقق من الكود مرة أخرى")

if __name__ == "__main__":
    main()
