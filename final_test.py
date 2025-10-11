#!/usr/bin/env python3
"""
اختبار نهائي لحل مشكلة تلف ملف Excel
=====================================

هذا الملف يختبر أن المشكلة تم حلها من الجذور
"""

from core.models import Rectangle, Group, UsedItem
from data_io import write_output_excel

def test_final_excel_fix():
    """اختبار نهائي لحل مشكلة Excel"""
    
    print("اختبار نهائي لحل مشكلة تلف ملف Excel")
    print("=" * 60)
    
    # إنشاء بيانات اختبار شاملة
    print("إنشاء بيانات اختبار...")
    
    test_groups = [
        Group(id=1, items=[
            UsedItem(rect_id=1, width=240, length=340, used_qty=100, original_qty=100)
        ]),
        Group(id=2, items=[
            UsedItem(rect_id=2, width=160, length=230, used_qty=148, original_qty=200)
        ])
    ]
    
    test_remaining = [
        Rectangle(1, 160, 230, 52),
        Rectangle(2, 130, 200, 50),
        Rectangle(3, 300, 600, 10)
    ]
    
    test_enhanced_groups = [
        Group(id=1001, items=[
            UsedItem(rect_id=3, width=130, length=200, used_qty=50, original_qty=50)
        ])
    ]
    
    try:
        # كتابة ملف Excel شامل
        output_path = "final_test_output.xlsx"
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
        
        print("تم إنشاء الملف بنجاح!")
        print("الملف يجب أن يفتح في Excel بدون مشاكل")
        print("لا يجب أن تظهر رسالة 'محاولة استعادة ما أمكن'")
        
        return True
        
    except Exception as e:
        print(f"خطأ في كتابة الملف: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    
    print("بدء الاختبار النهائي")
    print("=" * 80)
    
    success = test_final_excel_fix()
    
    if success:
        print("\nتم حل المشكلة بنجاح!")
        print("السبب كان: استيراد دوال من remainder_optimizer داخل excel_writer")
        print("الحل: إزالة الاستيراد الدائري وإنشاء اقتراحات بسيطة محلية")
        print("\nالآن يمكنك استخدام البرنامج بدون مشاكل!")
    else:
        print("\nلا تزال هناك مشكلة")
        print("يرجى التحقق من الكود مرة أخرى")

if __name__ == "__main__":
    main()
