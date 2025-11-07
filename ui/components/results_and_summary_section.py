from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from ui.components.created_groups_table import CreatedGroupsTable
from ui.components.process_summary_card import ProcessSummaryCard

class ResultsAndSummarySection(QWidget):
    def __init__(
            self,
            section_background_color= "#1E1E1E",
            table_component_props= None,
            summary_component_props= None,
            parent= None
    ):
        super().__init__(parent)
        self.section_background_color = section_background_color
        self.table_component_props = table_component_props or {}
        self.summary_component_props = summary_component_props or {}

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(18)
        self.setStyleSheet(f"background-color: {self.section_background_color}")

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)
        left_container.setStyleSheet("""
            background-color: #2E2E2E;
            border-radius: 10px;
        """)

        title_left = QLabel("Created Groups")
        title_left.setStyleSheet("color: #CCCCCC; font-size: 13pt; font-weight: bold;")
        left_layout.addWidget(title_left)

        self.groups_table = CreatedGroupsTable(
            parent= self,
            **self.table_component_props
        )
        left_layout.addWidget(self.groups_table)
        main_layout.addWidget(left_container, 2)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        right_container.setStyleSheet("""
            background-color: #2E2E2E;
            border-radius: 10px;
        """)

        title_right = QLabel("Process Summary")
        title_right.setStyleSheet("color: #CCCCCC; font-size: 13pt; font-weight: bold;")
        right_layout.addWidget(title_right)

        cards_props = self.summary_component_props or {
            "card_background": "#2E2E2E",
            "title_color": "#AAAAAA",
            "main_value_color": "#FFFFFF",
        }

        self.card_total_files = ProcessSummaryCard(
            title="TOTAL FILES",
            main_value="248",
            progress_percentage=100,
            progress_arc_color="#0078D7",
            progress_track_color="#404040",
            **cards_props
        )

        self.card_success_rate = ProcessSummaryCard(
            title="SUCCESS RATE",
            main_value="98.4%",
            progress_percentage=98,
            progress_arc_color="#28A745",
            progress_track_color="#404040",
            **cards_props
        )

        self.card_failed = ProcessSummaryCard(
            title="FAILED FILES",
            main_value="4",
            progress_percentage=10,
            progress_arc_color="#DC3545",
            progress_track_color="#404040",
            **cards_props
        )

        self.card_duration = ProcessSummaryCard(
            title="DURATION",
            main_value="2m 34s",
            progress_percentage=0,
            show_percentage_text=False,
            progress_arc_color="#6C757D",
            progress_track_color="#404040",
            **cards_props
        )

        right_layout.addWidget(self.card_total_files)
        right_layout.addWidget(self.card_success_rate)
        right_layout.addWidget(self.card_failed)
        right_layout.addWidget(self.card_duration)
        right_layout.addStretch()
        main_layout.addWidget(right_container, 1)
        
    def update_summary(self, total_files, success_rate, failed_files, duration):
        self.card_total_files.setValue(str(total_files))
        self.card_success_rate.setValue(f"{success_rate:.1f}%")
        self.card_success_rate.setProgress(int(success_rate))
        self.card_failed.setValue(str(failed_files))
        self.card_duration.setValue(duration)