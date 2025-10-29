"""
CutOptimizer - نظام تحسين القطع
===============================

نظام متقدم لتجميع السجاد باستخدام خوارزميات ذكية لتحسين الاستغلال.
"""

from .models.data_models import Rectangle, UsedItem, Group
from .core.comprehensive_grouper import ComprehensiveGrouper, create_comprehensive_groups
from .core.greedy_grouper import GreedyGrouper

__version__ = "1.0.0"

__all__ = [
    'Rectangle',
    'UsedItem',
    'Group',
    'ComprehensiveGrouper',
    'create_comprehensive_groups',
    'GreedyGrouper'
]
