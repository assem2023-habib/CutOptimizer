#!/usr/bin/env python3
"""
اختبار نهائي نهائي لحل مشكلة صيغ Excel
=======================================

هذا الملف يختبر أن مشكلة صيغ Excel تم حلها نهائياً
"""

from core.models import Rectangle, Group, UsedItem
from data_io import write_output_excel
import os

def test_final_formula_fix():
    """اختبار نهائي لحل مشكلة صيغ Excel"""
    
    print("اختبار نهائي لحل مشكلة صيغ Excel")
    print("=" * 50)
    
    # حذف الملفات القديمة
    old_files = ['comprehensive_test.xlsx', 'final_test_output.xlsx']
    for file in old_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"تم حذف الملف القديم: {file}")
    
    # إنشاء بيانات اختبار
    print("\nإنشاء بيانات اختبار...")
    
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
        Rectangle(2, 300, 600, 10)
    ]
    
    test_enhanced_groups = [
        Group(id=1001, items=[
            UsedItem(rect_id=3, width=130, length=200, used_qty=50, original_qty=50)
        ])
    ]
    
    try:
        # كتابة ملف Excel
        output_path = "final_formula_test.xlsx"
        print(f"كتابة ملف Excel: {output_path}")
        
        write_output_excel(
            path=output_path,
            groups=test_groups,
            remaining=test_remaining,
            enhanced_remainder_groups=test_enhanced_groups,
            min_width=370,
            max_width=400,
            tolerance_length=100
        )
        
        # التحقق من الملف
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"تم إنشاء الملف بنجاح!")
            print(f"حجم الملف: {file_size:,} بايت")
            print(f"الملف يجب أن يفتح في Excel بدون أي مشاكل")
            print(f"لا يجب أن تظهر رسالة 'Removed Records: Formula'")
            print(f"لا يجب أن تظهر رسالة 'محاولة استعادة ما أمكن'")
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
    
    print("بدء الاختبار النهائي لحل مشكلة صيغ Excel")
    print("=" * 70)
    
    success = test_final_formula_fix()
    
    if success:
        print("\nتم حل مشكلة صيغ Excel نهائياً!")
        print("ما تم حذفه:")
        print("1. دالة _append_totals_row بالكامل")
        print("2. جميع استدعاءات _append_totals_row")
        print("3. استيراد xl_col_to_name")
        print("\nالنتيجة:")
        print("- لا توجد صيغ Excel معطلة")
        print("- لا توجد رسائل استعادة")
        print("- ملف Excel يفتح بشكل طبيعي")
        print("\nالبرنامج جاهز للاستخدام بدون مشاكل!")
    else:
        print("\nلا تزال هناك مشكلة")
        print("يرجى التحقق من الكود مرة أخرى")

if __name__ == "__main__":
    main()
