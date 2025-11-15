import os
import json
import shutil
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

    config_dir = os.path.join("config", "backgrounds")
    os.makedirs(config_dir, exist_ok=True)

    file_name = os.path.basename(file_path)
    target_path = os.path.join(config_dir, file_name)

    shutil.copy(file_path, target_path)

    app_instance.config["background_image"] = target_path
    with open(app_instance.config_path, "w", encoding="utf-8") as f:
        json.dump(app_instance.config, f, ensure_ascii=False, indent=4)

    apply_background(app_instance, target_path)
    app_instance.log_append(f"🖼️ تم تعيين الصورة الجديدة كخلفية:\n{target_path}")



def apply_background(app_instance, image_path: str):
    """
    تطبيق الخلفية المحددة على واجهة التطبيق.
    """
    try:    
        if not os.path.exists(image_path):
            app_instance.log_append(f"❌  خطأ أثناء تطبيق الخلفية لم يتم ايجاد الخلفية")
            return
        
        qss_path = image_path.replace("\\", "/")

        pixmap = QPixmap(qss_path)
        if pixmap.isNull():
            app_instance.log_append(f"❌ خطأ أثناء تطبيق الخلفية مشكلة في pixmap")
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

