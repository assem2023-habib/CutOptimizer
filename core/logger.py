"""
Enhanced logging system for RectPack application.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


class RectPackLogger:
    """Enhanced logger for RectPack application with Arabic support."""
    
    def __init__(self, name: str = "RectPack", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers."""
        
        # File handler for detailed logs
        log_file = self.log_dir / f"rectpack_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)
    
    def log_operation_start(self, operation: str, details: Optional[str] = None):
        """Log the start of an operation."""
        msg = f"🚀 بدء العملية: {operation}"
        if details:
            msg += f" - {details}"
        self.info(msg)
    
    def log_operation_end(self, operation: str, success: bool = True, details: Optional[str] = None):
        """Log the end of an operation."""
        status = "✅ اكتملت" if success else "❌ فشلت"
        msg = f"{status} العملية: {operation}"
        if details:
            msg += f" - {details}"
        
        if success:
            self.info(msg)
        else:
            self.error(msg)
    
    def log_validation_results(self, errors: list, warnings: list = None):
        """Log validation results."""
        if errors:
            self.warning(f"⚠️ تم العثور على {len(errors)} خطأ في التحقق:")
            for error in errors:
                self.warning(f"  - {error}")
        
        if warnings:
            self.info(f"ℹ️ تم العثور على {len(warnings)} تحذير:")
            for warning in warnings:
                self.info(f"  - {warning}")
        
        if not errors and not warnings:
            self.info("✅ التحقق من صحة البيانات مكتمل بنجاح")
    
    def log_grouping_progress(self, groups_created: int, items_remaining: int, iteration: int = None):
        """Log grouping algorithm progress."""
        msg = f"📊 التقدم: {groups_created} مجموعة تم إنشاؤها، {items_remaining} عنصر متبقي"
        if iteration:
            msg += f" (التكرار {iteration})"
        self.info(msg)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True, error: str = None):
        """Log file operations."""
        if success:
            self.info(f"📁 {operation}: {file_path}")
        else:
            self.error(f"❌ فشل {operation}: {file_path} - {error}")
    
    def log_performance_metrics(self, operation: str, duration: float, items_processed: int = None):
        """Log performance metrics."""
        msg = f"⏱️ {operation} - المدة: {duration:.2f} ثانية"
        if items_processed:
            msg += f", العناصر المعالجة: {items_processed}"
            msg += f", المعدل: {items_processed/duration:.1f} عنصر/ثانية"
        self.info(msg)


# Global logger instance
logger = RectPackLogger()