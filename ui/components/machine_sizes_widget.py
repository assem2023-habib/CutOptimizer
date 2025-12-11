"""
Machine Sizes Widget
Manages machine size presets for the application
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QLineEdit, QMessageBox, QPushButton)
from PySide6.QtCore import QSize
from ui.widgets.app_button import AppButton
from ui.styles.settings_styles import SettingsStyles
from core.config.config_manager import ConfigManager


class MachineSizesWidget(QWidget):
    """Widget for managing machine size presets"""
    
    DEFAULT_SIZES = [
        {"name": "370x400", "min_width": 370, "max_width": 400, "tolerance": 5, "path_length": 0},
        {"name": "470x500", "min_width": 470, "max_width": 500, "tolerance": 5, "path_length": 0}
    ]
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.load_sizes()
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Description
        desc_label = QLabel("إدارة المقاسات المحددة مسبقاً للمكنات")
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Table
        self.table = self._create_table()
        layout.addWidget(self.table)
        
        # Buttons
        buttons = self._create_buttons()
        layout.addLayout(buttons)
    
    def _create_table(self):
        """Creates the sizes table"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["رقم النول", "الحد الأدنى", "الحد الأعلى", "التفاوت", "طول المسار", ""])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.setMaximumHeight(150)
        table.setStyleSheet(SettingsStyles.get_table_stylesheet())
        return table
    
    def _create_buttons(self):
        """Creates management buttons"""
        layout = QHBoxLayout()
        
        add_btn = AppButton(
            text="➕ إضافة مقاس جديد",
            color="#2E7D32",
            hover_color="#388E3C",
            text_color="#FFFFFF",
            fixed_size=QSize(150, 35)
        )
        add_btn.clicked.connect(self._show_add_dialog)
        
        refresh_btn = AppButton(
            text="🔄 تحديث",
            color="#1976D2",
            hover_color="#2196F3",
            text_color="#FFFFFF",
            fixed_size=QSize(100, 35)
        )
        refresh_btn.clicked.connect(self.load_sizes)
        
        layout.addWidget(add_btn)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        
        return layout
    
    def load_sizes(self):
        """Loads sizes from config"""
        sizes = ConfigManager.get_value("machine_sizes", self.DEFAULT_SIZES)
        
        if not sizes:
            sizes = self.DEFAULT_SIZES
            self._save_sizes(sizes)
        else:
            # Ensure path_length exists for backward compatibility
            updated = False
            for size in sizes:
                if "path_length" not in size:
                    size["path_length"] = 0
                    updated = True
            if updated:
                self._save_sizes(sizes)
        
        self._populate_table(sizes)
    
    def _populate_table(self, sizes):
        """Populates the table with sizes"""
        self.table.setRowCount(len(sizes))
        for i, size in enumerate(sizes):
            self._populate_row(i, size)
    
    def _populate_row(self, row, size):
        """Populates a single table row"""
        self.table.setItem(row, 0, QTableWidgetItem(size["name"]))
        self.table.setItem(row, 1, QTableWidgetItem(str(size["min_width"])))
        self.table.setItem(row, 2, QTableWidgetItem(str(size["max_width"])))
        self.table.setItem(row, 3, QTableWidgetItem(str(size.get("tolerance", 5))))
        self.table.setItem(row, 4, QTableWidgetItem(str(size.get("path_length", 0))))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet(SettingsStyles.get_delete_button_stylesheet())
        delete_btn.clicked.connect(lambda: self._delete_size(row))
        self.table.setCellWidget(row, 5, delete_btn)
    
    def _save_sizes(self, sizes):
        """Saves sizes to config"""
        ConfigManager.set_value("machine_sizes", sizes)
    
    def _show_add_dialog(self):
        """Shows dialog to add a new size"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ إضافة مقاس جديد")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(SettingsStyles.get_add_dialog_stylesheet())
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Input fields
        name_input, min_input, max_input, tolerance_input, path_length_input = self._create_input_fields(layout)
        
        # Buttons
        save_btn, cancel_btn = self._create_dialog_buttons(layout)
        
        # Connect
        save_btn.clicked.connect(
            lambda: self._save_new_size(dialog, name_input, min_input, max_input, tolerance_input, path_length_input)
        )
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _create_input_fields(self, layout):
        """Creates input fields for add dialog"""
        name_label = QLabel("رقم النول:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("مثال: 370x400")
        
        min_label = QLabel("العرض الأدنى:")
        min_input = QLineEdit()
        min_input.setPlaceholderText("مثال: 370")
        
        max_label = QLabel("العرض الأعلى:")
        max_input = QLineEdit()
        max_input.setPlaceholderText("مثال: 400")
        
        tolerance_label = QLabel("التفاوت (Tolerance):")
        tolerance_input = QLineEdit()
        tolerance_input.setPlaceholderText("مثال: 5")
        tolerance_input.setText("5")  # Default value

        path_length_label = QLabel("طول المسار (Path Length):")
        path_length_input = QLineEdit()
        path_length_input.setPlaceholderText("مثال: 1200")
        path_length_input.setText("0")
        
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(min_label)
        layout.addWidget(min_input)
        layout.addWidget(max_label)
        layout.addWidget(max_input)
        layout.addWidget(tolerance_label)
        layout.addWidget(tolerance_input)
        layout.addWidget(path_length_label)
        layout.addWidget(path_length_input)
        
        return name_input, min_input, max_input, tolerance_input, path_length_input
    
    def _create_dialog_buttons(self, layout):
        """Creates dialog buttons"""
        buttons_layout = QHBoxLayout()
        
        save_btn = AppButton(
            text="💾 حفظ",
            color="#2E7D32",
            hover_color="#388E3C",
            text_color="#FFFFFF",
            fixed_size=QSize(100, 35)
        )
        
        cancel_btn = AppButton(
            text="✖️ إلغاء",
            color="#D32F2F",
            hover_color="#F44336",
            text_color="#FFFFFF",
            fixed_size=QSize(100, 35)
        )
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        return save_btn, cancel_btn
    
    def _save_new_size(self, dialog, name_input, min_input, max_input, tolerance_input, path_length_input):
        """Validates and saves new size"""
        name = name_input.text().strip()
        
        try:
            min_w = int(min_input.text().strip())
            max_w = int(max_input.text().strip())
            tolerance = int(tolerance_input.text().strip())
            path_length = int(path_length_input.text().strip())
        except ValueError:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال أرقام صحيحة")
            return
        
        if not name:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال اسم المقاس")
            return
        
        if min_w >= max_w:
            QMessageBox.warning(dialog, "خطأ", "العرض الأدنى يجب أن يكون أقل من العرض الأعلى")
            return
        
        if tolerance <= 0:
            QMessageBox.warning(dialog, "خطأ", "التفاوت يجب أن يكون أكبر من صفر")
            return

        if path_length < 0:
            QMessageBox.warning(dialog, "خطأ", "طول المسار يجب أن يكون صفراً أو قيمة موجبة")
            return
        
        # Add new size
        sizes = ConfigManager.get_value("machine_sizes", [])
        sizes.append({
            "name": name,
            "min_width": min_w,
            "max_width": max_w,
            "tolerance": tolerance,
            "path_length": path_length
        })
        
        self._save_sizes(sizes)
        self.load_sizes()
        dialog.accept()
    
    def _delete_size(self, index):
        """Deletes a size"""
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المقاس؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            sizes = ConfigManager.get_value("machine_sizes", [])
            
            if 0 <= index < len(sizes):
                sizes.pop(index)
                self._save_sizes(sizes)
                self.load_sizes()
