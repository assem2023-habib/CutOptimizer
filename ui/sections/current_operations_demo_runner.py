import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
from ui.sections.current_operations_section import CurrentOperationsSection

class DemoWindow(QMainWindow):
    """Demo window to showcase the Current Operations Section"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Current Operations Section - Demo")
        self.setMinimumSize(1000, 600)
        
        # Setup main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout with margins
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Add the Current Operations Section
        self.operations_section = CurrentOperationsSection()
        layout.addWidget(self.operations_section)
        
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
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_demo_progress)
        self.timer.start(100)  # Update every 100ms for smooth demo
    
    def update_demo_progress(self):
        """Update progress for demo animation"""
        if self.progress >= 100:
            self.progress = 0
            
        self.progress += 0.5
        current_progress = int(self.progress)
        
        # Calculate derived values
        total = 1245
        processed = int((self.progress / 100) * total)
        success = int(processed * 0.793)
        remaining = total - processed
        
        # Fake time calculations
        elapsed_seconds = int((self.progress / 100) * 300) # Max 5 mins
        elapsed_mins = elapsed_seconds // 60
        elapsed_secs = elapsed_seconds % 60
        
        remaining_seconds = 300 - elapsed_seconds
        remaining_mins = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
        
        # Update the widget
        self.operations_section.update_progress(
            percentage=current_progress,
            current_step="Grouping Items" if current_progress < 70 else "Finalizing",
            processed=f"{processed} / {total}",
            elapsed=f"{elapsed_mins}m {elapsed_secs}s",
            remaining=f"{remaining_mins}m {remaining_secs}s"
        )
        



def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
