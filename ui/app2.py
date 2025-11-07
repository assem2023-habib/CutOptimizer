import json
import traceback
import sys, os
import copy
import subprocess
import platform
from PySide6.QtWidgets import (QWidget,QApplication,QLineEdit, QPushButton, QVBoxLayout
                               , QFileDialog, QLabel, QLineEdit,
                                 QTextEdit, QHBoxLayout, QMessageBox, 
                                 QTableWidget, QTableWidgetItem, 
                                 QProgressBar, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QIntValidator
from data_io.excel_io import read_input_excel, write_output_excel
from core.grouping_algorithm import build_groups
from core.validation import validate_config, validate_carpets
from .ui_utils import ( setup_button_animations,
                       _create_section_card)
from ui.components.top_button_section import TopButtonSection
from core.actions.file_actions import (
    browse_input_lineedit,
    browse_output_lineedit,
    open_excel_file
)
from ui.components.measurement_settings_section import MeasurementSettingsSection
from ui.components.process_controll_section import ProcessControllSection
from core.workers.grouping_worker import GroupingWorker
from ui.components.progress_status_item import ProgressStatusItem
from ui.components.results_and_summary_section import ResultsAndSummarySection


class RectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()

        self.worker_thread = None
        self.worker = None
        self.is_running = None
        self.config_path = config_path
        self.config = self.load_config()
        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit()

        self._setup_ui()

    def _setup_ui(self):
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

        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        title_label = QLabel("🏠 تجميع السجاد")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007bff; margin: 0;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)

        self.top_button_section = TopButtonSection(
            on_import_clicked= self.browse_input,
            on_export_clicked= self.browse_output
        )

        self.measurement_section = MeasurementSettingsSection()

        self.process_control_section = ProcessControllSection(
            on_start_clicked=self.run_grouping,
            on_stop_clicked=self.cancel_operation
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
                min_width=int(self.measurement_section.min_input.input.text()),
                max_width=int(self.measurement_section.max_input.input.text()),
                tolerance_len=int(self.measurement_section.margin_input.input.text()),
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
                table_data.append({
                    "group_id": f"GRP-{i:03}",
                    "carpet_id": getattr(g, "carpet_id", f"CPT-{100+i}"),
                    "qty_used": getattr(g, "qty_used", 0),
                    "qty_rem": getattr(g, "qty_rem", 0),
                    "ref_height": getattr(g, "ref_height", 0.0),
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
        else:
            self.status_item.set_text("❌ حدث خطأ أثناء العملية")
            self.status_item.set_status("failed")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RectPackApp()
    window.show()
    sys.exit(app.exec())
    