from typing import Tuple, Optional
import os
from .models import Rectangle 

def validate_config(min_w: int, max_w: int, tol: int) -> Tuple[bool, Optional[str]]:
    """
    Validates the configuration settings for grouping.

    Args:
        min_w (int): The minimum allowed total width.
        max_w (int): The maximum allowed total width.
        tol (int): The allowed tolerance for total length.

    Returns:
        Tuple[bool, Optional[str]]:
            - True, None  → if the configuration is valid.
            - False, "Error message" → if there is an issue.
    """
    # Check for positive values
    if min_w <= 0:
        return False, f"العرض الأدنى يجب أن يكون أكبر من صفر (القيمة الحالية: {min_w})"
    if max_w <= 0:
        return False, f"العرض الأقصى يجب أن يكون أكبر من صفر (القيمة الحالية: {max_w})"
    
    # Check logical relationship
    if min_w >= max_w:
        return False, f"العرض الأدنى ({min_w}) يجب أن يكون أقل من العرض الأقصى ({max_w})"
    
    # Check reasonable ranges
    if max_w - min_w < 10:
        return False, f"الفرق بين العرض الأدنى والأقصى صغير جداً ({max_w - min_w}). يُنصح بفرق لا يقل عن 10 سم"
    
    if max_w > 10000:
        return False, f"العرض الأقصى كبير جداً ({max_w}). الحد الأقصى المسموح: 10000 سم"
    
    # Check tolerance
    if tol < 0:
        return False, f"هامش التسامح لا يمكن أن يكون سالباً (القيمة الحالية: {tol})"
    if tol > 10000:
        return False, f"هامش التسامح كبير جداً ({tol}). الحد الأقصى المسموح: 10000 سم"
    
    return True, None

def validate_carpets(carpets: list[Rectangle]) -> list[str]:
    """
    Validates a list of Rectangle objects and returns error messages.
    
    Args:
        carpets: List of Rectangle objects to validate
        
    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    
    if not carpets:
        errors.append("لا توجد بيانات سجاد للتحقق منها")
        return errors
    
    seen_ids = set()
    
    for i, c in enumerate(carpets):
        # Check for missing attributes
        if not hasattr(c, 'id') or not hasattr(c, 'width') or not hasattr(c, 'length') or not hasattr(c, 'qty'):
            errors.append(f"الصف {i+1}: بيانات ناقصة (يجب أن تحتوي على id, width, length, qty)")
            continue
            
        # Check for duplicate IDs
        if c.id in seen_ids:
            errors.append(f"معرف مكرر: {c.id}")
        seen_ids.add(c.id)
        
        # Validate dimensions
        if c.width <= 0:
            errors.append(f"معرف {c.id}: العرض يجب أن يكون أكبر من صفر (القيمة الحالية: {c.width})")
        elif c.width > 10000:  # Reasonable upper limit
            errors.append(f"معرف {c.id}: العرض كبير جداً (القيمة الحالية: {c.width})")
            
        if c.length <= 0:
            errors.append(f"معرف {c.id}: الطول يجب أن يكون أكبر من صفر (القيمة الحالية: {c.length})")
        elif c.length > 10000:  # Reasonable upper limit
            errors.append(f"معرف {c.id}: الطول كبير جداً (القيمة الحالية: {c.length})")
            
        if c.qty < 0:
            errors.append(f"معرف {c.id}: الكمية لا يمكن أن تكون سالبة (القيمة الحالية: {c.qty})")
        elif c.qty == 0:
            errors.append(f"معرف {c.id}: تحذير - الكمية صفر")
        elif c.qty > 100000:  # Reasonable upper limit
            errors.append(f"معرف {c.id}: الكمية كبيرة جداً (القيمة الحالية: {c.qty})")
    
    return errors

def validate_file_path(file_path: str, check_exists: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validates file path for input/output operations.
    
    Args:
        file_path: Path to validate
        check_exists: Whether to check if file exists (for input files)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not file_path.strip():
        return False, "مسار الملف فارغ"
    
    file_path = file_path.strip()
    
    # Check file extension
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        return False, "يجب أن يكون الملف من نوع Excel (.xlsx أو .xls)"
    
    if check_exists:
        if not os.path.exists(file_path):
            return False, f"الملف غير موجود: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"المسار لا يشير إلى ملف: {file_path}"
        
        # Check file size (reasonable limit: 100MB)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, f"حجم الملف كبير جداً ({file_size / (1024*1024):.1f} MB). الحد الأقصى: 100 MB"
            if file_size == 0:
                return False, "الملف فارغ"
        except OSError as e:
            return False, f"خطأ في قراءة معلومات الملف: {e}"
    else:
        # For output files, check if directory exists and is writable
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            return False, f"المجلد غير موجود: {directory}"
        
        if directory and not os.access(directory, os.W_OK):
            return False, f"لا يمكن الكتابة في المجلد: {directory}"
    
    return True, None