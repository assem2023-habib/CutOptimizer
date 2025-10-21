import json
import os
from PySide6.QtWidgets import QWidget


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
    if hasattr(self, 'toolbar'):
        self.toolbar.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-bottom: 2px solid #007bff;
                border-radius: 8px;
                margin: 5px;
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
            color: black;
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
            color: #FFFFFF;
        }

        QPushButton:pressed {
            background-color: #004085;
            margin-top: 0px;
            border: 2px solid #000000;
            color: #FFFFFF;
        }

        QPushButton:disabled {
            background-color: #6c757d;
            color: #FFFFFF;
            opacity: 0.7;
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
            background-color: #FFFFFF;
        }

        QLineEdit::placeholder {
            color: #666666;
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

        /* العناوين الرئيسية */
        QLabel[cssClass="title"] {
            color: #007bff;
            font-weight: 600;
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
    if hasattr(self, 'toolbar'):
        self.toolbar.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-bottom: 2px solid #007bff;
                border-radius: 8px;
                margin: 5px;
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
