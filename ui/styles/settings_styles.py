"""
Settings UI Stylesheets
Centralized stylesheet definitions for settings dialogs and components
"""


class SettingsStyles:
    """Container for all settings-related stylesheets"""
    
    @staticmethod
    def get_dialog_stylesheet():
        """Returns the main dialog stylesheet"""
        return """
            QDialog {
                background-color: #1E1E1E;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 10px;
                background-color: #2D2D2D;
                border-radius: 4px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
            }
        """
    
    @staticmethod
    def get_combo_stylesheet():
        """Returns QComboBox stylesheet"""
        return """
            QComboBox {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
        """
    
    @staticmethod
    def get_table_stylesheet():
        """Returns QTableWidget stylesheet"""
        return """
            QTableWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                gridline-color: #3A3A3A;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                color: #FFFFFF;
                padding: 5px;
                border: 1px solid #3A3A3A;
                font-weight: bold;
            }
        """
    
    @staticmethod
    def get_delete_button_stylesheet():
        """Returns delete button stylesheet"""
        return """
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #F44336;
            }
        """
    
    @staticmethod
    def get_add_dialog_stylesheet():
        """Returns add dialog stylesheet"""
        return """
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QRadioButton {
                color: #FFFFFF;
                font-size: 12px;
                spacing: 8px;
                background-color: transparent;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #5C5C5C;
                background-color: #1E1E1E;
            }
            QRadioButton::indicator:checked {
                background-color: #1976D2;
                border: 2px solid #1976D2;
            }
        """
