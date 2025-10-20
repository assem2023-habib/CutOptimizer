import json
import os
from PySide6.QtWidgets import (QWidget, QPushButton, QFrame, QLabel, QHBoxLayout, QVBoxLayout)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QFont

def create_window_controls(self):
    """إنشاء شريط أدوات مع أزرار التحكم في النافذة"""
    # شريط الأدوات العلوي
    self.toolbar = QWidget()
    self.toolbar.setFixedHeight(40)
    self.toolbar.setStyleSheet("""
        QWidget {
            background-color: #2C2C2C;
            border-bottom: 2px solid #007bff;
        }
    """)

    toolbar_layout = QHBoxLayout(self.toolbar)
    toolbar_layout.setContentsMargins(10, 5, 10, 5)
    toolbar_layout.setSpacing(10)

    # عنوان التطبيق في الشريط
    title_label = QLabel("🏠 تجميع السجاد - نظام محسن")
    title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
    title_label.setStyleSheet("color: #007bff; margin: 0;")
    toolbar_layout.addWidget(title_label)

    # زر تغيير السمة (الوضع الليلي/النهاري)
    self.theme_btn = QPushButton("🌙")
    self.theme_btn.setFixedSize(35, 30)
    self.theme_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    self.theme_btn.setStyleSheet("""
        QPushButton {
            background-color: #6f42c1;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5a359a;
        }
    """)
    self.theme_btn.clicked.connect(self.toggle_theme)
    toolbar_layout.addWidget(self.theme_btn)

    toolbar_layout.addStretch()

    # أزرار التحكم في النافذة
    # زر تصغير
    self.minimize_btn = QPushButton("─")
    self.minimize_btn.setFixedSize(30, 25)
    self.minimize_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    self.minimize_btn.setStyleSheet("""
        QPushButton {
            background-color: #ffc107;
            color: #000;
            border: none;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e0a800;
        }
    """)
    self.minimize_btn.clicked.connect(self.showMinimized)
    toolbar_layout.addWidget(self.minimize_btn)

    # زر تكبير/استعادة
    self.maximize_btn = QPushButton("□")
    self.maximize_btn.setFixedSize(30, 25)
    self.maximize_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    self.maximize_btn.setStyleSheet("""
        QPushButton {
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #218838;
        }
    """)
    self.maximize_btn.clicked.connect(lambda: toggle_maximize_restore(self))
    toolbar_layout.addWidget(self.maximize_btn)

    # زر إغلاق
    self.close_btn = QPushButton("×")
    self.close_btn.setFixedSize(30, 25)
    self.close_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    self.close_btn.setStyleSheet("""
        QPushButton {
            background-color: #dc3545;
            color: #fff;
            border: none;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c82333;
        }
    """)
    self.close_btn.clicked.connect(self.close)
    toolbar_layout.addWidget(self.close_btn)

def toggle_maximize_restore(self):
    """تبديل بين التكبير والاستعادة"""
    if self.isMaximized():
        self.showNormal()
        self.maximize_btn.setText("□")
    else:
        self.showMaximized()
        self.maximize_btn.setText("❐")

def toggle_theme(self):
    """تبديل بين السمة الداكنة والفاتحة"""
    self.is_dark_theme = not self.is_dark_theme

    if self.is_dark_theme:
        # تطبيق السمة الداكنة
        self.theme_btn.setText("🌙")
        apply_dark_theme(self)
    else:
        # تطبيق السمة الفاتحة
        self.theme_btn.setText("☀️")
        apply_light_theme(self)

    # حفظ الإعداد في ملف التكوين
    save_theme_preference(self)

def apply_dark_theme(self):
    """تطبيق السمة الداكنة"""
    dark_stylesheet = """
        QWidget {
            background-color: #1A1A1A;
            color: #E0E0E0;
            font-family: 'Segoe UI', 'Roboto', 'Inter', sans-serif;
            font-size: 10pt;
        }

        /* خلفية مع صورة للنافذة الرئيسية */
        QWidget#mainWindow {
            background-image: url(./assets/images/backgrounds/background_image_light.png);
            background-repeat: no-repeat;
            background-position: center center;
            background-attachment: fixed;
            background-color: #1A1A1A;
        }

        /* الأزرار الأساسية */
        QPushButton {
            background-color: #007bff;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 9pt;
            min-height: 35px;
        }

        QPushButton:hover {
            background-color: #0056b3;
            margin-top: -1px;
            border: 2px solid #ffffff;
        }

        QPushButton:pressed {
            background-color: #004085;
            margin-top: 0px;
            border: 2px solid #ffffff;
        }

        QPushButton:disabled {
            background-color: #6c757d;
            color: #adb5bd;
        }

        /* مربعات الإدخال */
        QLineEdit {
            background-color: #2C2C2C;
            color: #E0E0E0;
            border: 2px solid #404040;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 10pt;
            selection-background-color: #007bff;
        }

        QLineEdit:focus {
            border-color: #007bff;
        }

        QLineEdit::placeholder {
            color: #888;
        }

        /* منطقة السجل */
        QTextEdit {
            background-color: #2C2C2C;
            color: #E0E0E0;
            border: 2px solid #404040;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }

        /* شريط التقدم */
        QProgressBar {
            border: 2px solid #404040;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            background-color: #2C2C2C;
        }

        QProgressBar::chunk {
            background: linear-gradient(90deg, #007bff, #0056b3);
            border-radius: 4px;
        }

        /* الجداول */
        QTableWidget {
            background-color: #2C2C2C;
            color: #E0E0E0;
            border: 2px solid #404040;
            border-radius: 6px;
            gridline-color: #404040;
            selection-background-color: #007bff;
            selection-color: #FFFFFF;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #404040;
        }

        QTableWidget::item:selected {
            background-color: #007bff;
            color: #FFFFFF;
        }

        QHeaderView::section {
            background-color: #363636;
            color: #E0E0E0;
            padding: 12px;
            border: none;
            border-bottom: 2px solid #007bff;
            font-weight: 600;
            font-size: 10pt;
        }

        /* التسميات */
        QLabel {
            color: #E0E0E0;
            font-weight: 500;
        }

        /* الإطارات */
        QFrame {
            background-color: #2C2C2C;
            border: 2px solid #404040;
            border-radius: 8px;
        }

        /* شريط التمرير */
        QScrollBar:vertical {
            background-color: #2C2C2C;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background-color: #2C2C2C;
            border-radius: 6px;
        }

        /* رسائل الخطأ والنجاح */
        QMessageBox {
            background-color: #1A1A1A;
        }

        /* منطقة التمرير */
        QScrollArea {
            border: none;
            background-color: #1A1A1A;
        }

        QScrollArea QWidget {
            background-color: #1A1A1A;
        }
    """
    self.setStyleSheet(dark_stylesheet)

    # تحديث ألوان شريط الأدوات
    self.toolbar.setStyleSheet("""
        QWidget {
            background-color: #2C2C2C;
            border-bottom: 2px solid #007bff;
        }
    """)

def apply_light_theme(self):
    """تطبيق السمة الفاتحة"""
    light_stylesheet = """
        QWidget {
            background-color: #FFFFFF;
            color: #333333;
            font-family: 'Segoe UI', 'Roboto', 'Inter', sans-serif;
            font-size: 10pt;
        }

        /* خلفية مع صورة للنافذة الرئيسية */
        QWidget#mainWindow {
            background-image: url(./assets/images/backgrounds/background_image_light.png);
            background-repeat: no-repeat;
            background-position: center center;
            background-attachment: fixed;
            background-color: #FFFFFF;
        }

        /* الأزرار الأساسية */
        QPushButton {
            background-color: #007bff;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 9pt;
            min-height: 35px;
        }

        QPushButton:hover {
            background-color: #0056b3;
            margin-top: -1px;
            border: 2px solid #000000;
        }

        QPushButton:pressed {
            background-color: #004085;
            margin-top: 0px;
            border: 2px solid #000000;
        }

        QPushButton:disabled {
            background-color: #6c757d;
            color: #adb5bd;
        }

        /* مربعات الإدخال */
        QLineEdit {
            background-color: #FFFFFF;
            color: #333333;
            border: 2px solid #CCCCCC;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 10pt;
            selection-background-color: #007bff;
        }

        QLineEdit:focus {
            border-color: #007bff;
        }

        QLineEdit::placeholder {
            color: #888;
        }

        /* منطقة السجل */
        QTextEdit {
            background-color: #FFFFFF;
            color: #333333;
            border: 2px solid #CCCCCC;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }

        /* شريط التقدم */
        QProgressBar {
            border: 2px solid #CCCCCC;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            background-color: #FFFFFF;
        }

        QProgressBar::chunk {
            background: linear-gradient(90deg, #007bff, #0056b3);
            border-radius: 4px;
        }

        /* الجداول */
        QTableWidget {
            background-color: #FFFFFF;
            color: #333333;
            border: 2px solid #CCCCCC;
            border-radius: 6px;
            gridline-color: #CCCCCC;
            selection-background-color: #007bff;
            selection-color: #FFFFFF;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #CCCCCC;
        }

        QTableWidget::item:selected {
            background-color: #007bff;
            color: #FFFFFF;
        }

        QHeaderView::section {
            background-color: #F8F9FA;
            color: #333333;
            padding: 12px;
            border: none;
            border-bottom: 2px solid #007bff;
            font-weight: 600;
            font-size: 10pt;
        }

        /* التسميات */
        QLabel {
            color: #333333;
            font-weight: 500;
        }

        /* الإطارات */
        QFrame {
            background-color: #FFFFFF;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
        }

        /* شريط التمرير */
        QScrollBar:vertical {
            background-color: #F8F9FA;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #CCCCCC;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #AAAAAA;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background-color: #F8F9FA;
            border-radius: 6px;
        }

        /* رسائل الخطأ والنجاح */
        QMessageBox {
            background-color: #FFFFFF;
        }

        /* منطقة التمرير */
        QScrollArea {
            border: none;
            background-color: #FFFFFF;
        }

        QScrollArea QWidget {
            background-color: #FFFFFF;
        }
    """
    self.setStyleSheet(light_stylesheet)

    # تحديث ألوان شريط الأدوات
    self.toolbar.setStyleSheet("""
        QWidget {
            background-color: #F8F9FA;
            border-bottom: 2px solid #007bff;
        }
    """)

def save_theme_preference(self):
    """حفظ تفضيل السمة في ملف التكوين"""
    try:
        config = self.load_config()
        config['theme'] = 'dark' if self.is_dark_theme else 'light'
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ تفضيل السمة: {e}")

def setup_button_animations(self):
    """إعداد الرسوم المتحركة للأزرار للحصول على تأثير انتقال سلس"""
    # رسم متحرك لزر اختيار الملف
    self.input_animation = QPropertyAnimation(self.input_btn, b"geometry")
    self.input_animation.setDuration(300)

    # رسم متحرك لزر حفظ الإخراج
    self.output_animation = QPropertyAnimation(self.output_btn, b"geometry")
    self.output_animation.setDuration(300)

    # رسم متحرك لزر بدء المعالجة
    self.run_animation = QPropertyAnimation(self.run_btn, b"geometry")
    self.run_animation.setDuration(300)

    # رسم متحرك لزر فتح ملف Excel
    self.open_excel_animation = QPropertyAnimation(self.open_excel_btn, b"geometry")
    self.open_excel_animation.setDuration(300)

    # رسم متحرك لزر إلغاء العملية
    self.cancel_animation = QPropertyAnimation(self.cancel_btn, b"geometry")
    self.cancel_animation.setDuration(300)

    # ربط إشارات الماوس بالرسوم المتحركة
    self.input_btn.enterEvent = lambda event: animate_button_up(self, self.input_btn, self.input_animation)
    self.input_btn.leaveEvent = lambda event: animate_button_down(self, self.input_btn, self.input_animation)

    self.output_btn.enterEvent = lambda event: animate_button_up(self, self.output_btn, self.output_animation)
    self.output_btn.leaveEvent = lambda event: animate_button_down(self, self.output_btn, self.output_animation)

    self.run_btn.enterEvent = lambda event: animate_button_up(self, self.run_btn, self.run_animation)
    self.run_btn.leaveEvent = lambda event: animate_button_down(self, self.run_btn, self.run_animation)

    self.cancel_btn.enterEvent = lambda event: animate_button_up(self, self.cancel_btn, self.cancel_animation)
    self.cancel_btn.leaveEvent = lambda event: animate_button_down(self, self.cancel_btn, self.cancel_animation)

    self.open_excel_btn.enterEvent = lambda event: animate_button_up(self, self.open_excel_btn, self.open_excel_animation)
    self.open_excel_btn.leaveEvent = lambda event: animate_button_down(self, self.open_excel_btn, self.open_excel_animation)

def animate_button_up(self, button, animation):
    """تحريك الزر لأعلى عند دخول الماوس"""
    start_rect = button.geometry()
    end_rect = QRect(start_rect.x(), start_rect.y() - 2, start_rect.width(), start_rect.height())
    animation.setStartValue(start_rect)
    animation.setEndValue(end_rect)
    animation.start()

def animate_button_down(self, button, animation):
    """إعادة الزر لوضعه الطبيعي عند خروج الماوس"""
    start_rect = button.geometry()
    end_rect = QRect(start_rect.x(), start_rect.y() + 2, start_rect.width(), start_rect.height())
    animation.setStartValue(start_rect)
    animation.setEndValue(end_rect)
    animation.start()

def _create_primary_button(self, text, callback):
    """إنشاء زر أساسي بتصميم عصري"""
    btn = QPushButton(text)
    btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    btn.setMinimumHeight(35)
    btn.clicked.connect(callback)
    return btn

def _create_section_card(self, title):
    """إنشاء بطاقة قسم مع تصميم حديث"""
    frame = QFrame()
    frame.setFrameStyle(QFrame.Box)
    frame.setLineWidth(2)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    title_label = QLabel(title)
    title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
    title_label.setStyleSheet("color: #007bff; margin-bottom: 10px;")
    layout.addWidget(title_label)

    return frame, layout

def load_theme_preference(self):
    """تحميل تفضيل السمة من ملف التكوين"""
    try:
        config = self.load_config()
        theme = config.get('theme', 'dark')
        if theme == 'light':
            self.is_dark_theme = False
            apply_light_theme(self)
            if hasattr(self, 'theme_btn'):
                self.theme_btn.setText("☀️")
        else:
            self.is_dark_theme = True
            apply_dark_theme(self)
            if hasattr(self, 'theme_btn'):
                self.theme_btn.setText("🌙")
    except Exception as e:
        # في حالة وجود خطأ، استخدم السمة الداكنة كافتراضي
        self.is_dark_theme = True
        apply_dark_theme(self)
        if hasattr(self, 'theme_btn'):
            self.theme_btn.setText("🌙")

def set_background_image(self):
        """تعيين صورة الخلفية للنافذة الرئيسية"""
        try:
            # الحصول على المسار المطلق للصورة
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)  # المشروع الرئيسي
            image_path = os.path.join(project_dir, 'assets', 'images', 'backgrounds', 'background_image_light.png')

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # إنشاء فرشاة للصورة
                    brush = QBrush(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

                    # تعيين الفرشاة كخلفية للوحة الألوان
                    palette = self.palette()
                    palette.setBrush(QPalette.Window, brush)
                    self.setPalette(palette)

                    # تعيين الخلفية لتكون ثابتة أثناء التمرير
                    self.setAutoFillBackground(True)
                    print(f"✅ تم تعيين صورة الخلفية من: {image_path}")
                else:
                    print(f"❌ فشل في تحميل الصورة من: {image_path}")
            else:
                print(f"❌ مسار الصورة غير موجود: {image_path}")
        except Exception as e:
            print(f"❌ خطأ في تعيين صورة الخلفية: {e}")