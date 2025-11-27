"""
Timer Manager - Manages elapsed time and remaining time calculations
"""
from PySide6.QtCore import QTimer, QElapsedTimer


class TimerManager:
    """Manages timing for operations with elapsed and remaining time calculations"""
    
    def __init__(self, operations_section):
        """
        Initialize timer manager
        
        Args:
            operations_section: Reference to CurrentOperationsSection for updates
        """
        self.operations_section = operations_section
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)
        self.start_time = None
        self.elapsed_str = "00:00:00"
    
    def start(self):
        """Start the elapsed time timer"""
        self.start_time = QElapsedTimer()
        self.start_time.start()
        self.timer.start(1000)  # Update every second
    
    def stop(self):
        """Stop the elapsed time timer"""
        self.timer.stop()
        self.start_time = None
    
    def is_running(self):
        """Check if timer is currently running"""
        return self.start_time is not None
    
    def get_elapsed_string(self):
        """Get the current elapsed time as formatted string"""
        return self.elapsed_str
    
    def _update_display(self):
        """Update the elapsed and remaining time display"""
        if not self.start_time:
            return
        
        self.elapsed_str = self._format_elapsed_time()
        remaining_str = self._calculate_remaining_time()
        current_progress = self.operations_section.progress_widget.progress_bar.value()
        
        self.operations_section.update_progress(
            percentage=current_progress,
            elapsed=self.elapsed_str,
            remaining=remaining_str
        )
    
    def _format_elapsed_time(self):
        """Format elapsed time as HH:MM:SS"""
        if not self.start_time:
            return "00:00:00"
        
        seconds = self.start_time.elapsed() // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def _calculate_remaining_time(self):
        """Calculate and format remaining time based on current progress"""
        if not self.start_time:
            return "--:--:--"
        
        current_progress = self.operations_section.progress_widget.progress_bar.value()
        
        if current_progress <= 0:
            return "--:--:--"
        
        elapsed_ms = self.start_time.elapsed()
        total_estimated_ms = (elapsed_ms / current_progress) * 100
        remaining_ms = total_estimated_ms - elapsed_ms
        
        if remaining_ms <= 0:
            return "--:--:--"
        
        rem_seconds = remaining_ms // 1000
        rm, rs = divmod(rem_seconds, 60)
        rh, rm = divmod(rm, 60)
        return f"{int(rh):02d}:{int(rm):02d}:{int(rs):02d}"
    
    def calculate_remaining_time_for_progress(self, progress):
        """
        Calculate remaining time based on specific progress value
        
        Args:
            progress: Current progress percentage (0-100)
            
        Returns:
            Formatted remaining time string
        """
        if not self.start_time or progress <= 0:
            return "--:--:--"
        
        elapsed_ms = self.start_time.elapsed()
        total_estimated_ms = (elapsed_ms / progress) * 100
        remaining_ms = total_estimated_ms - elapsed_ms
        
        if remaining_ms <= 0:
            return "00:00:00"
        
        seconds = remaining_ms // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
