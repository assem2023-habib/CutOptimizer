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

from core.workers.grouping_worker import GroupingWorker


class CombinedDemoWindow(QMainWindow):
    """Demo window showcasing all components in the requested order"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Complete UI Demo - CutOptimizer")
        self.setGeometry(50, 50, 1600, 900)
        
        # Initialize state
        self.worker = None
        self.is_running = False
        self.config = self.load_config()
        self._init_timer()
        
        # Set diagonal gradient from white to sky blue
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF,
                    stop:0.3 #F8FCFF,
                    stop:0.6 #EFF8FF,
                    stop:1 #D4EDFF
                );
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Central widget
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
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
            
            # Update UI
            self.operations_section.update_progress(
                percentage=self.operations_section.progress_widget.progress_bar.value(),
                elapsed=elapsed_str
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
        # We might want to pass more info here if available, but for now just update percentage
        self.operations_section.update_progress(
            percentage=value,
            current_step="Processing...",
            elapsed=getattr(self, "elapsed_str", "00:00:00")
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
