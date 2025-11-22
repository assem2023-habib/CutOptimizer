import copy
import traceback
from PySide6.QtCore import QObject, QThread, Signal
from typing import List
from models.carpet import Carpet

from data_io.excel_io import read_input_excel, write_output_excel
from core.validation import validate_carpets
from core.grouping_algorithm import build_groups
from core.suggestion_engine import generate_suggestions

class WorkerSignals(QObject):
    progress = Signal(int)
    log = Signal(str)
    error = Signal(str)
    data_ready = Signal(object, object, dict)
    finished = Signal(bool, str)

class GroupingWorker(QThread):
    def __init__(self, input_path, output_path,
                 min_width, max_width, tolerance_len, cfg):
        super().__init__()
        self.signals = WorkerSignals()

        self.input_path = input_path
        self.output_path = output_path
        self.min_width = min_width
        self.max_width = max_width
        self.tolerance_len = tolerance_len
        self.cfg = cfg

        self._is_interrupted = False
    
    def run(self):
        try:
            self._check_interrupt()
            # self.signals.progress.emit(5)
            self.signals.log.emit("📖 بدء قراءة ملف البيانات...")

            carpets = read_input_excel(self.input_path)
            self.signals.log.emit(f"✅ تم قراءة {len(carpets)} نوع من السجاد")

            self._check_interrupt()
            # self.signals.progress.emit(15)

            errs = validate_carpets(carpets)
            if errs:
                for e in errs:
                    self.signals.log.emit(f"⚠️ {e}")
            
            # self.signals.progress.emit(30)
            self.signals.log.emit("🔄 بدء تشكيل المجموعات...")

            original_carpets = copy.deepcopy(carpets)

            self._check_interrupt()

            carpets = self.merge_duplicate_carpets(carpets)
            
            groups = build_groups(
                carpets= carpets,
                min_width=self.min_width,
                max_width=self.max_width,
                max_partner=self.cfg.get("max_partner", 7),
                tolerance=self.tolerance_len,
            )
            

            self.signals.log.emit(f"✅ تم تشكيل {len(groups)} مجموعة")
            # self.signals.progress.emit(60)

            self._check_interrupt()
            self.signals.log.emit("📦 حساب المتبقيات...")

            remaining = [c for c in carpets if c.rem_qty > 0]

            total_rem= sum(c.rem_qty for c in remaining)
            total_original = sum(c.qty for c in original_carpets)
            total_used = sum(g.total_qty() for g in groups)
            utilization = (total_used / total_original * 100) if total_original > 0 else 0

            stats = {
                "total_original": total_original,
                "total_used": total_used,
                "total_remaining": total_rem,
                "utilization_percentage": utilization
            }    

            # self.signals.progress.emit(80)
            self._check_interrupt()
            suggested_groups = generate_suggestions(
                remaining=remaining,
                min_width=self.min_width,
                max_width=self.max_width,
                tolerance= self.tolerance_len
            )
            self._check_interrupt()

            self.signals.log.emit("💾 حفظ النتائج...")

            write_output_excel(
                path=self.output_path,
                groups=groups,
                remaining=remaining,
                min_width=self.min_width,
                max_width=self.max_width,
                tolerance_length= self.tolerance_len,
                originals=original_carpets,
                suggested_groups= suggested_groups,
                )
            
            self.signals.log.emit(f"✅ تم حفظ النتائج في: {self.output_path}")
            # self.signals.progress.emit(100)

            self.signals.data_ready.emit(groups, remaining, stats)
            self.signals.finished.emit(True,"تمت العملية بنجاح ✅")

        except InterruptedError:
            self.signals.log.emit("🛑 تم إيقاف العملية من قبل المستخدم.")
            self.signals.finished.emit(False, "تم الإيقاف يدويًا.")
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit(tb)
            self.signals.finished.emit(False, f"حدث خطأ أثناء المعالجة: {str(e)}")

    def _check_interrupt(self):
        if self._is_interrupted:
            raise InterruptedError("تم إيقاف العملية يدويًا.")

    def stop(self):
        self._is_interrupted = True
        self.signals.log.emit("⚠️ تم إرسال أمر إيقاف العامل.")

        
    def merge_duplicate_carpets(self, carpets: List[Carpet]) -> List[Carpet]:
        merged = {}
        
        for carpet in carpets:
            key = (carpet.width, carpet.height)

            if key not in merged:
                merged[key] = carpet
            else:
                original = merged[key]

                if not original.repeated:
                    original.repeated.append({
                        "id": original.id,
                        "qty_original":original.qty,
                        "qty_rem":original.qty,
                        "qty": 0,
                        "client_order": original.client_order
                    })

                original.repeated.append({
                    "id": carpet.id,
                    "qty": 0,
                    "qty_original":carpet.qty,
                    "qty_rem":carpet.qty,
                    "client_order": carpet.client_order
                })

                original.qty += carpet.qty
                original.rem_qty += carpet.qty
        return list(merged.values())