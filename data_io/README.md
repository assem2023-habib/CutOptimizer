# حزمة معالجة ملفات Excel - نظام تحسين القطع

## نظرة عامة

هذه الحزمة تحتوي على جميع الوحدات المسؤولة عن معالجة ملفات Excel في نظام تحسين القطع. تم إعادة تنظيم الكود ليكون أكثر تنظيماً وسهولة في الصيانة.

## البنية الجديدة

```
data_io/
├── __init__.py              # ملف التهيئة الرئيسي
├── excel_io.py              # الوحدة الرئيسية (واجهة موحدة)
├── excel_reader.py          # وحدة قراءة ملفات Excel
├── excel_writer.py          # وحدة كتابة ملفات Excel
├── remainder_optimizer.py    # وحدة تحسين تجميع البواقي
├── suggestion_generator.py   # وحدة توليد الاقتراحات
└── README.md                # هذا الملف
```

## الوحدات المتاحة

### 1. excel_reader.py
**الغرض**: قراءة ملفات Excel وتحويلها إلى كائنات Rectangle

**الدوال الرئيسية**:
- `read_input_excel()`: قراءة ملف Excel وتحويله إلى قائمة Rectangle
- `validate_excel_data()`: التحقق من صحة البيانات المقروءة
- `get_excel_summary()`: الحصول على ملخص إحصائي للبيانات

**مثال على الاستخدام**:
```python
from data_io import read_input_excel, validate_excel_data

# قراءة الملف
carpets = read_input_excel("data.xlsx")

# التحقق من صحة البيانات
if validate_excel_data(carpets):
    print(f"تم قراءة {len(carpets)} عنصر بنجاح")
```

### 2. excel_writer.py
**الغرض**: كتابة النتائج إلى ملفات Excel مع تقارير مفصلة

**الدوال الرئيسية**:
- `write_output_excel()`: كتابة النتائج إلى ملف Excel مع جميع الأوراق

**مثال على الاستخدام**:
```python
from data_io import write_output_excel

# كتابة النتائج
write_output_excel(
    "results.xlsx",
    groups=original_groups,
    remaining=remaining_items,
    enhanced_remainder_groups=enhanced_groups
)
```

### 3. remainder_optimizer.py
**الغرض**: خوارزميات تحسين تجميع البواقي

**الدوال الرئيسية**:
- `create_enhanced_remainder_groups()`: خوارزمية محسنة لتجميع البواقي
- `create_enhanced_remainder_groups_from_rectangles()`: دالة مساعدة سهلة الاستخدام
- `exhaustively_regroup()`: تجميع شامل للبواقي
- `calculate_group_efficiency()`: حساب كفاءة المجموعات
- `optimize_group_formation()`: تحسين تشكيل المجموعات

**مثال على الاستخدام**:
```python
from data_io import create_enhanced_remainder_groups_from_rectangles

# تشكيل مجموعات إضافية من البواقي
enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
    remaining_items, 370, 400, 100
)
```

### 4. suggestion_generator.py
**الغرض**: توليد اقتراحات لتشكيل المجموعات

**الدوال الرئيسية**:
- `generate_partner_suggestions()`: توليد اقتراحات ذكية
- `analyze_remaining_items()`: تحليل العناصر المتبقية
- `get_optimization_recommendations()`: الحصول على توصيات التحسين

**مثال على الاستخدام**:
```python
from data_io import generate_partner_suggestions, analyze_remaining_items

# توليد الاقتراحات
suggestions = generate_partner_suggestions(remaining_items, 370, 400, 100)

# تحليل العناصر المتبقية
analysis = analyze_remaining_items(remaining_items)
print(f"إجمالي الكمية: {analysis['total_quantity']}")
```

### 5. excel_io.py
**الغرض**: الوحدة الرئيسية التي توفر واجهة موحدة لجميع الوحدات

**المزايا**:
- واجهة موحدة لجميع الوحدات
- سهولة الاستيراد والاستخدام
- توافق مع الإصدارات السابقة
- دعم كامل للتوثيق

## المزايا الجديدة

### 1. التنظيم المحسن
- فصل الوحدات حسب الوظيفة
- كود أكثر تنظيماً وسهولة في الصيانة
- توثيق شامل لجميع الدوال

### 2. المرونة
- إمكانية استيراد الوحدات منفصلة
- واجهة موحدة للاستخدام السهل
- دعم للتوافق مع الإصدارات السابقة

### 3. الأداء
- خوارزميات محسنة لتجميع البواقي
- إمكانية تكرار العناصر في نفس المجموعة
- تحسين استغلال المواد

### 4. التقارير
- تقارير مفصلة مع تصنيف المجموعات
- إحصائيات شاملة للتحليل
- تدقيق دقيق للكميات

## أمثلة شاملة

### مثال 1: معالجة كاملة للملف
```python
from data_io import (
    read_input_excel, 
    create_enhanced_remainder_groups_from_rectangles,
    write_output_excel
)

# قراءة البيانات
carpets = read_input_excel("input.xlsx")

# تشكيل المجموعات الأصلية (من الكود الرئيسي)
original_groups = [...]  # المجموعات الأصلية
remaining_items = [...]  # البواقي

# تشكيل مجموعات إضافية من البواقي
enhanced_groups, final_remaining = create_enhanced_remainder_groups_from_rectangles(
    remaining_items, 370, 400, 100
)

# كتابة النتائج
write_output_excel(
    "output.xlsx",
    groups=original_groups,
    remaining=final_remaining,
    enhanced_remainder_groups=enhanced_groups
)
```

### مثال 2: تحليل البيانات
```python
from data_io import analyze_remaining_items, get_optimization_recommendations

# تحليل العناصر المتبقية
analysis = analyze_remaining_items(remaining_items)
print(f"إجمالي العناصر: {analysis['total_items']}")
print(f"إجمالي الكمية: {analysis['total_quantity']}")
print(f"المجموعات المحتملة: {analysis['potential_groups']}")

# الحصول على توصيات التحسين
recommendations = get_optimization_recommendations(remaining_items, 370, 400, 100)
for rec in recommendations:
    print(f"توصية: {rec}")
```

### مثال 3: حساب كفاءة المجموعات
```python
from data_io import calculate_group_efficiency

# حساب كفاءة مجموعة
efficiency = calculate_group_efficiency(group)
print(f"استغلال العرض: {efficiency['width_utilization']:.2%}")
print(f"اتساق الأطوال: {efficiency['length_consistency']:.2%}")
print(f"كفاءة المساحة: {efficiency['area_efficiency']:.2%}")
print(f"النقاط الإجمالية: {efficiency['overall_score']:.2%}")
```

## التحديثات المستقبلية

- إضافة المزيد من خوارزميات التحسين
- دعم تنسيقات ملفات أخرى (CSV, JSON)
- واجهة مستخدم رسومية
- تحليلات متقدمة للأداء

## الدعم والمساعدة

للمساعدة أو الاستفسارات، يرجى الرجوع إلى:
- التوثيق المضمن في الكود
- أمثلة الاستخدام في هذا الملف
- التعليقات في الكود المصدري

---

**المؤلف**: نظام تحسين القطع  
**التاريخ**: 2024  
**الإصدار**: 2.0
