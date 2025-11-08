from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QSizePolicy
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
import qtawesome as qta

class CreatedGroupsTable(QWidget):
    def __init__(self,
                 parent= None,
                 table_bg= "#FFFFFF",
                 header_bg= "#F5F5F5",
                 header_text_color= "#555555",
                 row_bg= "#FFFFFF",
                 alt_row_bg= "#FAFAFA",
                 cell_text_color= "#333333",
                 border_color= "#E0E0E0",
                 pagination_text_color= "#0078D7",
                 pagination_icon_color= "#0078D7",
                 data= None
                 ):
        super().__init__(parent)
        
        self.table_bg= table_bg
        self.header_bg= header_bg
        self.header_text_color= header_text_color
        self.row_bg= row_bg
        self.alt_row_bg= alt_row_bg
        self.cell_text_color= cell_text_color
        self.border_color= border_color
        self.pagination_text_color= pagination_text_color
        self.pagination_icon_color= pagination_icon_color

        self.current_page= 1
        self.rows_per_page= 6
        # self.data= data or {self._generate_sample_data()}
        self.data= data or ()
        self.total_pages= max(1, (len(self.data) + self.rows_per_page -1) // self.rows_per_page)

        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.table= QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Group ID", "Qty Used", "Qty Rem", "Ref Height" ,"Carpet"
        ])
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setStyleSheet(f"""
                                    QTableWidget{{
                                        background-color: {self.table_bg};
                                        gridline-color: {self.border_color};
                                        border: 1px solid {self.border_color};
                                        font-size: 13px;
                                        color: {self.cell_text_color};
                                    }}
                                    QHeaderView::section {{
                                        background-color: {self.header_bg};
                                        color: {self.header_text_color};
                                        font-weight: bold;
                                        padding: 6px;
                                        border-bottom: 1px solid {self.border_color};
                                    }}
                                    QTableWidget::item {{
                                        selection-background-color: #E3F2FD;
                                        selection-color: #000;
                                    }}
                                """)
        layout.addWidget(self.table)

        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignCenter)

        prev_icon = qta.icon("fa5s.arrow-left", color= self.pagination_icon_color)
        next_icon = qta.icon("fa5s.arrow-right", color= self.pagination_icon_color)

        self.prev_button = QPushButton(prev_icon, "Previous")
        self.next_button= QPushButton(next_icon, "Next")

        for btn in (self.prev_button, self.next_button):
            btn.setStyleSheet(f"""
                    QPushButton {{
                              background-color: transparent;
                              color: {self.pagination_text_color};
                              border: none;
                              font-weight: 500;
                    }}
                    QPushButton:disabled {{
                        color: #AAAAAA;
                    }}
                """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.page_label = QLabel()
        self.page_label.setStyleSheet(f"""
                color: {self.pagination_text_color};
                font-weight: 500;
            """)
        self.page_label.setFont(QFont("Segoe UI", 10))

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addSpacing(12)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addSpacing(12)
        pagination_layout.addWidget(self.next_button)

        layout.addLayout(pagination_layout)

        self.prev_button.clicked.connect(self._previous_page)
        self.next_button.clicked.connect(self._next_page)

    def _populate_table(self):
        self.table.setRowCount(0)
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.data[start:end]

        for row_index, row_data in enumerate(page_data):
            self.table.insertRow(row_index)
            for col_index, key in enumerate(["group_id", "qty_used", "qty_rem", "ref_height", "carpet"]):
                item = QTableWidgetItem(str(row_data[key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)
        self._update_pagination_state()
    
    def _update_pagination_state(self):
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._populate_table()

    def _previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._populate_table()

    # def _generate_sample_data(self):
    #     return [
    #         {
    #             "group_id": f"GRP-{i:03}",
    #             "qty_used": f"{i * 3}",
    #             "qty_rem": f"{50 - i}",
    #             "ref_height": f"{1.2 + i*0.1:.2f}",
    #             "carpet": f"CPT-{100+i}",
    #         }
    #         for i in range(1, 26)
    #     ]