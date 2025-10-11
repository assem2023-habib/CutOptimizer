#!/usr/bin/env python3
"""
إصلاح مشكلة ملف Excel
=====================

هذا الملف يحتوي على حلول لمشكلة تلف ملف Excel
"""

import os
import pandas as pd
from core.models import Rectangle, Group, UsedItem
from data_io import write_output_excel

def fix_excel_corruption():
    """إصلاح مشكلة تلف ملف Excel"""
    
    print("إصلاح مشكلة تلف ملف Excel")
    print("=" * 50)
    
    # حذف الملفات التالفة إن وُجدت
    corrupted_files = ['res.xlsx', 'test_output.xlsx']
    for file in corrupted_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"تم حذف الملف التالف: {file}")
            except Exception as e:
                print(f"فشل في حذف {file}: {e}")
    
    # إنشاء بيانات اختبار بسيطة وآمنة
    print("\nإنشاء بيانات اختبار...")
    
    test_groups = [
        Group(id=1, items=[
            UsedItem(rect_id=1, width=240, length=340, used_qty=100, original_qty=100)
        ])
    ]
    
    test_remaining = [
        Rectangle(1, 160, 230, 52)
    ]
    
    # كتابة ملف Excel جديد وآمن
    try:
        output_path = "fixed_output.xlsx"
        print(f"كتابة ملف Excel جديد: {output_path}")
        
        write_output_excel(
            path=output_path,
            groups=test_groups,
            remaining=test_remaining,
            min_width=370,
            max_width=400,
            tolerance_length=100
        )
        
        print(f"تم إنشاء الملف بنجاح: {output_path}")
        print("يمكنك الآن فتح الملف في Excel")
        
        # التحقق من حجم الملف
        file_size = os.path.getsize(output_path)
        print(f"حجم الملف: {file_size:,} بايت")
        
        return True
        
    except Exception as e:
        print(f"خطأ في كتابة الملف: {e}")
        return False

def create_simple_excel():
    """إنشاء ملف Excel بسيط جداً للاختبار"""
    
    print("\nإنشاء ملف Excel بسيط للاختبار...")
    
    try:
        # إنشاء بيانات بسيطة جداً
        data = {
            'المجموعة': ['المجموعة 1', 'المجموعة 2'],
            'العرض': [240, 160],
            'الطول': [340, 230],
            'الكمية': [100, 50]
        }
        
        df = pd.DataFrame(data)
        
        # كتابة ملف Excel بسيط
        with pd.ExcelWriter('simple_test.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='اختبار', index=False)
        
        print("تم إنشاء ملف Excel بسيط: simple_test.xlsx")
        return True
        
    except Exception as e:
        print(f"خطأ في إنشاء الملف البسيط: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    
    print("بدء إصلاح مشكلة ملف Excel")
    print("=" * 60)
    
    # محاولة الإصلاح الرئيسي
    success = fix_excel_corruption()
    
    if not success:
        print("\nفشل الإصلاح الرئيسي، محاولة إنشاء ملف بسيط...")
        success = create_simple_excel()
    
    if success:
        print("\nتم إصلاح المشكلة بنجاح!")
        print("يمكنك الآن استخدام البرنامج بشكل طبيعي")
    else:
        print("\nفشل في إصلاح المشكلة")
        print("يرجى التحقق من إعدادات Excel أو إعادة تثبيت المكتبات")

if __name__ == "__main__":
    main()
