import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPalette, QColor, QLinearGradient
from current_operations_widget import CurrentOperationsWidget


class DemoWindow(QMainWindow):
    """Demo window to showcase the Current Operations widget"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Current Operations - Glass Component Demo")
        self.setMinimumSize(900, 700)
        
        # Setup main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout with margins
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Add the Current Operations widget
        self.operations_widget = CurrentOperationsWidget()
        layout.addWidget(self.operations_widget)
        
        layout.addStretch()
        
        # Set gradient background to showcase glass effect
        self.setup_background()
        
        # Setup demo animation timer
        self.setup_demo_animation()
    
    def setup_background(self):
        """Setup a gradient background to showcase the glass morphism effect"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E8EAF6,
                    stop:0.5 #C5CAE9,
                    stop:1 #9FA8DA
                );
            }
        """)
    
    def setup_demo_animation(self):
        """Setup a timer to animate the progress for demo purposes"""
        self.progress = 67
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_demo_progress)
        self.timer.start(1000)  # Update every second
    
    def update_demo_progress(self):
        """Update progress for demo animation"""
        self.progress = (self.progress + 1) % 101
        
        # Calculate derived values
        total = 1245
        processed = int((self.progress / 100) * total)
        success = int(processed * 0.793)
        remaining = total - processed
        
        elapsed_mins = int((self.progress / 100) * 5)
        elapsed_secs = int(((self.progress / 100) * 5 * 60) % 60)
        
        remaining_mins = int(((100 - self.progress) / 100) * 5)
        remaining_secs = int((((100 - self.progress) / 100) * 5 * 60) % 60)
        
        # Update the widget
        self.operations_widget.update_progress(
            percentage=self.progress,
            current_step="Grouping Items" if self.progress < 70 else "Finalizing",
            processed=f"{processed} / {total}",
            elapsed=f"{elapsed_mins}m {elapsed_secs}s",
            remaining=f"{remaining_mins}m {remaining_secs}s"
        )
        
        self.operations_widget.update_statistics(
            total=f"{total:,}",
            success=f"{success:,}",
            remaining=f"{remaining:,}"
        )


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    app.setFont(app.font("Segoe UI", 10))
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
