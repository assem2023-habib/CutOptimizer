"""
Core Module - النواة الأساسية للنظام
==================================

يحتوي هذا المجلد على:
- نماذج البيانات (models.py)
- خوارزميات التجميع المختلفة
- أدوات المساعدة والتحسين
"""

from .models import Rectangle, UsedItem, Group
from .comprehensive_grouper import ComprehensiveGrouper
from .greedy_grouper import GreedyGrouper

__all__ = [
    'Rectangle',
    'UsedItem',
    'Group',
    'ComprehensiveGrouper',
    'create_comprehensive_groups',
    'GreedyGrouper'
]