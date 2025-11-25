"""
مثال على استخدام قسم إدارة الملفات
Example usage of File Management Section
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.sections.file_management_section import FileManagementSection


class FileManagementDemo(QMainWindow):
    """نافذة تجريبية لعرض قسم إدارة الملفات"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataProcessor Pro - File Management Demo")
        self.setMinimumSize(1000, 600)
        
        # Set background color with gradient for better glass effect visibility
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6B4EEB,
                    stop:0.5 #8B5CF6,
                    stop:1 #A78BFA
                );
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Add File Management Section
        self.file_management = FileManagementSection()
        self.file_management.file_selected.connect(self._on_file_selected)
        layout.addWidget(self.file_management)
        
        # Add stretch to push content to top
        layout.addStretch()
        
    def _on_file_selected(self, file_path):
        """عند اختيار ملف"""
        print(f"File selected: {file_path}")
        file_info = self.file_management.get_file_info()
        print(f"File Name: {file_info['name']}")
        print(f"Rows: {file_info['rows']}")
        print(f"Columns: {file_info['columns']}")


def main():
    """تشغيل التطبيق التجريبي"""
    app = QApplication(sys.argv)
    
    # Set application font
    app.setFont(QFont("Segoe UI", 10))
    
    window = FileManagementDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
