import os, json, shutil

from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt

DEFAULT_BG_COLOR = "#FFFFFFFF"

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
        config_dir = os.path.join("config", "backgrounds")
        os.makedirs(config_dir, exist_ok=True)

        # مسح محتوى المجلد قبل نسخ الصورة الجديدة
        clear_backgrounds_folder(config_dir, app_instance)

        file_name = os.path.basename(file_path)
        target_path = os.path.join(config_dir, file_name)
        
        # نسخ الملف الجديد
        shutil.copy(file_path, target_path)

        # حفظ المسار في ملف الإعدادات
        app_instance.config["background_image"] = target_path
        with open(app_instance.config_path, "w", encoding="utf-8") as f:
            json.dump(app_instance.config, f, ensure_ascii=False, indent=4)

        apply_background(app_instance, target_path)
        app_instance.log_append(f"🖼️ تم تعيين الصورة الجديدة كخلفية:\n{target_path}")
        
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
                    app_instance.log_append(f"🗑️ تم حذف الملف القديم: {filename}")
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
        if not image_path or not os.path.exists(image_path):
            app_instance.log_append(f"❌ خطأ: الخلفية غير موجودة - {image_path}")
            reset_to_default_background(app_instance)
            return
        
        qss_path = image_path.replace("\\", "/")
        pixmap = QPixmap(qss_path)
        
        if pixmap.isNull():
            app_instance.log_append(f"❌ خطأ: فشل تحميل الصورة - {image_path}")
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
        
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء تطبيق الخلفية: {e}")
        reset_to_default_background(app_instance)


def remove_background(app_instance):
    """إزالة الخلفية والعودة للون الافتراضي."""
    try:
        if "background_image" in app_instance.config:
            old_bg = app_instance.config["background_image"]
            del app_instance.config["background_image"]
            
            with open(app_instance.config_path, "w", encoding="utf-8") as f:
                json.dump(app_instance.config, f, ensure_ascii=False, indent=4)
            
            # مسح مجلد الخلفيات
            config_dir = os.path.join("config", "backgrounds")
            clear_backgrounds_folder(config_dir, app_instance)
            
            reset_to_default_background(app_instance)
            app_instance.log_append(f"✅ تم إزالة الخلفية بنجاح")
            
    except Exception as e:
        app_instance.log_append(f"❌ خطأ أثناء إزالة الخلفية: {e}")


def reset_to_default_background(app_instance):
    """إعادة تعيين الخلفية إلى اللون الافتراضي."""
    try:
        palette = app_instance.palette()
        palette.setBrush(QPalette.Window, QBrush(Qt.white))
        app_instance.setPalette(palette)
        app_instance.setAutoFillBackground(True)
    except Exception as e:
        app_instance.log_append(f"❌ خطأ في إعادة تعيين الخلفية الافتراضية: {e}")


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