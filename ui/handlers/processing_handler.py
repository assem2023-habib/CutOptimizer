"""
Processing Handler - Manages worker operations and processing workflow
"""
import os
import traceback
from PySide6.QtWidgets import QMessageBox

from core.workers.grouping_worker import GroupingWorker


class ProcessingHandler:
    """Handles all processing operations including worker management"""
    
    def __init__(self, parent_window, config, timer_manager):
        """
        Initialize processing handler
        
        Args:
            parent_window: Reference to main window
            config: Configuration dictionary
            timer_manager: Timer manager instance
        """
        self.window = parent_window
        self.config = config
        self.timer_manager = timer_manager
        self.worker = None
        self.is_running = False
        self.output_path = None
    
    def start_grouping(self, data):
        """
        Start the grouping process
        
        Args:
            data: Dictionary with processing configuration
        """
        if self.is_running:
            QMessageBox.information(self.window, "Info", "Operation is already running.")
            return
        
        input_path = self._get_input_path()
        if not input_path:
            return
        
        settings = self._extract_settings(data)
        if not settings:
            return
        
        self._start_worker(input_path, settings)
    
    def cancel_operation(self):
        """Cancel the current operation"""
        if not self.is_running:
            return
        
        try:
            if self.worker:
                self.worker.stop()
                current_progress = self.window.operations_section.progress_widget.progress_bar.value()
                self.window.operations_section.update_progress(current_progress, "Stopping...", "", "", "")
        except Exception as e:
            print(f"Error cancelling: {e}")
        finally:
            self.reset_state()
    
    def reset_state(self):
        """Reset state after operation completion or cancellation"""
        self.is_running = False
        self.timer_manager.stop()
        if self.worker:
            self.worker = None
    
    def _get_input_path(self):
        """Get and validate input file path"""
        input_path = self.window.file_section.get_file_path()
        if not input_path:
            QMessageBox.warning(self.window, "Warning", "Please select an Excel file first.")
            return None
        return input_path
    
    def _extract_settings(self, data):
        """Extract and validate settings from data"""
        try:
            machine_size = data.get("machine_size", {})
            sort_type = data.get("sort_type")
            grouping_mode = data.get("grouping_mode")
            
            settings = {
                'min_width': machine_size.get("min_width", 0),
                'max_width': machine_size.get("max_width", 0),
                'tolerance': int(data.get("tolerance", 5)),
                'path_length_limit': machine_size.get("path_length_limit", 0),
                'sort_type': sort_type,
                'grouping_mode': grouping_mode
            }
            
            # Update config with ALL user selections
            self.config.update({
                "min_width": settings['min_width'],
                "max_width": settings['max_width'],
                "tolerance": settings['tolerance'],
                "path_length_limit": settings['path_length_limit'],
                "sort_type": sort_type,
                "grouping_mode": grouping_mode
            })
            
            return settings
        except ValueError:
            QMessageBox.warning(self.window, "Error", "Invalid numeric values in settings.")
            return None
    
    def _start_worker(self, input_path, settings):
        """Initialize and start the grouping worker"""
        try:
            # Generate output path
            base, ext = os.path.splitext(input_path)
            self.output_path = f"{base}_processed{ext}"
            
            # Reset UI
            self.window.results_widget.set_data([])
            self.window.stats_component.update_statistics(0, 0, 0)
            
            # Start timer and update state
            self.timer_manager.start()
            self.is_running = True
            self.window.operations_section.update_progress(0, "Starting...", "0/0", "00:00:00", "--:--:--")
            
            # Create and start worker
            self.worker = GroupingWorker(
                input_path=input_path,
                output_path=self.output_path,
                min_width=settings['min_width'],
                max_width=settings['max_width'],
                tolerance_len=settings['tolerance'],
                path_length_limit=settings['path_length_limit'],
                cfg=self.config  # Now includes sort_type and grouping_mode!
            )
            
            # Connect signals
            self.worker.signals.progress.connect(self.on_progress)
            self.worker.signals.error.connect(self.on_error)
            self.worker.signals.data_ready.connect(self.on_data_ready)
            self.worker.signals.finished.connect(self.on_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to start operation: {e}")
            self.reset_state()
    
    # ==================== Worker Signal Handlers ====================
    
    def on_progress(self, value):
        """Handle worker progress updates"""
        elapsed_str = self.timer_manager.get_elapsed_string()
        remaining_str = self.timer_manager.calculate_remaining_time_for_progress(value)
        
        self.window.operations_section.update_progress(
            percentage=value,
            current_step="Processing...",
            processed=f"{value}%",
            elapsed=elapsed_str,
            remaining=remaining_str
        )
    
    def on_error(self, error_msg):
        """Handle worker error"""
        QMessageBox.critical(self.window, "Error", f"An error occurred:\n{error_msg}")
    
    def on_data_ready(self, groups, remaining, stats):
        """Handle worker data ready signal"""
        try:
            table_data = self._prepare_table_data(groups)
            self.window.results_widget.set_data(table_data)
            self._update_statistics(stats)
        except Exception as e:
            print(f"Error processing results: {e}")
            traceback.print_exc()
    
    def on_finished(self, success=True, message="Operation Completed"):
        """Handle worker finished signal"""
        self.timer_manager.stop()
        self.is_running = False
        
        status_msg = "Completed Successfully" if success else "Failed"
        self.window.operations_section.update_progress(
            100 if success else 0,
            status_msg,
            elapsed=self.timer_manager.get_elapsed_string()
        )
        
        if success:
            self._handle_success()
    
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
        
        self.window.stats_component.update_statistics(
            total=total_original,
            grouped=total_used,
            remaining=total_remaining
        )
    
    def _handle_success(self):
        """Handle successful operation completion"""
        if self.output_path:
            self.window.results_widget.set_excel_file_path(self.output_path)
        QMessageBox.information(self.window, "Success", "Operation completed successfully!")
