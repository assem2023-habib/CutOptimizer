#!/usr/bin/env python3
"""
اختبار كتابة ملف Excel محسن
============================

هذا الملف يختبر كتابة ملف Excel مع التحسينات الجديدة
"""

from core.models import Rectangle, Group, UsedItem
from data_io import write_output_excel

def test_excel_writing():
    """اختبار كتابة ملف Excel"""
    
    print("اختبار كتابة ملف Excel")
    print("=" * 40)
    
    # إنشاء بيانات اختبار بسيطة
    test_groups = [
        Group(id=1, items=[
            UsedItem(rect_id=1, width=240, length=340, used_qty=100, original_qty=100)
        ]),
        Group(id=2, items=[
            UsedItem(rect_id=2, width=160, length=230, used_qty=148, original_qty=200)
        ])
    ]
    
    test_remaining = [
        Rectangle(1, 160, 230, 52),  # متبقي
        Rectangle(2, 130, 200, 50)   # متبقي
    ]
    
    test_enhanced_groups = [
        Group(id=1001, items=[
            UsedItem(rect_id=3, width=130, length=200, used_qty=50, original_qty=50)
        ])
    ]
    
    try:
        # كتابة ملف Excel
        output_path = "test_output.xlsx"
        write_output_excel(
            path=output_path,
            groups=test_groups,
            remaining=test_remaining,
            enhanced_remainder_groups=test_enhanced_groups,
            min_width=370,
            max_width=400,
            tolerance_length=100
        )
        
        print(f"تم إنشاء ملف Excel بنجاح: {output_path}")
        print("يمكنك الآن فتح الملف في Excel")
        
    except Exception as e:
        print(f"خطأ في كتابة ملف Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_writing()
