"""
نافذة الإعدادات - تحتوي على جميع خيارات الإعدادات بما في ذلك تغيير الخلفية
"""
import json
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLineEdit,
                               QMessageBox, QPushButton, QRadioButton, 
                               QButtonGroup, QComboBox, QWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from ui.components.app_button import AppButton
from core.utilies.background_utils import change_background


class SettingsView(QDialog):
    """نافذة الإعدادات الرئيسية"""
    
    # Constants
    DEFAULT_MACHINE_SIZES = [
        {"name": "370x400", "min_width": 370, "max_width": 400},
        {"name": "470x500", "min_width": 470, "max_width": 500}
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._setup_ui()
    
    # ============================================================================
    # Stylesheet Methods
    # ============================================================================
    
    @staticmethod
    def _get_dialog_stylesheet():
        """Returns the main dialog stylesheet"""
        return """
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
        """
    
    @staticmethod
    def _get_combo_stylesheet():
        """Returns QComboBox stylesheet"""
        return """
            QComboBox {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
        """
    
    @staticmethod
    def _get_table_stylesheet():
        """Returns QTableWidget stylesheet"""
        return """
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
        """
    
    @staticmethod
    def _get_delete_button_stylesheet():
        """Returns delete button stylesheet"""
        return """
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
        """
    
    @staticmethod
    def _get_add_dialog_stylesheet():
        """Returns add dialog stylesheet"""
        return """
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
        """
    
    # ============================================================================
    # Config Helper Methods
    # ============================================================================
    
    @staticmethod
    def _get_config_path():
        """Returns the path to config.json"""
        return os.path.join(os.getcwd(), "config", "config.json")
    
    def _load_config(self):
        """Loads and returns the config dictionary"""
        config_path = self._get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_config(self, config):
        """Saves the config dictionary to file"""
        config_path = self._get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل حفظ الإعدادات: {e}")
    
    # ============================================================================
    # UI Setup
    # ============================================================================
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("⚙️ الإعدادات")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(self._get_dialog_stylesheet())
        
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
    
    # ============================================================================
    # Appearance Section
    # ============================================================================
    
    def _create_appearance_section(self):
        """إنشاء قسم إعدادات المظهر"""
        appearance_group = QGroupBox("🎨 المظهر والخلفية")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # عنوان فرعي
        desc_label = QLabel("قم بتخصيص مظهر التطبيق حسب تفضيلاتك")
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # خيارات نوع الخلفية (Radio buttons)
        self._create_background_type_selection(layout)
        
        # حاوية خيار الصورة
        self.image_container = self._create_image_background_controls()
        layout.addWidget(self.image_container)
        
        # حاوية خيار التدرج
        self.gradient_container = self._create_gradient_controls()
        layout.addWidget(self.gradient_container)
        
        # ربط الأحداث
        self.bg_type_group.buttonClicked.connect(self._on_bg_type_changed)
        
        # الحالة الافتراضية
        self._setup_initial_background_state()
        
        # ملاحظة
        note_label = QLabel("💡 نصيحة: اختر نمط الخلفية الذي يريح عينيك")
        note_label.setStyleSheet("color: #808080; font-size: 10px; font-style: italic;")
        layout.addWidget(note_label)
        
        appearance_group.setLayout(layout)
        return appearance_group
    
    def _create_background_type_selection(self, layout):
        """Creates radio buttons for background type selection"""
        type_layout = QHBoxLayout()
        self.bg_type_group = QButtonGroup(self)
        
        self.radio_image = QRadioButton("صورة خلفية")
        self.radio_image.setStyleSheet("color: white; font-size: 12px;")
        self.radio_gradient = QRadioButton("تدرج لوني")
        self.radio_gradient.setStyleSheet("color: white; font-size: 12px;")
        
        self.bg_type_group.addButton(self.radio_image)
        self.bg_type_group.addButton(self.radio_gradient)
        
        type_layout.addWidget(self.radio_image)
        type_layout.addWidget(self.radio_gradient)
        type_layout.addStretch()
        layout.addLayout(type_layout)
    
    def _create_image_background_controls(self):
        """Creates the image background controls container"""
        container = QWidget()
        image_layout = QHBoxLayout(container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        image_layout.addWidget(bg_label)
        image_layout.addStretch()
        image_layout.addWidget(self.change_bg_btn)
        
        return container
    
    def _create_gradient_controls(self):
        """Creates the gradient background controls container"""
        container = QWidget()
        gradient_layout = QHBoxLayout(container)
        gradient_layout.setContentsMargins(0, 0, 0, 0)
        
        grad_label = QLabel("🎨 اختر التدرج:")
        grad_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        
        self.gradient_combo = QComboBox()
        self.gradient_combo.setMinimumWidth(200)
        self.gradient_combo.setStyleSheet(self._get_combo_stylesheet())
        
        # استيراد التدرجات من الملف المركزي
        from ui.constants.gradients import GRADIENTS
        self.gradients = GRADIENTS
        
        for name, _ in self.gradients:
            self.gradient_combo.addItem(name)
            
        self.gradient_combo.currentIndexChanged.connect(self._apply_gradient)
        
        gradient_layout.addWidget(grad_label)
        gradient_layout.addStretch()
        gradient_layout.addWidget(self.gradient_combo)
        
        return container
    
    def _setup_initial_background_state(self):
        """Sets up initial radio button state based on current config"""
        config = self._load_config()
        current_bg_image = config.get("background_image", "")
        
        if current_bg_image:
            self.radio_image.setChecked(True)
            self.gradient_container.setVisible(False)
        else:
            self.radio_gradient.setChecked(True)
            self.image_container.setVisible(False)
    
    def _on_bg_type_changed(self, button):
        """معالجة تغيير نوع الخلفية"""
        if button == self.radio_image:
            self.image_container.setVisible(True)
            self.gradient_container.setVisible(False)
        else:
            self.image_container.setVisible(False)
            self.gradient_container.setVisible(True)
            self._apply_gradient(self.gradient_combo.currentIndex())
    
    def _apply_gradient(self, index):
        """تطبيق التدرج المختار"""
        if index >= 0 and index < len(self.gradients):
            gradient_style = self.gradients[index][1]
            
            if self.parent_widget:
                from core.utilies.background_utils import save_background_gradient
                save_background_gradient(index)
                self.parent_widget.setStyleSheet(f"#MainWindow {{ background: {gradient_style}; }}")
    
    def _change_background(self):
        """تغيير خلفية النافذة الرئيسية"""
        if self.parent_widget:
            change_background(self.parent_widget)
    
    # ============================================================================
    # Action Buttons
    # ============================================================================
    
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
    
    # ============================================================================
    # Machine Sizes Section
    # ============================================================================
    
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
        self.sizes_table = self._create_sizes_table()
        layout.addWidget(self.sizes_table)
        
        # أزرار الإدارة
        buttons_layout = self._create_machine_size_buttons()
        layout.addLayout(buttons_layout)
        
        sizes_group.setLayout(layout)
        
        # تحميل المقاسات الحالية
        self._load_machine_sizes()
        
        return sizes_group
    
    def _create_sizes_table(self):
        """Creates and configures the machine sizes table"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["الاسم", "الحد الأدنى", "الحد الأعلى", ""])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.setMaximumHeight(150)
        table.setStyleSheet(self._get_table_stylesheet())
        return table
    
    def _create_machine_size_buttons(self):
        """Creates the management buttons for machine sizes"""
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
        
        return buttons_layout
    
    def _load_machine_sizes(self):
        """تحميل المقاسات من config.json"""
        config = self._load_config()
        sizes = config.get("machine_sizes", self.DEFAULT_MACHINE_SIZES)
        
        # If no sizes in config, save defaults
        if not config.get("machine_sizes"):
            self._save_machine_sizes(self.DEFAULT_MACHINE_SIZES)
        
        self._populate_sizes_table(sizes)
    
    def _populate_sizes_table(self, sizes):
        """Populates the table with machine sizes"""
        self.sizes_table.setRowCount(len(sizes))
        for i, size in enumerate(sizes):
            self._populate_table_row(i, size)
    
    def _populate_table_row(self, row_index, size):
        """Populates a single row in the sizes table"""
        # العمود 0: الاسم
        self.sizes_table.setItem(row_index, 0, QTableWidgetItem(size["name"]))
        # العمود 1: الحد الأدنى
        self.sizes_table.setItem(row_index, 1, QTableWidgetItem(str(size["min_width"])))
        # العمود 2: الحد الأعلى
        self.sizes_table.setItem(row_index, 2, QTableWidgetItem(str(size["max_width"])))
        # العمود 3: زر الحذف
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet(self._get_delete_button_stylesheet())
        delete_btn.clicked.connect(lambda: self._delete_machine_size(row_index))
        self.sizes_table.setCellWidget(row_index, 3, delete_btn)
    
    def _save_machine_sizes(self, sizes):
        """حفظ المقاسات في config.json"""
        config = self._load_config()
        config["machine_sizes"] = sizes
        self._save_config(config)
    
    def _add_machine_size_dialog(self):
        """فتح نافذة لإضافة مقاس جديد"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ إضافة مقاس جديد")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(self._get_add_dialog_stylesheet())
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Create input fields
        name_input, min_input, max_input = self._create_size_input_fields(layout)
        
        # Create buttons
        save_btn, cancel_btn = self._create_size_dialog_buttons(layout)
        
        # Connect save button
        save_btn.clicked.connect(
            lambda: self._save_new_machine_size(dialog, name_input, min_input, max_input)
        )
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _create_size_input_fields(self, layout):
        """Creates input fields for the add size dialog"""
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
        
        return name_input, min_input, max_input
    
    def _create_size_dialog_buttons(self, layout):
        """Creates action buttons for the add size dialog"""
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
    
    def _save_new_machine_size(self, dialog, name_input, min_input, max_input):
        """Validates and saves a new machine size"""
        name = name_input.text().strip()
        
        try:
            min_w = int(min_input.text().strip())
            max_w = int(max_input.text().strip())
        except ValueError:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال أرقام صحيحة للعرض")
            return
        
        # Validate input
        if not self._validate_machine_size_input(name, min_w, max_w, dialog):
            return
        
        # Load current sizes and add new one
        config = self._load_config()
        sizes = config.get("machine_sizes", [])
        sizes.append({"name": name, "min_width": min_w, "max_width": max_w})
        
        self._save_machine_sizes(sizes)
        self._load_machine_sizes()
        dialog.accept()
    
    def _validate_machine_size_input(self, name, min_w, max_w, dialog):
        """Validates machine size input"""
        if not name:
            QMessageBox.warning(dialog, "خطأ", "يرجى إدخال اسم المقاس")
            return False
        
        if min_w >= max_w:
            QMessageBox.warning(dialog, "خطأ", "العرض الأدنى يجب أن يكون أقل من العرض الأعلى")
            return False
        
        return True
    
    def _delete_machine_size(self, index):
        """حذف مقاس من القائمة"""
        reply = QMessageBox.question(
            self, 
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المقاس؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            config = self._load_config()
            sizes = config.get("machine_sizes", [])
            
            if 0 <= index < len(sizes):
                sizes.pop(index)
                self._save_machine_sizes(sizes)
                self._load_machine_sizes()
