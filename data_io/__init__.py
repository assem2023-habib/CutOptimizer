"""
حزمة معالجة ملفات Excel
======================

هذه الحزمة تحتوي على جميع الوحدات المسؤولة عن معالجة ملفات Excel
في نظام تحسين القطع.

الوحدات المتاحة:
- excel_reader: قراءة ملفات Excel
- excel_writer: كتابة ملفات Excel  
- remainder_optimizer: تحسين تجميع البواقي
- suggestion_generator: توليد الاقتراحات
- excel_io: الوحدة الرئيسية

المؤلف: نظام تحسين القطع
التاريخ: 2024
الإصدار: 2.0
"""

# استيراد الدوال الرئيسية
from .excel_io import (
    read_input_excel,
    write_output_excel,
    create_enhanced_remainder_groups,
    create_enhanced_remainder_groups_from_rectangles,
    exhaustively_regroup,
    generate_partner_suggestions,
    validate_excel_data,
    get_excel_summary,
    analyze_remaining_items,
    get_optimization_recommendations,
    calculate_group_efficiency,
    optimize_group_formation
)

# استيراد الدوال من الوحدات المنفصلة
from .excel_reader import (
    read_input_excel as read_excel,
    validate_excel_data as validate_data,
    get_excel_summary as get_summary
)

from .excel_writer import (
    write_output_excel as write_excel
)

from .remainder_optimizer import (
    create_enhanced_remainder_groups as create_groups,
    create_enhanced_remainder_groups_from_rectangles as create_groups_from_rectangles,
    exhaustively_regroup as regroup,
    calculate_group_efficiency as calculate_efficiency,
    process_remainder_complete as process_remainder,
    generate_size_suggestions as generate_suggestions,
    analyze_remaining_for_optimization as analyze_optimization
)

from .suggestion_generator import (
    generate_partner_suggestions as generate_suggestions,
    analyze_remaining_items as analyze_items,
    get_optimization_recommendations as get_recommendations
)

# تعريف الإصدار
__version__ = "2.0"
__author__ = "نظام تحسين القطع"
__date__ = "2024"

# قائمة الدوال المتاحة للاستيراد
__all__ = [
    # الدوال الرئيسية
    'read_input_excel',
    'write_output_excel',
    'create_enhanced_remainder_groups',
    'create_enhanced_remainder_groups_from_rectangles',
    'exhaustively_regroup',
    'generate_partner_suggestions',
    'validate_excel_data',
    'get_excel_summary',
    'analyze_remaining_items',
    'get_optimization_recommendations',
    'calculate_group_efficiency',
    'process_remainder_complete',
    'generate_size_suggestions',
    'analyze_remaining_for_optimization',
    
    # الدوال البديلة
    'read_excel',
    'write_excel',
    'create_groups',
    'create_groups_from_rectangles',
    'regroup',
    'generate_suggestions',
    'analyze_items',
    'get_recommendations',
    'validate_data',
    'get_summary',
    'calculate_efficiency',
    'optimize_formation'
]
