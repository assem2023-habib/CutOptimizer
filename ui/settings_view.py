"""
نافذة الإعدادات - تحتوي على جميع خيارات الإعدادات بما في ذلك تغيير الخلفية
"""
import json
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLineEdit,
                               QMessageBox, QPushButton)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from ui.components.app_button import AppButton
from core.utilies.background_utils import change_background


class SettingsView(QDialog):
    """نافذة الإعدادات الرئيسية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("⚙️ الإعدادات")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 10px;
                background-color: #2D2D2D;
                border-radius: 4px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
            }
        """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title_label = QLabel("⚙️ إعدادات التطبيق")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #00FF91; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # قسم المظهر
        appearance_group = self._create_appearance_section()
        main_layout.addWidget(appearance_group)
        
        # قسم مقاسات المكنات
        machine_sizes_group = self._create_machine_sizes_section()
        main_layout.addWidget(machine_sizes_group)
        
        # مساحة فارغة للتوسع المستقبلي
        main_layout.addStretch()
        
        # أزرار الإجراءات
        buttons_layout = self._create_action_buttons()
        main_layout.addLayout(buttons_layout)
    
    def _create_appearance_section(self):
        """إنشاء قسم إعدادات المظهر"""
        appearance_group = QGroupBox("🎨 المظهر والخلفية")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # عنوان فرعي
        desc_label = QLabel("قم بتخصيص مظهر التطبيق حسب تفضيلاتك")
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # زر تغيير الخلفية
        bg_layout = QHBoxLayout()
        bg_label = QLabel("🖼️ صورة الخلفية:")
        bg_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        
        self.change_bg_btn = AppButton(
            text="📁 تغيير الخلفية",
            color="#2D5F8D",
            hover_color="#3A7DAB",
            text_color="#FFFFFF",
            fixed_size=QSize(150, 35)
        )
        self.change_bg_btn.clicked.connect(self._change_background)
        
        bg_layout.addWidget(bg_label)
        bg_layout.addStretch()
        bg_layout.addWidget(self.change_bg_btn)
        
        layout.addLayout(bg_layout)
        
        # ملاحظة
        note_label = QLabel("💡 نصيحة: اختر صورة خلفية مناسبة لتحسين تجربتك")
        note_label.setStyleSheet("color: #808080; font-size: 10px; font-style: italic;")
        layout.addWidget(note_label)
        
        appearance_group.setLayout(layout)
        return appearance_group
    
    def _create_action_buttons(self):
        """إنشاء أزرار الإجراءات (إغلاق)"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = AppButton(
            text="✖️ إغلاق",
            color="#D32F2F",
            hover_color="#F44336",
            text_color="#FFFFFF",
            fixed_size=QSize(120, 38)
        )
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(close_btn)
        return buttons_layout
    
    
    def _create_machine_sizes_section(self):
        """إنشاء قسم إدارة مقاسات المكنات"""
        sizes_group = QGroupBox("📏 مقاسات المكنات")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # عنوان فرعي
        desc_label = QLabel("إدارة المقاسات المحددة مسبقاً للمكنات")
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # جدول المقاسات
        self.sizes_table = QTableWidget()
        self.sizes_table.setColumnCount(4)
        self.sizes_table.setHorizontalHeaderLabels(["الاسم", "الحد الأدنى", "الحد الأعلى", ""])
        self.sizes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sizes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.sizes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.sizes_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.sizes_table.setMaximumHeight(150)
        self.sizes_table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                gridline-color: #3A3A3A;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                color: #FFFFFF;
                padding: 5px;
                border: 1px solid #3A3A3A;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.sizes_table)
        
        # أزرار الإدارة
        buttons_layout = QHBoxLayout()
        
        add_btn = AppButton(
            text="➕ إضافة مقاس جديد",
            color="#2E7D32",
            hover_color="#388E3C",
            text_color="#FFFFFF",
            fixed_size=QSize(150, 35)
        )
        add_btn.clicked.connect(self._add_machine_size_dialog)
        
        refresh_btn = AppButton(
            text="🔄 تحديث",
            color="#1976D2",
            hover_color="#2196F3",
            text_color="#FFFFFF",
            fixed_size=QSize(100, 35)
        )
        refresh_btn.clicked.connect(self._load_machine_sizes)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        sizes_group.setLayout(layout)
        
        # تحميل المقاسات الحالية
        self._load_machine_sizes()
        
        return sizes_group
    
    def _load_machine_sizes(self):
        """تحميل المقاسات من config.json"""
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        
        # المقاسات الافتراضية
        default_sizes = [
            {"name": "370x400", "min_width": 370, "max_width": 400},
            {"name": "470x500", "min_width": 470, "max_width": 500}
        ]
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                sizes = config.get("machine_sizes", default_sizes)
            else:
                sizes = default_sizes
                # حفظ المقاسات الافتراضية
                self._save_machine_sizes(sizes)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل تحميل المقاسات: {e}")
            sizes = default_sizes
        
        # ملء الجدول
        self.sizes_table.setRowCount(len(sizes))
        for i, size in enumerate(sizes):
            # العمود 0: الاسم
            self.sizes_table.setItem(i, 0, QTableWidgetItem(size["name"]))
            # العمود 1: الحد الأدنى
            self.sizes_table.setItem(i, 1, QTableWidgetItem(str(size["min_width"])))
            # العمود 2: الحد الأعلى
            self.sizes_table.setItem(i, 2, QTableWidgetItem(str(size["max_width"])))
            # العمود 3: زر الحذف
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #D32F2F;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #F44336;
                }
            """)
            delete_btn.clicked.connect(lambda checked, idx=i: self._delete_machine_size(idx))
            self.sizes_table.setCellWidget(i, 3, delete_btn)
    
    def _save_machine_sizes(self, sizes):
        """حفظ المقاسات في config.json"""
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                config = {}
            
            config["machine_sizes"] = sizes
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل حفظ المقاسات: {e}")
    
    def _add_machine_size_dialog(self):
        """فتح نافذة لإضافة مقاس جديد"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ إضافة مقاس جديد")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # حقل الاسم
        name_label = QLabel("اسم المقاس:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("مثال: 370x400")
        
        # حقل الحد الأدنى
        min_label = QLabel("العرض الأدنى:")
        min_input = QLineEdit()
        min_input.setPlaceholderText("مثال: 370")
        
        # حقل الحد الأعلى
        max_label = QLabel("العرض الأعلى:")
        max_input = QLineEdit()
        max_input.setPlaceholderText("مثال: 400")
        
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(min_label)
        layout.addWidget(min_input)
        layout.addWidget(max_label)
        layout.addWidget(max_input)
        
        # أزرار
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
        
        def save_size():
            name = name_input.text().strip()
            try:
                min_w = int(min_input.text().strip())
                max_w = int(max_input.text().strip())
            except ValueError:
                QMessageBox.warning(dialog, "خطأ", "يرجى إدخال أرقام صحيحة للعرض")
                return
            
            if not name:
                QMessageBox.warning(dialog, "خطأ", "يرجى إدخال اسم المقاس")
                return
            
            if min_w >= max_w:
                QMessageBox.warning(dialog, "خطأ", "العرض الأدنى يجب أن يكون أقل من العرض الأعلى")
                return
            
            # تحميل المقاسات الحالية
            config_path = os.path.join(os.getcwd(), "config", "config.json")
            try:
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    sizes = config.get("machine_sizes", [])
                else:
                    sizes = []
                
                # إضافة المقاس الجديد
                sizes.append({"name": name, "min_width": min_w, "max_width": max_w})
                self._save_machine_sizes(sizes)
                self._load_machine_sizes()
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, "خطأ", f"فشل حفظ المقاس: {e}")
        
        save_btn.clicked.connect(save_size)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _delete_machine_size(self, index):
        """حذف مقاس من القائمة"""
        reply = QMessageBox.question(
            self, 
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المقاس؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            config_path = os.path.join(os.getcwd(), "config", "config.json")
            try:
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    sizes = config.get("machine_sizes", [])
                    
                    if 0 <= index < len(sizes):
                        sizes.pop(index)
                        self._save_machine_sizes(sizes)
                        self._load_machine_sizes()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل حذف المقاس: {e}")
    
    def _change_background(self):
        """تغيير خلفية النافذة الرئيسية"""
        if self.parent_widget:
            change_background(self.parent_widget)
