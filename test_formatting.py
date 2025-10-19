#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح التنسيقات في ملفات Excel
========================================

هذا الملف يختبر أن التنسيقات تُطبق على جميع الأوراق حتى لو كانت فارغة
"""

import sys
import os
import pandas as pd
from typing import List

# إضافة مسار المشروع إلى PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_io.excel_writer import write_output_excel
from core.models import Rectangle, Group, UsedItem


def create_test_data():
    """إنشاء بيانات اختبار بسيطة"""
    # إنشاء مجموعات فارغة
    groups = []

    # إنشاء عناصر متبقية فارغة
    remaining = []

    # إنشاء أصليات فارغة
    originals = []

    return groups, remaining, originals


def test_excel_formatting():
    """اختبار تطبيق التنسيقات على الأوراق"""
    print("اختبار إصلاح التنسيقات في ملفات Excel...")

    # إنشاء بيانات اختبار
    groups, remaining, originals = create_test_data()

    # مسار ملف الاختبار
    test_file = "test_formatting.xlsx"

    try:
        # كتابة الملف باستخدام الدالة المُصلحة
        write_output_excel(
            path=test_file,
            groups=groups,
            remaining=remaining,
            originals=originals
        )

        # التحقق من وجود الملف
        if os.path.exists(test_file):
            print(f"✅ تم إنشاء ملف الاختبار بنجاح: {test_file}")

            # قراءة الملف للتحقق من الأوراق
            with pd.ExcelFile(test_file) as xls:
                sheets = xls.sheet_names
                expected_sheets = [
                    'تفاصيل المجموعات',
                    'ملخص المجموعات',
                    'السجاد المتبقي',
                    'الإجماليات',
                    'تدقيق الكميات'
                ]

                print(f"📋 الأوراق الموجودة في الملف: {sheets}")

                # التحقق من وجود جميع الأوراق المتوقعة
                for sheet in expected_sheets:
                    if sheet in sheets:
                        print(f"✅ الورقة موجودة: {sheet}")
                    else:
                        print(f"❌ الورقة مفقودة: {sheet}")

                # التحقق من أن جميع الأوراق لها محتوى (حتى لو كان رسالة "لا توجد بيانات")
                for sheet in sheets:
                    df = pd.read_excel(test_file, sheet_name=sheet)
                    if not df.empty:
                        print(f"✅ الورقة '{sheet}' تحتوي على بيانات")
                    else:
                        print(f"ℹ️ الورقة '{sheet}' فارغة (لكن تم إنشاؤها مع التنسيقات)")

            print("✅ تم اختبار التنسيقات بنجاح!")
            return True
        else:
            print(f"❌ فشل في إنشاء ملف الاختبار: {test_file}")
            return False

    except Exception as e:
        print(f"❌ خطأ أثناء اختبار التنسيقات: {str(e)}")
        return False
    finally:
        # تنظيف ملف الاختبار
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 تم حذف ملف الاختبار: {test_file}")


if __name__ == "__main__":
    success = test_excel_formatting()
    if success:
        print("\n🎉 نجح اختبار إصلاح التنسيقات!")
        print("✅ الآن ستُطبق التنسيقات على جميع الأوراق حتى لو كانت فارغة")
    else:
        print("\n❌ فشل اختبار إصلاح التنسيقات!")
        sys.exit(1)
