"""
Combined Components Demo - Final Version
Complete UI with all components in the requested order
Using ProcessingConfigSection instead of MeasurementSettingsSection
"""

import sys
import os
import json
import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QMessageBox
from PySide6.QtCore import Qt, QTimer, QElapsedTimer

# Add parent directory to path for imports
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.sections.file_management_section import FileManagementSection
from ui.sections.processing_config_section import ProcessingConfigSection
from ui.sections.current_operations_section import CurrentOperationsSection
from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget
from ui.settings_view import SettingsView
from ui.components.app_button import AppButton
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import QSize


from core.workers.grouping_worker import GroupingWorker


class CombinedDemoWindow(QMainWindow):
    """Demo window showcasing all components in the requested order"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Complete UI Demo - CutOptimizer")
        self.setGeometry(50, 50, 1600, 900)
        self.setObjectName("MainWindow")
        
        # Initialize state
        self.worker = None
        self.is_running = False
        self._suppress_log = False
        self.config_path = 'config/config.json'  # Required by background_utils
        self.config = self.load_config()
        self._init_timer()
        
        # Don't set stylesheet - let background_utils handle it via QPalette
        # Apply saved background or default gradient
        if "background_image" in self.config:
            from core.utilies.background_utils import apply_background
            apply_background(self, self.config["background_image"])
        elif "background_gradient" in self.config:
            # Apply saved gradient
            gradient_index = self.config["background_gradient"]
            # Define gradients (same as in settings_view.py)
            gradients = [
                ("أزرق سماوي (افتراضي)", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #E0F7FA)"),
                ("ليلي غامق", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e)"),
                ("غروب الشمس", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #ff9966, stop:1 #ff5e62)"),
                ("غابة خضراء", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #134E5E, stop:1 #71B280)"),
                ("بنفسجي ملكي", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2E3192, stop:1 #1BFFFF)"),
                ("رمادي عصري", "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345)")
            ]
            if 0 <= gradient_index < len(gradients):
                gradient_style = gradients[gradient_index][1]
                self.setStyleSheet(f"#MainWindow {{ background: {gradient_style}; }}")
            else:
                from core.utilies.background_utils import apply_default_gradient
                apply_default_gradient(self)
        else:
            from core.utilies.background_utils import apply_default_gradient
            apply_default_gradient(self)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header with Settings Button
        header_layout = QHBoxLayout()
        header_title = QLabel("CutOptimizer Demo")
        header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        self.settings_btn = AppButton(
            text="⚙️",
            color="transparent",
            hover_color="#0078D7",
            text_color="#333333",
            fixed_size=QSize(40, 32)
        )
        self.settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_btn)
        
        layout.addLayout(header_layout)

        # 1. File Management Section (Excel Input) - First

        self.file_section = FileManagementSection()
        layout.addWidget(self.file_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 2. Processing Configuration Section (Settings/Input) - Second
        self.config_section = ProcessingConfigSection()
        self.config_section.start_processing_signal.connect(self.run_grouping)
        self.config_section.cancel_signal.connect(self.cancel_operation)
        layout.addWidget(self.config_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 3. Current Operations Section (الخط) - Third
        self.operations_section = CurrentOperationsSection()
        # Reset progress initially
        self.operations_section.update_progress(0, "Ready", "0/0", "00:00:00", "00:00:00")
        layout.addWidget(self.operations_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 4. Summary Statistics Component (الإحصاءات) - Fourth
        self.stats_component = SummaryStatisticsComponent()
        layout.addWidget(self.stats_component, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 5. Processing Results Widget (الجدول) - Last
        self.results_widget = ProcessingResultsWidget()
        layout.addWidget(self.results_widget, 1)
    
    def resizeEvent(self, event):
        """Reapply background when window is resized"""
        if "background_image" in self.config:
            from core.utilies.background_utils import apply_background
            self._suppress_log = True
            try:
                apply_background(self, self.config["background_image"])
            finally:
                self._suppress_log = False
        super().resizeEvent(event)

    def _init_timer(self):
        """Initialize local timer"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer_display)
        self.start_time = None

    def _start_timer(self):
        """Start the timer"""
        self.start_time = QElapsedTimer()
        self.start_time.start()
        self.timer.start(1000)
        
    def _stop_timer(self):
        """Stop the timer"""
        self.timer.stop()
        self.start_time = None

    def _update_timer_display(self):
        """Update the elapsed time in the UI"""
        if self.start_time:
            seconds = self.start_time.elapsed() // 1000
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            elapsed_str = f"{h:02d}:{m:02d}:{s:02d}"
            
            # Calculate remaining time based on current progress
            current_progress = self.operations_section.progress_widget.progress_bar.value()
            remaining_str = "--:--:--"
            if current_progress > 0:
                elapsed_ms = self.start_time.elapsed()
                total_estimated_ms = (elapsed_ms / current_progress) * 100
                remaining_ms = total_estimated_ms - elapsed_ms
                if remaining_ms > 0:
                    rem_seconds = remaining_ms // 1000
                    rm, rs = divmod(rem_seconds, 60)
                    rh, rm = divmod(rm, 60)
                    remaining_str = f"{int(rh):02d}:{int(rm):02d}:{int(rs):02d}"

            # Update UI
            self.operations_section.update_progress(
                percentage=current_progress,
                elapsed=elapsed_str,
                remaining=remaining_str
            )
            self.elapsed_str = elapsed_str

    def load_config(self):
        config_path = os.path.join(os.getcwd(), 'config', 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    return cfg
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}
    
    def log_append(self, message):
        """Log message to console (required by background_utils)"""
        if self._suppress_log and "✅ تم تطبيق الخلفية بنجاح" in message:
            return
        print(message)

    def _open_settings(self):
        """Open settings dialog"""
        settings_dialog = SettingsView(parent=self)
        settings_dialog.exec()
        
        # Update machine sizes in config section
        self.config_section._load_machine_sizes()
        
        # Update dropdown options
        new_options = [f"{size['name']} ({size['min_width']}-{size['max_width']})" for size in self.config_section.machine_sizes]
        
        # Update the dropdown's options_list and refresh the list widget
        self.config_section.size_dropdown.options_list = new_options
        
        # Clear and repopulate the list widget
        self.config_section.size_dropdown.list_widget.clear()
        for item_text in new_options:
            from PySide6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(item_text)
            self.config_section.size_dropdown.list_widget.addItem(item)



    def run_grouping(self, data):
        if self.is_running:
            QMessageBox.information(self, "Info", "Operation is already running.")
            return

        # Get input path from file section
        input_path = self.file_section.get_file_path()
        if not input_path:
            QMessageBox.warning(self, "Warning", "Please select an Excel file first.")
            return
            
        # Generate output path (same dir, suffix _processed)
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_processed{ext}"
        self.output_path = output_path

        # Extract settings from data
        try:
            machine_size = data.get("machine_size", {})
            min_w = machine_size.get("min_width", 0)
            max_w = machine_size.get("max_width", 0)
            tol = int(data.get("tolerance", 5))
            
            # Update config with current settings if needed
            self.config.update({
                "min_width": min_w,
                "max_width": max_w,
                "tolerance": tol
            })
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid numeric values in settings.")
            return

        try:
            # Reset UI
            self.results_widget.set_data([])
            self.stats_component.update_statistics(0, 0, 0)
            
            self._start_timer()
            self.is_running = True
            
            # Update UI state
            self.operations_section.update_progress(0, "Starting...", "0/0", "00:00:00", "--:--:--")
            
            # Start Worker
            self.worker = GroupingWorker(
                input_path=input_path,
                output_path=output_path,
                min_width=min_w,
                max_width=max_w,
                tolerance_len=tol,
                cfg=self.config
            )

            self.worker.signals.progress.connect(self.on_worker_progress)
            self.worker.signals.error.connect(self.on_worker_error)
            self.worker.signals.data_ready.connect(self.on_worker_data_ready)
            self.worker.signals.finished.connect(self.on_worker_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start operation: {e}")
            self.reset_ui_state()

    def cancel_operation(self):
        if not self.is_running:
            return 

        try:
            if self.worker:
                self.worker.stop()
                self.operations_section.update_progress(self.operations_section.progress_widget.progress_bar.value(), "Stopping...", "", "", "")
        except Exception as e:
            print(f"Error cancelling: {e}")
        finally:
            self.reset_ui_state()

    def on_worker_progress(self, value):
        # Calculate estimated remaining time
        elapsed_str = getattr(self, "elapsed_str", "00:00:00")
        remaining_str = "--:--:--"
        
        if self.start_time and value > 0:
            elapsed_ms = self.start_time.elapsed()
            total_estimated_ms = (elapsed_ms / value) * 100
            remaining_ms = total_estimated_ms - elapsed_ms
            
            seconds = remaining_ms // 1000
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            remaining_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

        # Update progress with details
        self.operations_section.update_progress(
            percentage=value,
            current_step="Processing...",
            processed=f"{value}%", # Using percentage as proxy for processed count for now
            elapsed=elapsed_str,
            remaining=remaining_str
        )

    def on_worker_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")

    def on_worker_data_ready(self, groups, remaining, stats):
        try:
            # Prepare data for table
            table_data = []
            for g in groups:
                for item in getattr(g, "items", []):
                    table_data.append((
                        f"GRP-{getattr(g, 'group_id', '—'):03}",
                        str(getattr(item, "qty_used", 0)),
                        str(getattr(item, "qty_rem", 0)),
                        str(item.length_ref() if hasattr(item, "length_ref") else 0),
                        str(item.summary() if hasattr(item, "summary") else "-"),
                        "Completed" # Status
                    ))
            
            # Add remaining items if any (optional, depending on how we want to show them)
            # For now, let's just show grouped items in the table as per app.py logic
            
            self.results_widget.set_data(table_data)
            
            # Update Statistics
            total_original = stats.get("total_original", 0)
            total_used = stats.get("total_used", 0)
            total_remaining = stats.get("total_remaining", 0)
            
            self.stats_component.update_statistics(
                total=total_original,
                grouped=total_used,
                remaining=total_remaining
            )
            
        except Exception as e:
            print(f"Error processing results: {e}")
            traceback.print_exc()

    def on_worker_finished(self, success=True, message="Operation Completed"):
        self._stop_timer()
        self.is_running = False
        
        status_msg = "Completed Successfully" if success else "Failed"
        self.operations_section.update_progress(
            100 if success else 0, 
            status_msg, 
            elapsed=getattr(self, "elapsed_str", "00:00:00")
        )
        
        if success:
            if hasattr(self, 'output_path') and self.output_path:
                self.results_widget.set_excel_file_path(self.output_path)
            QMessageBox.information(self, "Success", "Operation completed successfully!")
        
        # self.reset_ui_state() # Optional, might want to keep results visible

    def reset_ui_state(self):
        self.is_running = False
        self._stop_timer()
        if self.worker:
            self.worker = None


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    from PySide6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))
    
    window = CombinedDemoWindow()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
