import json
import traceback
import sys, os
import shutil
from PySide6.QtWidgets import (QWidget,QApplication, QVBoxLayout
                               , QFileDialog, QLabel,
                                 QTextEdit, QHBoxLayout, QMessageBox, 
                                 QScrollArea)
from PySide6.QtCore import Qt, QSize

from PySide6.QtGui import QFont, QPixmap, QPalette, QBrush

from ui.sections.top_button_section import TopButtonSection
from core.actions.file_actions import (
    browse_input_lineedit,
    browse_output_lineedit,
    open_excel_file
)
from ui.components.app_button import AppButton
from ui.sections.measurement_settings_section import MeasurementSettingsSection
from ui.sections.process_controll_section import ProcessControllSection
from core.workers.grouping_worker import GroupingWorker
from ui.components.progress_status_item import ProgressStatusItem
from ui.sections.results_and_summary_section import ResultsAndSummarySection
from core.utilies.timer_utils import init_timer, start_timer, stop_timer

class RectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()

        self.worker_thread = None
        self.worker = None
        self.is_running = False
        self.config_path = config_path
        self.config = self.load_config()
        init_timer(self)

        self._setup_ui()

    def resizeEvent(self, event):
        if "background_image" in self.config:
            self.apply_background(self.config["background_image"])
        super().resizeEvent(event)

    def _setup_ui(self):
        self.resize(900, 800)
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.frameGeometry()
        self.move(
            (screen.width() - window_size.width()) // 2,
            (screen.height() - window_size.height()) // 2
        )
        self.setObjectName("mainWindow")
        self.setWindowTitle("تجميع السجاد - نظام محسن")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 120); /* أسود شفاف */
                border-radius: 10px;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        title_label = QLabel("🏠")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.change_bg_btn = AppButton(
            text="🖼️",
            color="#6f42c1",
            hover_color="#8c68d4",
            text_color="#FFFFFF",
            fixed_size=QSize(50, 22)
        )
        self.change_bg_btn.clicked.connect(self.change_background)
        header_layout.addWidget(self.change_bg_btn)
        content_layout.addLayout(header_layout)

        self.top_button_section = TopButtonSection(
            on_import_clicked= self.browse_input,
            on_export_clicked= self.browse_output
        )

        self.measurement_section = MeasurementSettingsSection()

        self.process_control_section = ProcessControllSection(
            on_start_clicked=self.run_grouping,
            on_stop_clicked=self.cancel_operation,
            on_open_excel_clicked=self.open_excel_file 
        )
        self.status_item = ProgressStatusItem("جاهز لبدء العملية", "pending")
        self.results_section = ResultsAndSummarySection()

        content_layout.addWidget(self.top_button_section)
        content_layout.addWidget(self.measurement_section)
        content_layout.addWidget(self.process_control_section)
        content_layout.addWidget(self.status_item)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(150)
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)
        content_layout.addWidget(self.log)
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        content_layout.addWidget(self.results_section)
        content_layout

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                return {}
            return cfg
        except Exception as e:
            QMessageBox.warning(self, "Config", f"خطأ بتحميل الإعدادات : {e}")
            return {}

    def browse_input(self):
        browse_input_lineedit(
            self.top_button_section.input_edit,
            self.top_button_section.output_edit
        )

    def browse_output(self):
        browse_output_lineedit(self.top_button_section.output_edit)

    def open_excel_file(self):
        output_path = self.top_button_section.output_edit.text().strip()
        open_excel_file(output_path, getattr(self, "log_append", None))

    def run_grouping(self):
        start_timer(self)
        if self.is_running:
            QMessageBox.information(self, "معلومة", "العملية قيد التشغيل بالفعل.")
            return
        input_path = self.top_button_section.input_edit.text().strip()
        output_path = self.top_button_section.output_edit.text().strip()

        if not input_path or not output_path:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد ملف الإدخال والإخراج أولاً.")
            return
        self.results_section.groups_table.data= []
        self.results_section.groups_table._populate_table()
        self.results_section.update_summary(
            total_files=0,
            success_rate=0,
            failed_files=0,
            duration="—"
        )
        try:
            min_w = int(self.measurement_section.min_input.input.text())
            max_w = int(self.measurement_section.max_input.input.text())
            tol = int(self.measurement_section.margin_input.input.text())
        except ValueError:
            QMessageBox.warning(self, "قيم خاطئة", "يرجى إدخال أرقام صحيحة في حقول القياسات.")
            return
        try:
            self.timer.timeout.connect(self.update_duration_card)
            self.is_running = True
            self.process_control_section.enable_stop_only()
            self.measurement_section.set_inputs_enabled(False)
            self.top_button_section.setEnabled(False)

            self.log_append("✅ تم بدء عملية التجميع...")
            self.status_item.set_text("🔄 جاري تنفيذ العملية...")
            self.status_item.set_status("in_progress")

            self.worker = GroupingWorker(
                input_path=input_path,
                output_path=output_path,
                min_width=min_w,
                max_width=max_w,
                tolerance_len=tol,
                cfg=self.config
            )

            self.worker.signals.log.connect(self.log_append)
            self.worker.signals.progress.connect(lambda p: self.log_append(f"🔄 Progress: {p}%"))
            self.worker.signals.error.connect(lambda e: self.log_append(f"❌ خطأ:\n{e}"))
            self.worker.signals.data_ready.connect(self.on_worker_data_ready)
            self.worker.signals.finished.connect(self.on_worker_finished)
            self.worker.start()
        except Exception as e:
            self.log_append(f"❌ خطأ أثناء بدء العملية: {e}")
            traceback.print_exc()
            self.reset_ui_state()

    def cancel_operation(self):
        if not self.is_running:
            QMessageBox.information(self, "معلومة", "لا توجد عملية قيد التشغيل.")
            return 

        try:
            if self.worker:
                self.worker.stop()
                self.log_append("🛑 تم إرسال أمر الإلغاء...")

            else:
                self.log_append("⚠️ لا يوجد عامل نشط لإيقافه.")

        except Exception as e:
            self.log_append(f"❌ خطأ أثناء الإلغاء: {e}")
            traceback.print_exc()

        finally:
            self.reset_ui_state()
    
    def on_worker_data_ready(self, groups, remaining, stats):
        try:
            table_data = []
            for i, g in enumerate(groups, start=1):
                for item in getattr(g, "items", []):
                    table_data.append({
                       "group_id": f"GRP-{getattr(g, 'group_id', '—'):03}",
                        "qty_used": getattr(item, "qty_used", 0),
                        "qty_rem": getattr(item, "qty_rem", 0),
                        "ref_height": item.length_ref() if hasattr(item, "length_ref") else 0,
                        "carpet": item.summary() if hasattr(item, "summary") else "-",
                    })

            self.results_section.groups_table.data = table_data
            self.results_section.groups_table.total_pages = max(
                1, (len(table_data) + self.results_section.groups_table.rows_per_page - 1)
                // self.results_section.groups_table.rows_per_page
            )
            self.results_section.groups_table.current_page = 1
            self.results_section.groups_table._populate_table()

            total_original = stats.get("total_original", 0)
            total_used = stats.get("total_used", 0)
            total_remaining = stats.get("total_remaining", 0)
            utilization = stats.get("utilization_percentage", 0)
            self.results_section.update_summary(
                total_files= total_original,
                success_rate=utilization,
                failed_files=total_remaining,
                duration="_"
            )
            self.log_append("📊 تم تحديث قسم النتائج والملخص.")
        except Exception as e:
            self.log_append(f"⚠️ خطأ أثناء تحديث النتائج: {e}")
                

    def on_worker_finished(self, success= True, message= "تمت العملية بنجاح."):
        if success:
            self.status_item.set_text("✅ تمت العملية بنجاح")
            self.status_item.set_status("success")
            self.process_control_section.show_open_excel_button(True)
        else:
            self.status_item.set_text("❌ حدث خطأ أثناء العملية")
            self.status_item.set_status("failed")
            self.process_control_section.show_open_excel_button(False)
        
        stop_timer(self)
        self.reset_ui_state()

    def log_append(self, text):
        self.log.append(text)

    def reset_ui_state(self):
        self.is_running = False
        self.process_control_section.enable_start_only()
        self.measurement_section.set_inputs_enabled(True)
        self.top_button_section.setEnabled(True)

        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
            self.worker = None

        self.log_append("↩️ الواجهة عادت للحالة الافتراضية.")         

    def change_background(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "اختر صورة الخلفية",
                "",
                "صور (*.png *.jpg *.jpeg)"
            )

            if not file_path:
                return

            config_dir = os.path.join(os.getcwd(), "config", "backgrounds")
            os.makedirs(config_dir, exist_ok=True)

            file_name = os.path.basename(file_path)
            target_path = os.path.join(config_dir, file_name)

            shutil.copy(file_path, target_path)

            self.config["background_image"] = target_path
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            self.apply_background(target_path)
            self.log_append(f"🖼️ تم تعيين الصورة الجديدة كخلفية:\n{target_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تغيير الخلفية:\n{e}")
            self.log_append(f"❌ خطأ أثناء تغيير الخلفية: {e}")   

    def apply_background(self, image_path: str):
        try:
            if not os.path.exists(image_path):
                return

            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                return

            # ضبط حجم الصورة لتتناسب مع النافذة
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)

        except Exception as e:
            self.log_append(f"❌ خطأ أثناء تغيير الخلفية: {e}")   


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RectPackApp()
    window.show()
    sys.exit(app.exec())
    

    