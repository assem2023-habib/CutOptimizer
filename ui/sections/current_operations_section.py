from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui.components.glass_card_layout import GlassCardLayout
from ui.components.operation_progress_widget import OperationProgressWidget

# Simple SVG for the list icon
LIST_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#6B4EEB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>"""





class CurrentOperationsSection(GlassCardLayout):
    """Main Current Operations component with glass morphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(title="Current Operations", icon_svg=LIST_ICON_SVG, parent=parent)
        self.setup_content_ui()
        
    def setup_content_ui(self):
        # Create a container for the vertical layout content
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Progress Section
        self.progress_widget = OperationProgressWidget()
        content_layout.addWidget(self.progress_widget)
        
        # Add the container to the GlassCardLayout
        self.add_content_widget(content_container)
    


    
    def update_progress(self, percentage, current_step=None, processed=None, 
                       elapsed=None, remaining=None):
        """Update progress bar and details"""
        self.progress_widget.update_progress(percentage, current_step, processed, elapsed, remaining)
    

