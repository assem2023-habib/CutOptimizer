"""
Main Window - CutOptimizer Application
Complete UI with all components in the requested order
"""
import sys
import os
import json
import traceback

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QScrollArea, QMessageBox, QHBoxLayout, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, QSize
from PySide6.QtGui import QFont

# Add parent directory to path for imports
sys.path.insert(0, r'c:\Users\RYZEN\Desktop\Task\CutOptimizer')

from ui.sections.file_management_section import FileManagementSection
from ui.sections.processing_config_section import ProcessingConfigSection
from ui.sections.current_operations_section import CurrentOperationsSection
from ui.components.summary_statistics_component import SummaryStatisticsComponent
from ui.components.processing_results_widget import ProcessingResultsWidget
from ui.settings_view import SettingsView
from ui.widgets.app_button import AppButton
from ui.constants.gradients import get_gradient_style
from core.workers.grouping_worker import GroupingWorker
from core.utilies.background_utils import apply_background, apply_default_gradient


class CombinedDemoWindow(QMainWindow):
    """Main window showcasing all components in the requested order"""
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_state_variables()
        self._apply_background()
        self._setup_ui()
    
    # ==================== Initialization Methods ====================
    
    def _init_window(self):
        """Initialize window properties"""
        self.setWindowTitle("Complete UI Demo - CutOptimizer")
        self.setGeometry(50, 50, 1600, 900)
        self.setObjectName("MainWindow")
    
    def _init_state_variables(self):
        """Initialize state variables"""
        self.worker = None
        self.is_running = False
        self._suppress_log = False
        self.config_path = 'config/config.json'
        self.config = self._load_config()
        self._init_timer()
    
    def _init_timer(self):
        """Initialize timer for tracking elapsed time"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer_display)
        self.start_time = None
    
    def _load_config(self):
        """Load configuration from config.json"""
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
    
    def _apply_background(self):
        """Apply background gradient or image from config"""
        if "background_image" in self.config:
            apply_background(self, self.config["background_image"])
        elif "background_gradient" in self.config:
            gradient_index = self.config["background_gradient"]
            gradient_style = get_gradient_style(gradient_index)
            self.setStyleSheet(f"#MainWindow {{ background: {gradient_style}; }}")
        else:
            apply_default_gradient(self)
    
    # ==================== UI Setup Methods ====================
    
    def _setup_ui(self):
        """Setup the main user interface"""
        # Create scroll area
        scroll = self._create_scroll_area()
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Add components
        layout.addLayout(self._create_header())
        self._add_sections(layout)
    
    def _create_scroll_area(self):
        """Create and configure scroll area"""
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
        return scroll
    
    def _create_header(self):
        """Create header with title and settings button"""
        header_layout = QHBoxLayout()
        
        # Title
        header_title = QLabel("CutOptimizer Demo")
        header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        # Settings button
        self.settings_btn = AppButton(
            text="⚙️",
            color="transparent",
            hover_color="#0078D7",
            text_color="#333333",
            fixed_size=QSize(40, 32)
        )
        self.settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_btn)
        
        return header_layout
    
    def _add_sections(self, layout):
        """Add all UI sections to the layout"""
        # 1. File Management Section
        self.file_section = FileManagementSection()
        layout.addWidget(self.file_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 2. Processing Configuration Section
        self.config_section = ProcessingConfigSection()
        self.config_section.start_processing_signal.connect(self.run_grouping)
        self.config_section.cancel_signal.connect(self.cancel_operation)
        layout.addWidget(self.config_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 3. Current Operations Section
        self.operations_section = CurrentOperationsSection()
        self.operations_section.update_progress(0, "Ready", "0/0", "00:00:00", "00:00:00")
        layout.addWidget(self.operations_section, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 4. Summary Statistics Component
        self.stats_component = SummaryStatisticsComponent()
        layout.addWidget(self.stats_component, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 5. Processing Results Widget
        self.results_widget = ProcessingResultsWidget()
        layout.addWidget(self.results_widget, 1)
    
    # ==================== Event Handlers ====================
    
    def resizeEvent(self, event):
        """Reapply background when window is resized"""
        if "background_image" in self.config:
            self._suppress_log = True
            try:
                apply_background(self, self.config["background_image"])
            finally:
                self._suppress_log = False
        super().resizeEvent(event)
    
    def log_append(self, message):
        """Log message to console (required by background_utils)"""
        if self._suppress_log and "✅ تم تطبيق الخلفية بنجاح" in message:
            return
        print(message)
    
    # ==================== Settings Methods ====================
    
    def _open_settings(self):
        """Open settings dialog and update machine sizes"""
        settings_dialog = SettingsView(parent=self)
        settings_dialog.exec()
        self._update_machine_sizes_dropdown()
    
    def _update_machine_sizes_dropdown(self):
        """Update machine sizes dropdown after settings change"""
        self.config_section._load_machine_sizes()
        new_options = [
            f"{size['name']} ({size['min_width']}-{size['max_width']})" 
            for size in self.config_section.machine_sizes
        ]
        
        self.config_section.size_dropdown.options_list = new_options
        self.config_section.size_dropdown.list_widget.clear()
        
        for item_text in new_options:
            item = QListWidgetItem(item_text)
            self.config_section.size_dropdown.list_widget.addItem(item)
    
    # ==================== Timer Methods ====================
    
    def _start_timer(self):
        """Start the elapsed time timer"""
        self.start_time = QElapsedTimer()
        self.start_time.start()
        self.timer.start(1000)
    
    def _stop_timer(self):
        """Stop the elapsed time timer"""
        self.timer.stop()
        self.start_time = None
    
    def _update_timer_display(self):
        """Update the elapsed and remaining time display"""
        if not self.start_time:
            return
        
        elapsed_str = self._format_elapsed_time()
        remaining_str = self._calculate_remaining_time()
        current_progress = self.operations_section.progress_widget.progress_bar.value()
        
        self.operations_section.update_progress(
            percentage=current_progress,
            elapsed=elapsed_str,
            remaining=remaining_str
        )
        self.elapsed_str = elapsed_str
    
    def _format_elapsed_time(self):
        """Format elapsed time as HH:MM:SS"""
        seconds = self.start_time.elapsed() // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def _calculate_remaining_time(self):
        """Calculate and format remaining time"""
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
    
    # ==================== Processing Methods ====================
    
    def run_grouping(self, data):
        """Start the grouping process"""
        if self.is_running:
            QMessageBox.information(self, "Info", "Operation is already running.")
            return
        
        input_path = self._get_input_path()
        if not input_path:
            return
        
        settings = self._extract_settings(data)
        if not settings:
            return
        
        self._start_grouping_worker(input_path, settings)
    
    def _get_input_path(self):
        """Get and validate input file path"""
        input_path = self.file_section.get_file_path()
        if not input_path:
            QMessageBox.warning(self, "Warning", "Please select an Excel file first.")
            return None
        return input_path
    
    def _extract_settings(self, data):
        """Extract and validate settings from data"""
        try:
            machine_size = data.get("machine_size", {})
            settings = {
                'min_width': machine_size.get("min_width", 0),
                'max_width': machine_size.get("max_width", 0),
                'tolerance': int(data.get("tolerance", 5))
            }
            
            # Update config
            self.config.update({
                "min_width": settings['min_width'],
                "max_width": settings['max_width'],
                "tolerance": settings['tolerance']
            })
            
            return settings
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid numeric values in settings.")
            return None
    
    def _start_grouping_worker(self, input_path, settings):
        """Initialize and start the grouping worker"""
        try:
            # Generate output path
            base, ext = os.path.splitext(input_path)
            self.output_path = f"{base}_processed{ext}"
            
            # Reset UI
            self.results_widget.set_data([])
            self.stats_component.update_statistics(0, 0, 0)
            
            # Start timer and update state
            self._start_timer()
            self.is_running = True
            self.operations_section.update_progress(0, "Starting...", "0/0", "00:00:00", "--:--:--")
            
            # Create and start worker
            self.worker = GroupingWorker(
                input_path=input_path,
                output_path=self.output_path,
                min_width=settings['min_width'],
                max_width=settings['max_width'],
                tolerance_len=settings['tolerance'],
                cfg=self.config
            )
            
            # Connect signals
            self.worker.signals.progress.connect(self.on_worker_progress)
            self.worker.signals.error.connect(self.on_worker_error)
            self.worker.signals.data_ready.connect(self.on_worker_data_ready)
            self.worker.signals.finished.connect(self.on_worker_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start operation: {e}")
            self.reset_ui_state()
    
    def cancel_operation(self):
        """Cancel the current operation"""
        if not self.is_running:
            return
        
        try:
            if self.worker:
                self.worker.stop()
                current_progress = self.operations_section.progress_widget.progress_bar.value()
                self.operations_section.update_progress(current_progress, "Stopping...", "", "", "")
        except Exception as e:
            print(f"Error cancelling: {e}")
        finally:
            self.reset_ui_state()
    
    def reset_ui_state(self):
        """Reset UI state after operation completion or cancellation"""
        self.is_running = False
        self._stop_timer()
        if self.worker:
            self.worker = None
    
    # ==================== Worker Signal Handlers ====================
    
    def on_worker_progress(self, value):
        """Handle worker progress updates"""
        elapsed_str = getattr(self, "elapsed_str", "00:00:00")
        remaining_str = self._calculate_remaining_time_for_progress(value)
        
        self.operations_section.update_progress(
            percentage=value,
            current_step="Processing...",
            processed=f"{value}%",
            elapsed=elapsed_str,
            remaining=remaining_str
        )
    
    def _calculate_remaining_time_for_progress(self, progress):
        """Calculate remaining time based on current progress"""
        if not self.start_time or progress <= 0:
            return "--:--:--"
        
        elapsed_ms = self.start_time.elapsed()
        total_estimated_ms = (elapsed_ms / progress) * 100
        remaining_ms = total_estimated_ms - elapsed_ms
        
        seconds = remaining_ms // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    
    def on_worker_error(self, error_msg):
        """Handle worker error"""
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
    
    def on_worker_data_ready(self, groups, remaining, stats):
        """Handle worker data ready signal"""
        try:
            table_data = self._prepare_table_data(groups)
            self.results_widget.set_data(table_data)
            self._update_statistics(stats)
        except Exception as e:
            print(f"Error processing results: {e}")
            traceback.print_exc()
    
    def _prepare_table_data(self, groups):
        """Prepare data for results table"""
        table_data = []
        for g in groups:
            for item in getattr(g, "items", []):
                table_data.append((
                    f"GRP-{getattr(g, 'group_id', '—'):03}",
                    str(getattr(item, "qty_used", 0)),
                    str(getattr(item, "qty_rem", 0)),
                    str(item.length_ref() if hasattr(item, "length_ref") else 0),
                    str(item.summary() if hasattr(item, "summary") else "-"),
                    "Completed"
                ))
        return table_data
    
    def _update_statistics(self, stats):
        """Update statistics display"""
        total_original = stats.get("total_original", 0)
        total_used = stats.get("total_used", 0)
        total_remaining = stats.get("total_remaining", 0)
        
        self.stats_component.update_statistics(
            total=total_original,
            grouped=total_used,
            remaining=total_remaining
        )
    
    def on_worker_finished(self, success=True, message="Operation Completed"):
        """Handle worker finished signal"""
        self._stop_timer()
        self.is_running = False
        
        status_msg = "Completed Successfully" if success else "Failed"
        self.operations_section.update_progress(
            100 if success else 0,
            status_msg,
            elapsed=getattr(self, "elapsed_str", "00:00:00")
        )
        
        if success:
            self._handle_success_completion()
    
    def _handle_success_completion(self):
        """Handle successful operation completion"""
        if hasattr(self, 'output_path') and self.output_path:
            self.results_widget.set_excel_file_path(self.output_path)
        QMessageBox.information(self, "Success", "Operation completed successfully!")