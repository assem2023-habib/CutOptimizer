import os
import shutil
from PySide6.QtGui import QPixmap, QPalette, QBrush, QLinearGradient, QColor
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtWidgets import QFileDialog, QMessageBox

from core.config.config_manager import ConfigManager

DEFAULT_BG_COLOR = "#FFFFFFFF"
DEFAULT_BG_PATH = "config/backgrounds/img1.jpg"

def get_user_backgrounds_dir():
    """Returns the directory for storing user background images in AppData"""
    base_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    bg_path = os.path.join(base_path, "backgrounds")
    os.makedirs(bg_path, exist_ok=True)
    return bg_path

def change_background(app_instance):
    """
    تغيير خلفية التطبيق وحفظ المسار في ملف الإعدادات.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        app_instance,
        "اختر صورة الخلفية",
        "",
        "صور (*.png *.jpg *.jpeg)"
    )
    
    if not file_path:
        return

    try:
        # تحديد المجلد في AppData
        config_dir_abs = get_user_backgrounds_dir()
        
        # مسح محتوى المجلد قبل نسخ الصورة الجديدة
        clear_backgrounds_folder(config_dir_abs, app_instance)

        file_name = os.path.basename(file_path)
        target_path_abs = os.path.join(config_dir_abs, file_name)
        
        # نسخ الملف الجديد
        shutil.copy(file_path, target_path_abs)

        # حفظ المسار المطلق في QSettings
        ConfigManager.set_value("background_image", target_path_abs)
        # إزالة التدرج إذا كان موجوداً
        ConfigManager.remove_value("background_gradient")

        apply_background(app_instance, target_path_abs)
        app_instance.log_append(f"🖼️ تم تعيين الصورة الجديدة كخلفية:\n{file_name}")
        
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء تغيير الخلفية: {e}")
        QMessageBox.critical(app_instance, "خطأ", f"فشل تغيير الخلفية:\n{e}")


def clear_backgrounds_folder(folder_path: str, app_instance):
    """
    مسح جميع الملفات داخل مجلد الخلفيات.
    """
    try:
        if not os.path.exists(folder_path):
            return
        
        # حذف جميع الملفات داخل المجلد
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    # app_instance.log_append(f"🗑️ تم حذف الملف القديم: {filename}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                app_instance.log_append(f"⚠️ تعذر حذف {filename}: {e}")
                
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء مسح مجلد الخلفيات: {e}")

def apply_background(app_instance, image_path: str):
    """
    تطبيق الخلفية المحددة على واجهة التطبيق.
    """
    try:
        if not image_path:
            # app_instance.log_append(f"❌ خطأ: مسار الخلفية فارغ")
            reset_to_default_background(app_instance)
            return
        
        # إذا كان المسار نسبياً (للخلفيات الافتراضية)، نستخدم resource_path
        # إذا كان مطلقاً (للخلفيات المخصصة)، نستخدمه كما هو
        if not os.path.isabs(image_path):
             absolute_image_path = resource_path(image_path)
        else:
             absolute_image_path = image_path
        
        if not os.path.exists(absolute_image_path):
            app_instance.log_append(f"❌ خطأ: الخلفية غير موجودة - {absolute_image_path}")
            reset_to_default_background(app_instance)
            return
        
        # تحميل الصورة
        pixmap = QPixmap(absolute_image_path)
        
        if pixmap.isNull():
            app_instance.log_append(f"❌ خطأ: فشل تحميل الصورة - {absolute_image_path}")
            reset_to_default_background(app_instance)
            return
        
        scaled_pixmap = pixmap.scaled(
            app_instance.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        palette = app_instance.palette()
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        app_instance.setPalette(palette)
        app_instance.setAutoFillBackground(True)
        # app_instance.log_append(f"✅ تم تطبيق الخلفية بنجاح")
        
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء تطبيق الخلفية: {e}")
        reset_to_default_background(app_instance)


def remove_background(app_instance):
    """إزالة الخلفية والعودة للتدرج اللوني الافتراضي."""
    try:
        ConfigManager.remove_value("background_image")
        
        # مسح مجلد الخلفيات
        config_dir_abs = get_user_backgrounds_dir()
        clear_backgrounds_folder(config_dir_abs, app_instance)
        
        reset_to_default_background(app_instance)
        app_instance.log_append(f"✅ تم إزالة الخلفية بنجاح")
            
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء إزالة الخلفية: {e}")



def reset_to_default_background(app_instance):
    """تطبيق الخلفية الافتراضية (تدرج لوني جميل من الأبيض إلى السماوي)."""
    try:
        bg_path = resource_path(DEFAULT_BG_PATH)
        # app_instance.log_append(f"🔍 تحميل الخلفية الافتراضية من: {bg_path}")

        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    app_instance.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                palette = app_instance.palette()
                palette.setBrush(QPalette.Window, QBrush(scaled))
                app_instance.setPalette(palette)
                app_instance.setAutoFillBackground(True)
                # app_instance.log_append("✅ تم تعيين الخلفية الافتراضية بنجاح")
                return
        
        # fallback — تطبيق تدرج لوني جميل من الأبيض إلى السماوي
        apply_default_gradient(app_instance)
        # app_instance.log_append("✨ تم تطبيق التدرج اللوني الافتراضي.")

    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء تعيين الخلفية الافتراضية: {e}")
        # في حال حدوث خطأ، نستخدم التدرج اللوني
        apply_default_gradient(app_instance)


def apply_default_gradient(app_instance):
    """تطبيق تدرج لوني جميل من الأبيض إلى السماوي كخلفية افتراضية."""
    try:
        # إنشاء تدرج لوني من الأعلى إلى الأسفل
        gradient = QLinearGradient(0, 0, 0, app_instance.height())
        
        # نقطة البداية: أبيض ثلجي نقي
        gradient.setColorAt(0.0, QColor(255, 255, 255))  # White
        
        # نقطة وسطى: أبيض مع لمسة سماوي خفيفة جداً
        gradient.setColorAt(0.3, QColor(240, 248, 255))  # Alice Blue
        
        # نقطة وسطى ثانية: سماوي فاتح جداً
        gradient.setColorAt(0.6, QColor(224, 242, 254))  # Light Sky Blue
        
        # نقطة النهاية: سماوي فاتح جميل
        gradient.setColorAt(1.0, QColor(186, 230, 253))  # Beautiful Sky Blue
        
        # تطبيق التدرج
        palette = app_instance.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        app_instance.setPalette(palette)
        app_instance.setAutoFillBackground(True)
        
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء تطبيق التدرج اللوني: {e}")
        # في حال الفشل، استخدم لون أبيض عادي
        palette = app_instance.palette()
        palette.setBrush(QPalette.Window, QBrush(Qt.white))
        app_instance.setPalette(palette)


def validate_image(file_path: str) -> bool:
    """التحقق من صحة ملف الصورة."""
    if not os.path.exists(file_path):
        return False
    
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    _, ext = os.path.splitext(file_path.lower())
    
    if ext not in valid_extensions:
        return False
    
    # محاولة تحميل الصورة للتأكد من صحتها
    pixmap = QPixmap(file_path)
    return not pixmap.isNull()


def resource_path(relative_path):
    """
    يدعم التشغيل من PyInstaller onefile.
    يحول المسار النسبي إلى مسار مطلق يعمل في بيئة التطوير وفي الـ EXE.
    """
    # إذا كان المسار مطلقاً بالفعل، قم بإرجاعه كما هو
    if os.path.isabs(relative_path):
        return relative_path
    
    # إذا كان التطبيق يعمل كـ EXE بواسطة PyInstaller
    if hasattr(sys, "_MEIPASS"):
        # للملفات المدمجة في الـ EXE
        bundled_path = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(bundled_path):
            return bundled_path
        
        # للملفات التي يتم إنشاؤها أثناء التشغيل (مثل backgrounds)
        # نستخدم المسار بجانب الـ EXE
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, relative_path)
    
    # في بيئة التطوير، نستخدم المسار بالنسبة لمجلد السكريبت
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

def save_background_path(path: str):
    """
    حفظ مسار الخلفية في ملف الإعدادات.
    إذا كان المسار فارغاً، يتم إزالة إعداد الخلفية.
    """
    try:
        if path:
            ConfigManager.set_value("background_image", path)
            ConfigManager.remove_value("background_gradient")
        else:
            ConfigManager.remove_value("background_image")
            
    except Exception as e:
        print(f"❌ Error saving background path: {e}")

def save_background_gradient(gradient_index: int):
    """
    حفظ التدرج اللوني المختار في ملف الإعدادات.
    يزيل أي صورة خلفية محفوظة.
    """
    try:
        ConfigManager.set_value("background_gradient", gradient_index)
        ConfigManager.remove_value("background_image")
            
    except Exception as e:
        print(f"❌ Error saving background gradient: {e}")