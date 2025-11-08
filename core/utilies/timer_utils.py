from PySide6.QtCore import QTimer, QElapsedTimer
import types

def init_timer(self):
    """تهيئة المؤقت لمرة واحدة داخل __init__."""
    self.timer = QTimer(self)
    self.start_time = None

    self.update_duration_card = types.MethodType(update_duration_card, self)

    # ثانياً: نربطها بالمؤقت بعد أن أصبحت موجودة فعلاً
    self.timer.timeout.connect(self.update_duration_card)

def start_timer(self):
    """بدء المؤقت وتحديث بطاقة المدة كل ثانية."""
    if not hasattr(self, "timer"):
        init_timer(self)

    self.start_time = QElapsedTimer()
    self.start_time.start()

    self.results_section.card_duration.setValue("0s")
    self.timer.start(1000)
    self.log_append("⏱️ تم بدء مؤقت العملية.")

def stop_timer(self):
    """إيقاف المؤقت وتحديث المدة النهائية."""
    if not hasattr(self, "timer"):
        return

    self.timer.stop()
    if self.start_time:
        total_seconds = self.start_time.elapsed() // 1000
        formatted = format_duration(total_seconds)
        self.results_section.card_duration.setValue(formatted)
        self.log_append(f"⏱️ مدة العملية الإجمالية: {formatted}")
    self.start_time = None

def update_duration_card(self):
    """تحديث الوقت الحالي في البطاقة كل ثانية."""
    if not self.start_time:
        return

    total_seconds = self.start_time.elapsed() // 1000
    formatted = format_duration(total_seconds)
    self.results_section.card_duration.setValue(formatted)

def format_duration(total_seconds: int) -> str:
    """تحويل الثواني إلى صيغة سهلة القراءة مثل 1m 23s أو 1h 02m."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
