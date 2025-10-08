# advanced_rectpack_app.py
"""
واجهة متقدّمة لتشغيل خوارزميات تجميع السجاد (RectPack)
بنى على واجهة الأصلية مع دعم خوارزمية تجميع بواقي محسّنة
توفر إمكانية تكرار نفس النوع داخل نفس المجموعة.
"""

import json
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt

# imports أساسية من مشروعك (مرن: يحاول استدعاء الدالة المحسّنة أولًا ثم fallback)
from data_io.excel_io import read_input_excel, write_output_excel
from data_io.pdf_report import SimplePDFReport
from core.grouping import group_carpets_greedy
from core.validation import validate_config, validate_carpets

# محاولة استدعاء الدالة المحسّنة؛ إن لم تكن موجودة سنستخدم exhaustively_regroup إن وُجد
try:
    # الدالة المحسّنة كما وضعناها في الوحدة الرئيسية (create_enhanced_remainder_groups)
    from data_io.excel_io import create_enhanced_remainder_groups as enhanced_remainder_fn  # تكيّف حسب بنية مشروعك
except Exception:
    enhanced_remainder_fn = None

try:
    # دالة fallback قديمة / موجودة في excel_io
    from data_io.excel_io import exhaustively_regroup as fallback_exhaustive_fn
except Exception:
    fallback_exhaustive_fn = None


class AdvancedRectPackApp(QWidget):
    def __init__(self, config_path='config/config.json'):
        super().__init__()
        self.setWindowTitle("RectPack Advanced - تجميع السجاد المتقدّم")
        self.resize(980, 680)
        self.config_path = config_path
        self.config = self.load_config()

        layout = QVBoxLayout()

        # input file selector
        h1 = QHBoxLayout()
        self.input_edit = QLineEdit()
        btn_browse = QPushButton("اختيار ملف الإدخال (.xlsx)")
        btn_browse.clicked.connect(self.browse_input)
        h1.addWidget(QLabel("ملف الإدخال:"))
        h1.addWidget(self.input_edit)
        h1.addWidget(btn_browse)
        layout.addLayout(h1)

        # output file selector
        h2 = QHBoxLayout()
        self.output_edit = QLineEdit()
        btn_out = QPushButton("اختر مكان حفظ الإخراج")
        btn_out.clicked.connect(self.browes_output)
        h2.addWidget(QLabel("ملف الإخراج:"))
        h2.addWidget(self.output_edit)
        h2.addWidget(btn_out)
        layout.addLayout(h2)

        # width inputs
        h2_5 = QHBoxLayout()
        self.min_width_edit = QLineEdit()
        self.min_width_edit.setText(str(self.config.get('min_width', 370)))
        self.min_width_edit.setPlaceholderText("العرض الأدنى")
        h2_5.addWidget(QLabel("العرض الأدنى:"))
        h2_5.addWidget(self.min_width_edit)

        self.max_width_edit = QLineEdit()
        self.max_width_edit.setText(str(self.config.get('max_width', 400)))
        self.max_width_edit.setPlaceholderText("العرض الأقصى")
        h2_5.addWidget(QLabel("العرض الأقصى:"))
        h2_5.addWidget(self.max_width_edit)

        # tolerance_length input
        self.tolerance_edit = QLineEdit()
        self.tolerance_edit.setText(str(self.config.get('tolerance_length', 100)))
        self.tolerance_edit.setPlaceholderText("هامش التسامح بالطول")
        h2_5.addWidget(QLabel("هامش التسامح بالطول:"))
        h2_5.addWidget(self.tolerance_edit)
        layout.addLayout(h2_5)

        # advanced options: use enhanced regroup
        h_adv = QHBoxLayout()
        self.advanced_checkbox = QCheckBox("استخدام التجميع المحسّن (تكرار العناصر داخل نفس المجموعة إذا لزم)")
        # تفعيل افتراضي لو كانت الدالة المحسنة موجودة
        self.advanced_checkbox.setChecked(enhanced_remainder_fn is not None)
        h_adv.addWidget(self.advanced_checkbox)
        layout.addLayout(h_adv)

        # run & config info
        h3 = QHBoxLayout()
        self.run_btn = QPushButton("تشغيل التجميع")
        self.run_btn.clicked.connect(self.run_grouping)
        h3.addWidget(self.run_btn)

        # config display
        cfg_label = QLabel(f"Config: {os.path.abspath(self.config_path)}")
        h3.addWidget(cfg_label)
        layout.addLayout(h3)

        # results table label + table
        layout.addWidget(QLabel("سجل النشاطات:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, stretch=1)

        # results summary table (simple)
        layout.addWidget(QLabel("ملخص المجموعات (الأصلية):"))
        self.summary_table = QTableWidget(0, 4)
        self.summary_table.setHorizontalHeaderLabels(["عدد الأنواع", "الطول المرجعي", "العرض الإجمالي", "رقم المجموعة"])
        layout.addWidget(self.summary_table, stretch=1)

        self.setLayout(layout)

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            return cfg
        except Exception as e:
            QMessageBox.warning(self, "Config", f"خطأ بتحميل الإعدادات : {e}")
            return {}

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف الاكسل", "",
                                             "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            self.input_edit.setText(path)

    def browes_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف الإخراج", "",
                                             "Excel Files (*.xlsx *.xls);;Excel 2007+ (*.xlsx);;Excel 97-2003 (*.xls);;All Files (*)")
        if path:
            if not path.lower().endswith(('.xlsx', '.xls')):
                path += '.xlsx'
            self.output_edit.setText(path)

    def log_append(self, text: str):
        self.log.append(text)

    def run_grouping(self):
        input_path = self.input_edit.text().strip()
        output_path = self.output_edit.text().strip()
        if not input_path or not output_path:
            QMessageBox.warning(self, "اختر مسار الإدخال ومسار الإخراج", "يرجى اختيار ملف الإدخال ومسار ملف الإخراج أولاً.")
            return

        # Get width values from input
        try:
            min_width = int(self.min_width_edit.text().strip())
            max_width = int(self.max_width_edit.text().strip())
            tolerance_len = int(self.tolerance_edit.text().strip())
            if min_width <= 0 or max_width <= 0:
                QMessageBox.warning(self, "خطأ في القيم", "العرض الأدنى والأقصى يجب أن يكونا أكبر من 0")
                return
            if min_width >= max_width:
                QMessageBox.warning(self, "خطأ في القيم", "العرض الأدنى يجب أن يكون أقل من العرض الأقصى")
                return
            if tolerance_len < 0:
                QMessageBox.warning(self, "خطأ في القيم", "هامش التسامح يجب أن يكون صفراً أو رقماً موجباً")
                return
        except ValueError:
            QMessageBox.warning(self, "خطأ في القيم", "يرجى إدخال أرقام صحيحة للعرض الأدنى والأقصى وهامش التسامح")
            return

        # validate config
        ok, err = validate_config(min_width, max_width, tolerance_len)
        if not ok:
            QMessageBox.warning(self, "Config error", err)
            return

        self.log_append(f"قراءة الملف: {input_path}")
        try:
            carpets = read_input_excel(input_path)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل بقراءة ملف الاكسل: {e}")
            return

        # احتفظ بنسخة من الأصليات قبل أي تعديل
        originals_copy = [type(c)(c.id, c.width, c.length, c.qty) if hasattr(c, 'id') else c for c in carpets]

        errs = validate_carpets(carpets)
        if errs:
            self.log_append("تحذيرات في البيانات:")
            for e in errs:
                self.log_append(" - " + e)

        # التجميع الأساسي (greedy)
        groups, remaining = group_carpets_greedy(
            carpets,
            min_width=min_width,
            max_width=max_width,
            tolerance_length=tolerance_len,
            start_with_largest=self.config.get('start_with_largest', True),
            allow_split_rows=self.config.get('allow_split_rows', True)
        )

        self.log_append(f"تم تشكيل {len(groups)} مجموعة . المتبقي: {len(remaining)} أنواع (مع كميات).")

        # اختيار طريقة إعادة تجميع البواقي
        use_enhanced = self.advanced_checkbox.isChecked() and enhanced_remainder_fn is not None

        if use_enhanced:
            self.log_append("استخدام: التجميع المحسّن (create_enhanced_remainder_groups).")
            try:
                rem_groups, rem_final_remaining = enhanced_remainder_fn(
                    remaining,
                    min_width,
                    max_width,
                    tolerance_len,
                    start_group_id=max([g.id for g in groups] + [0]) + 1,
                    max_rounds=100
                )
            except Exception as e:
                self.log_append(f"خطأ في التجميع المحسّن: {e}")
                # fallback إلى الدالة التقليدية إن وُجدت
                if fallback_exhaustive_fn:
                    self.log_append("العودة إلى التجميع التقليدي (fallback).")
                    rem_groups, rem_final_remaining = fallback_exhaustive_fn(
                        remaining, min_width, max_width, tolerance_len,
                        start_group_id=max([g.id for g in groups] + [0]) + 1,
                        max_rounds=100
                    )
                else:
                    rem_groups, rem_final_remaining = [], remaining
        else:
            # استخدام fallback إن كانت متاحة
            if fallback_exhaustive_fn:
                self.log_append("استخدام: التجميع التقليدي (exhaustively_regroup).")
                rem_groups, rem_final_remaining = fallback_exhaustive_fn(
                    remaining, min_width, max_width, tolerance_len,
                    start_group_id=max([g.id for g in groups] + [0]) + 1,
                    max_rounds=100
                )
            else:
                self.log_append("لا توجد دالة إعادة تجميع متاحة؛ سيتم تخطي مرحلة التجميع المتقدم.")
                rem_groups, rem_final_remaining = [], remaining

        self.log_append(f"تم تشكيل {len(rem_groups)} مجموعة إضافية من البواقي. تبقّى بعد ذلك: {len(rem_final_remaining)} أنواع.")

        # write excel
        try:
            write_output_excel(
                output_path,
                groups,
                rem_final_remaining,
                remainder_groups=rem_groups,
                min_width=min_width,
                max_width=max_width,
                tolerance_length=tolerance_len,
                originals=originals_copy
            )
            self.log_append(f"حفظ ملف : {output_path}")
        except Exception as e:
            self.log_append(f"خطأ بحفظ اكسل: {e}")

        # create pdf (محاولات توليد تقرير — إن فشل نعرض رسالة ولا نوقف العملية)
        try:
            pdf_path = os.path.splitext(output_path)[0] + "_report.pdf"
            pdf = SimplePDFReport(title="تقرير مجموعات السجاد")
            pdf.groups_to_pdf(groups, pdf_path)
            self.log_append(f"تم إنشاء تقرير PDF: {pdf_path}")
        except Exception as e:
            self.log_append("خطأ عند إنشاء PDF: " + str(e))

        # update summary table (الأصلية فقط)
        self.summary_table.setRowCount(0)
        for g in groups:
            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            self.summary_table.setItem(row, 0, QTableWidgetItem(str(len(g.items))))
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(g.ref_length())))
            self.summary_table.setItem(row, 2, QTableWidgetItem(str(g.total_width())))
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"المجموعة_{g.id}"))

        # عرض البواقي النهائية في اللوغ
        if rem_final_remaining:
            self.log_append(f"السجاد المتبقي ({len(rem_final_remaining)} أنواع):")
            for carpet in rem_final_remaining:
                self.log_append(f"  - معرف {carpet.id}: {carpet.width}x{carpet.length} (كمية متبقية: {carpet.qty})")
        else:
            self.log_append("لا يوجد سجاد متبقي - تم استخدام جميع القطع!")

# بدء التطبيق إذا شغّل الملف مباشرة
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = AdvancedRectPackApp()
    win.show()
    sys.exit(app.exec())
