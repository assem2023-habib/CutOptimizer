"""
Processing Results Widget Component
Displays processing results in a table format with status badges and pagination
Uses GlassCardLayout for glassmorphism effect
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.components.glass_card_layout import GlassCardLayout
import qtawesome as qta
from core.actions.file_actions import open_excel_file


# Grid icon SVG for the title
GRID_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#6B4EEB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>"""


class StatusBadge(QWidget):
    """Custom widget for status badge with pill shape"""
    
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.status = status
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the badge UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        
        label = QLabel(self.status)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        
        # Set colors based on status
        if self.status == "Completed":
            bg_color = "#E6FFEE"
            text_color = "#28A745"
        elif self.status == "Pending":
            bg_color = "#FFF3E0"
            text_color = "#FFA000"
        else:
            bg_color = "#F5F5F5"
            text_color = "#333333"
        
        label.setStyleSheet(f"color: {text_color}; background: transparent;")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 15px;
            }}
        """)
        
        layout.addWidget(label)


class ProcessingResultsWidget(GlassCardLayout):
    """Processing Results table component with glassmorphism effect and pagination"""
    
    def __init__(self, parent=None):
        super().__init__(title="Processing Results", icon_svg=GRID_ICON_SVG, parent=parent)
        
        # Pagination settings
        self.current_page = 1
        self.rows_per_page = 6
        self.all_data = []  # Will hold all data
        self.total_pages = 1
        self.excel_file_path = None

        
        # Set minimum size for the card
        self.setMinimumHeight(600)
        
        self.setup_content_ui()
        self._generate_sample_data()
        self._populate_table()
    
    def setup_content_ui(self):
        """Set up the content UI"""
        # Create a container for the content
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # Export button header
        header_layout = self._create_header()
        content_layout.addLayout(header_layout)
        
        # Table
        self.table = self._create_table()
        content_layout.addWidget(self.table)
        
        # Pagination controls
        pagination_widget = self._create_pagination()
        content_layout.addWidget(pagination_widget)
        
        # Add the container to the GlassCardLayout
        self.add_content_widget(content_container)
    
    def _create_header(self) -> QHBoxLayout:
        """Create the header section with read excel button"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        header_layout.addStretch()
        
        # Read Excel button
        self.read_excel_btn = QPushButton("� Read Excel")
        self.read_excel_btn.setFont(QFont("Segoe UI", 13))
        self.read_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B4EEB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5A3DD8;
            }
            QPushButton:pressed {
                background-color: #4A2EC7;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.read_excel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.read_excel_btn.clicked.connect(self._read_excel)
        self.read_excel_btn.setEnabled(False) # Initially disabled
        header_layout.addWidget(self.read_excel_btn)
        
        return header_layout
    
    def _create_table(self) -> QTableWidget:
        """Create the results table"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Group ID", "Qty Used", "Qty Rem", "Ref Height", "Carpet", "Status"
        ])
        
        # Table styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                gridline-color: transparent;
                selection-background-color: rgba(107, 78, 235, 0.15);
            }
            QTableWidget::item {
                padding: 12px 16px;
                color: #1a1a1a;
                font-size: 14px;
                border-bottom: 1px solid rgba(240, 240, 240, 0.5);
            }
            QHeaderView::section {
                background-color: transparent;
                color: #1a1a1a;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid rgba(232, 232, 232, 0.6);
                text-align: left;
            }
        """)
        
        # Header configuration
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        # Vertical header (row numbers) - hide it
        table.verticalHeader().setVisible(False)
        
        # Row height
        table.verticalHeader().setDefaultSectionSize(56)
        
        # Disable editing
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Selection behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Font
        table.setFont(QFont("Segoe UI", 14))
        
        return table
    
    def _create_pagination(self) -> QWidget:
        """Create pagination controls"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
            }
        """)
        
        pagination_layout = QHBoxLayout(container)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.setSpacing(20)
        pagination_layout.setContentsMargins(20, 10, 20, 10)
        
        # Previous button
        prev_icon = qta.icon("fa5s.arrow-left", color="#6B4EEB")
        self.prev_button = QPushButton(prev_icon, "Previous")
        self.prev_button.setFont(QFont("Segoe UI", 12))
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6B4EEB;
                border: none;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                color: #5A3DD8;
                background-color: rgba(107, 78, 235, 0.1);
                border-radius: 5px;
            }
            QPushButton:disabled {
                color: #AAAAAA;
            }
        """)
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.prev_button.clicked.connect(self._previous_page)
        
        # Page label
        self.page_label = QLabel()
        self.page_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.page_label.setStyleSheet("color: #1a1a1a; background: transparent; border: none;")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(120)
        
        # Next button
        next_icon = qta.icon("fa5s.arrow-right", color="#6B4EEB")
        self.next_button = QPushButton(next_icon, "Next")
        self.next_button.setFont(QFont("Segoe UI", 12))
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6B4EEB;
                border: none;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                color: #5A3DD8;
                background-color: rgba(107, 78, 235, 0.1);
                border-radius: 5px;
            }
            QPushButton:disabled {
                color: #AAAAAA;
            }
        """)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.next_button.clicked.connect(self._next_page)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        
        return container
    
    def _generate_sample_data(self):
        """Generate sample data for demonstration (15 items)"""
        self.all_data = [
            ("GRP-001", "45", "5", "1.20", "CPT-101", "Completed"),
            ("GRP-002", "32", "8", "1.35", "CPT-102", "Pending"),
            ("GRP-003", "28", "12", "1.50", "CPT-103", "Completed"),
            ("GRP-004", "50", "0", "1.40", "CPT-104", "Pending"),
            ("GRP-005", "38", "7", "1.25", "CPT-105", "Completed"),
            ("GRP-006", "42", "3", "1.30", "CPT-106", "Completed"),
            ("GRP-007", "36", "9", "1.45", "CPT-107", "Pending"),
            ("GRP-008", "40", "6", "1.28", "CPT-108", "Completed"),
            ("GRP-009", "30", "10", "1.38", "CPT-109", "Pending"),
            ("GRP-010", "48", "2", "1.32", "CPT-110", "Completed"),
            ("GRP-011", "35", "8", "1.42", "CPT-111", "Pending"),
            ("GRP-012", "44", "4", "1.26", "CPT-112", "Completed"),
            ("GRP-013", "39", "7", "1.36", "CPT-113", "Completed"),
            ("GRP-014", "33", "11", "1.48", "CPT-114", "Pending"),
            ("GRP-015", "47", "1", "1.22", "CPT-115", "Completed"),
        ]
        
        self.total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)
    
    def _populate_table(self):
        """Populate table with current page data"""
        self.table.setRowCount(0)
        
        # Calculate start and end indices for current page
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.all_data[start:end]
        
        for row_idx, row_data in enumerate(page_data):
            self.table.insertRow(row_idx)
            
            # Regular text columns (Group ID, Qty Used, Qty Rem, Ref Height, Carpet)
            for col_idx in range(5):
                item = QTableWidgetItem(str(row_data[col_idx]))
                item.setFont(QFont("Segoe UI", 14))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
            
            # Status column - special handling with badge
            status = row_data[5]
            status_item = QTableWidgetItem("")  # Empty item
            self.table.setItem(row_idx, 5, status_item)
            
            # Create and set badge widget
            badge = StatusBadge(status)
            
            # Container to left-align the badge
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(16, 0, 0, 0)
            container_layout.addWidget(badge)
            container_layout.addStretch()
            
            self.table.setCellWidget(row_idx, 5, container)
        
        self._update_pagination_state()
    
    def _update_pagination_state(self):
        """Update pagination controls state"""
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
    
    def _next_page(self):
        """Navigate to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._populate_table()
    
    def _previous_page(self):
        """Navigate to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._populate_table()
    
    def set_data(self, data: list):
        """
        Set table data
        
        Args:
            data: List of tuples (group_id, qty_used, qty_rem, ref_height, carpet, status)
        """
        self.all_data = data
        self.total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.current_page = 1
        self._populate_table()
    
    def _read_excel(self):
        """Handle Read Excel button click"""
        if self.excel_file_path:
            open_excel_file(self.excel_file_path)
        else:
            print("No Excel file path set!")

    def set_excel_file_path(self, path: str):
        """Set the path for the Excel file and enable the button"""
        self.excel_file_path = path
        self.read_excel_btn.setEnabled(bool(path))

