import json
import os
from PySide6.QtWidgets import (QWidget, QPushButton, QFrame, QLabel, QHBoxLayout, QVBoxLayout)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QFont
from .theme_manager import toggle_theme, apply_dark_theme, apply_light_theme, save_theme_preference, load_theme_preference

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