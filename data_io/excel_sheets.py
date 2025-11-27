"""
Excel Sheets Module - Compatibility Layer
==========================================
هذا الملف يعيد تصدير جميع دوال إنشاء الصفحات من الوحدات المنفصلة
للحفاظ على التوافقية مع الكود الموجود.

This file re-exports all sheet creation functions from separate modules
to maintain backward compatibility with existing code.
"""

# استيراد جميع الدوال من الوحدات المنفصلة
# Import all functions from separate modules

from .sheets.group_details_sheet import (
    _create_group_details_sheet,
    _detals_sheet_table
)

from .sheets.group_summary_sheet import (
    _create_group_summary_sheet,
    _summary_sheet_table
)

from .sheets.remaining_sheet import (
    _create_remaining_sheet,
    _remaining_sheet_table
)

from .sheets.totals_sheet import (
    _create_totals_sheet
)

from .sheets.audit_sheet import (
    _create_audit_sheet,
    _audit_sheet_table
)

from .sheets.waste_sheet import (
    _generate_waste_sheet,
    _waste_sheet_table
)

from .sheets.suggestion_sheets import (
    _create_remaining_suggestion_sheet,
    _create_enhanset_remaining_suggestion_sheet
)

from .sheets.detailed_waste_sheet import _generate_detailed_waste_sheet

# إعادة تصدير جميع الدوال للحفاظ على التوافقية
# Re-export all functions for backward compatibility
__all__ = [
    '_create_group_details_sheet',
    '_detals_sheet_table',
    '_create_group_summary_sheet',
    '_summary_sheet_table',
    '_create_remaining_sheet',
    '_remaining_sheet_table',
    '_create_totals_sheet',
    '_create_audit_sheet',
    '_audit_sheet_table',
    '_generate_waste_sheet',
    '_waste_sheet_table',
    '_create_remaining_suggestion_sheet',
    '_create_enhanset_remaining_suggestion_sheet',
    '_generate_detailed_waste_sheet'
]