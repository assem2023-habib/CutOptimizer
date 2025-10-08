"""
Advanced export functionality for RectPack results.
Supports CSV, JSON, and detailed reporting formats.
"""

import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from core.models import Group, Rectangle
from core.logger import logger


class AdvancedExporter:
    """Advanced exporter for RectPack results with multiple format support."""
    
    def __init__(self):
        self.export_timestamp = datetime.now()
    
    def export_to_csv(self, groups: List[Group], remaining: List[Rectangle], 
                     output_path: str, config: Dict[str, Any] = None) -> bool:
        """
        Export results to CSV format.
        
        Args:
            groups: List of created groups
            remaining: List of remaining rectangles
            output_path: Path for CSV file
            config: Configuration parameters used
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.log_operation_start("تصدير CSV", output_path)
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(['# تقرير تجميع السجاد - RectPack'])
                writer.writerow(['# تاريخ الإنشاء:', self.export_timestamp.strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                # Write configuration
                if config:
                    writer.writerow(['# الإعدادات المستخدمة'])
                    for key, value in config.items():
                        writer.writerow([f'# {key}:', str(value)])
                    writer.writerow([])
                
                # Write groups summary
                writer.writerow(['# ملخص المجموعات'])
                writer.writerow(['رقم المجموعة', 'عدد الأنواع', 'العرض الإجمالي', 'الطول المرجعي', 'المساحة الإجمالية'])
                
                for group in groups:
                    total_area = sum(item.width * item.length * item.used_qty for item in group.items)
                    writer.writerow([
                        f'المجموعة_{group.id}',
                        len(group.items),
                        group.total_width(),
                        group.ref_length(),
                        total_area
                    ])
                
                writer.writerow([])
                
                # Write detailed group information
                writer.writerow(['# تفاصيل المجموعات'])
                writer.writerow(['رقم المجموعة', 'معرف القطعة', 'العرض', 'الطول', 'الكمية المستخدمة', 'الكمية الأصلية'])
                
                for group in groups:
                    for item in group.items:
                        writer.writerow([
                            f'المجموعة_{group.id}',
                            item.rect_id,
                            item.width,
                            item.length,
                            item.used_qty,
                            item.original_qty
                        ])
                
                writer.writerow([])
                
                # Write remaining items
                if remaining:
                    writer.writerow(['# العناصر المتبقية'])
                    writer.writerow(['معرف القطعة', 'العرض', 'الطول', 'الكمية المتبقية'])
                    
                    for rect in remaining:
                        writer.writerow([rect.id, rect.width, rect.length, rect.qty])
                else:
                    writer.writerow(['# لا توجد عناصر متبقية - تم استخدام جميع القطع!'])
            
            logger.log_file_operation("تصدير CSV", output_path, success=True)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تصدير CSV: {e}", exc_info=True)
            return False
    
    def export_to_json(self, groups: List[Group], remaining: List[Rectangle], 
                      output_path: str, config: Dict[str, Any] = None) -> bool:
        """
        Export results to JSON format.
        
        Args:
            groups: List of created groups
            remaining: List of remaining rectangles
            output_path: Path for JSON file
            config: Configuration parameters used
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.log_operation_start("تصدير JSON", output_path)
            
            # Prepare data structure
            export_data = {
                "metadata": {
                    "export_timestamp": self.export_timestamp.isoformat(),
                    "version": "1.0",
                    "tool": "RectPack",
                    "description": "نتائج تجميع السجاد"
                },
                "configuration": config or {},
                "summary": {
                    "total_groups": len(groups),
                    "total_remaining_items": len(remaining),
                    "total_items_processed": sum(len(g.items) for g in groups) + len(remaining)
                },
                "groups": [],
                "remaining_items": []
            }
            
            # Add groups data
            for group in groups:
                group_data = {
                    "id": group.id,
                    "total_width": group.total_width(),
                    "reference_length": group.ref_length(),
                    "item_count": len(group.items),
                    "total_area": sum(item.width * item.length * item.used_qty for item in group.items),
                    "items": []
                }
                
                for item in group.items:
                    item_data = {
                        "rect_id": item.rect_id,
                        "width": item.width,
                        "length": item.length,
                        "used_quantity": item.used_qty,
                        "original_quantity": item.original_qty,
                        "area": item.width * item.length * item.used_qty
                    }
                    group_data["items"].append(item_data)
                
                export_data["groups"].append(group_data)
            
            # Add remaining items
            for rect in remaining:
                remaining_data = {
                    "id": rect.id,
                    "width": rect.width,
                    "length": rect.length,
                    "remaining_quantity": rect.qty,
                    "area": rect.width * rect.length * rect.qty
                }
                export_data["remaining_items"].append(remaining_data)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.log_file_operation("تصدير JSON", output_path, success=True)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تصدير JSON: {e}", exc_info=True)
            return False
    
    def export_detailed_report(self, groups: List[Group], remaining: List[Rectangle], 
                             output_path: str, config: Dict[str, Any] = None) -> bool:
        """
        Export detailed text report.
        
        Args:
            groups: List of created groups
            remaining: List of remaining rectangles
            output_path: Path for text file
            config: Configuration parameters used
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.log_operation_start("تصدير تقرير مفصل", output_path)
            
            with open(output_path, 'w', encoding='utf-8') as txtfile:
                # Header
                txtfile.write("=" * 60 + "\n")
                txtfile.write("تقرير تجميع السجاد المفصل - RectPack\n")
                txtfile.write("=" * 60 + "\n\n")
                
                txtfile.write(f"تاريخ الإنشاء: {self.export_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Configuration
                if config:
                    txtfile.write("الإعدادات المستخدمة:\n")
                    txtfile.write("-" * 20 + "\n")
                    for key, value in config.items():
                        txtfile.write(f"{key}: {value}\n")
                    txtfile.write("\n")
                
                # Summary
                total_area_used = sum(
                    sum(item.width * item.length * item.used_qty for item in group.items)
                    for group in groups
                )
                total_area_remaining = sum(rect.width * rect.length * rect.qty for rect in remaining)
                
                txtfile.write("الملخص العام:\n")
                txtfile.write("-" * 15 + "\n")
                txtfile.write(f"عدد المجموعات المُنشأة: {len(groups)}\n")
                txtfile.write(f"عدد الأنواع المتبقية: {len(remaining)}\n")
                txtfile.write(f"المساحة المستخدمة: {total_area_used:,} سم²\n")
                txtfile.write(f"المساحة المتبقية: {total_area_remaining:,} سم²\n")
                if total_area_used + total_area_remaining > 0:
                    efficiency = (total_area_used / (total_area_used + total_area_remaining)) * 100
                    txtfile.write(f"كفاءة الاستخدام: {efficiency:.1f}%\n")
                txtfile.write("\n")
                
                # Groups details
                txtfile.write("تفاصيل المجموعات:\n")
                txtfile.write("=" * 20 + "\n\n")
                
                for i, group in enumerate(groups, 1):
                    txtfile.write(f"المجموعة {group.id}:\n")
                    txtfile.write(f"  العرض الإجمالي: {group.total_width()} سم\n")
                    txtfile.write(f"  الطول المرجعي: {group.ref_length()} سم\n")
                    txtfile.write(f"  عدد الأنواع: {len(group.items)}\n")
                    
                    group_area = sum(item.width * item.length * item.used_qty for item in group.items)
                    txtfile.write(f"  المساحة الإجمالية: {group_area:,} سم²\n")
                    
                    txtfile.write("  القطع المستخدمة:\n")
                    for item in group.items:
                        txtfile.write(f"    - معرف {item.rect_id}: {item.width}×{item.length} "
                                    f"(استُخدم {item.used_qty} من أصل {item.original_qty})\n")
                    txtfile.write("\n")
                
                # Remaining items
                if remaining:
                    txtfile.write("العناصر المتبقية:\n")
                    txtfile.write("=" * 17 + "\n")
                    for rect in remaining:
                        area = rect.width * rect.length * rect.qty
                        txtfile.write(f"معرف {rect.id}: {rect.width}×{rect.length} "
                                    f"(كمية: {rect.qty}, مساحة: {area:,} سم²)\n")
                else:
                    txtfile.write("🎉 لا توجد عناصر متبقية - تم استخدام جميع القطع!\n")
                
                txtfile.write("\n" + "=" * 60 + "\n")
                txtfile.write("تم إنشاء هذا التقرير بواسطة RectPack\n")
            
            logger.log_file_operation("تصدير تقرير مفصل", output_path, success=True)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تصدير التقرير المفصل: {e}", exc_info=True)
            return False


# Global exporter instance
exporter = AdvancedExporter()