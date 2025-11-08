from PySide6.QtWidgets import (
    QWidget, QLabel, QListWidget, QListWidgetItem, QVBoxLayout,
    QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QGraphicsBlurEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QPixmap, QPainter, QPolygon, QBrush

class DropDownList(QWidget):
    def __init__(self,
                 selected_value_text= "Select....",
                 dropdown_background_color= "#3C3C3C",
                 dropdown_border_color= "#666666",
                 selected_value_text_color= "#FFFFFF",
                 indicator_icon_type= "caret-down",
                 indicator_icon_color= "#CCCCCC",
                 options_list= None,
                 option_text_color= "#FFFFFF",
                 option_hover_color= "#505050",
                 is_enabled= True,
                 parent= None,
                 ):
        super().__init__(parent)
        self.selected_value_text= selected_value_text
        self.dropdown_background_color= dropdown_background_color
        self.dropdown_border_color= dropdown_border_color
        self.selected_value_text_color= selected_value_text_color
        self.indicator_icon_type= indicator_icon_type
        self.indicator_icon_color= indicator_icon_color
        self.options_list= options_list or  ["Option 1", "Option 2", "Option 3"]
        self.option_text_color= option_text_color
        self.option_hover_color= option_hover_color
        self.is_enabled= is_enabled

        self._menu_visible= False
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):

        self.setFixedHeight(40)
        layout= QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.selector_btn = QPushButton(self.selected_value_text)
        self.selector_btn.setFixedHeight(40)
        self.selector_btn.setCursor(Qt.PointingHandCursor)
        self.selector_btn.clicked.connect(self.toggle_menu)

        self.arrow_label= QLabel()
        self.arrow_label.setPixmap(self._get_icon(self.indicator_icon_type, self.indicator_icon_color))
        self.arrow_label.setFixedSize(16, 16)

        btn_layout= QHBoxLayout()
        btn_layout.setContentsMargins(10, 0, 10, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(self.arrow_label)
        self.selector_btn.setLayout(btn_layout)

        layout.addWidget(self.selector_btn)

        self.list_widget= QListWidget()
        for item_text in self.options_list:
            item= QListWidgetItem(item_text)
            self.list_widget.addItem(item)

        self.list_widget.setWindowFlags(Qt.Popup)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setVisible(False)
        self.list_widget.itemClicked.connect(self._on_item_selected)

        shadow= QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(2, 3)
        self.setGraphicsEffect(shadow)

        blur= QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.selector_btn.setGraphicsEffect(blur)

    def _apply_styles(self):
        base_style= f"""
            QPushButton{{
                background-color: {self.dropdown_background_color};
                color: {self.selected_value_text_color};
                border: 1px solid {self.dropdown_border_color};
                border-radius: 5px;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton:hover{{
                background-color:#4C4C4C;
            }}
            QPushButton:disabled{{
                background-color: #555555;
                color: #AAAAAA;
            }}
        """
        self.selector_btn.setStyleSheet(base_style)
        list_style= f"""
            QListWidget{{
                background-color: {self.dropdown_background_color};
                color: {self.option_text_color};
                border: 1px solid {self.dropdown_border_color};
                border-top: none;
                border-radius: 0 0 5px 5px;
            }}
            
            QListWidget::item {{
                height: 30px;
                padding-left: 10px;
            }}

            QListWidget::item:hover{{
                background-color: {self.option_hover_color};
            }}
        """
        self.list_widget.setStyleSheet(list_style)
        self.setDisabled(not self.is_enabled)
    
    def _get_icon(self, icon_type, color):
        pixmap= QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter= QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.NoPen)

        if "down" in icon_type:
            polygon= QPolygon([QPoint(4, 6), QPoint(12, 6), QPoint(8, 10)])
        else:
            polygon= QPolygon([QPoint(4, 10), QPoint(12, 10), QPoint(8, 6)])
        
        painter.drawPolygon(polygon)
        painter.end()
        return pixmap
    
   
    def _on_item_selected(self, item):
        self.selected_value_text= ""
        new_text= item.text()
        self.selected_value_text= new_text
        self.selector_btn.setText(new_text)
        
        self.arrow_label.setPixmap(self._get_icon("caret-down", self.indicator_icon_color))
        self._menu_visible= False
        self.list_widget.hide()
    
    def get_selected_value(self):
        return self.selected_value_text
    
    def setDisabled(self, disabled):
        self.selector_btn.setDisabled(disabled)
        super().setDisabled(disabled)

    def toggle_menu(self):
        if self._menu_visible:
            self.list_widget.hide()
            self._menu_visible= False
            self.arrow_label.setPixmap(
                self._get_icon("caret-down", self.indicator_icon_color)
            )
        
        else:
            global_pos= self.mapToGlobal(self.selector_btn.pos())
            x= global_pos.x()
            y= global_pos.y() + self.selector_btn.height()
            self.list_widget.move(x, y)
            self.list_widget.setFixedWidth(self.width())
            self.list_widget.setMinimumHeight(0)
            self.list_widget.setMaximumHeight(min(200, len(self.options_list) *30))

            self.list_widget.show()
            self._menu_visible= True
            self.arrow_label.setPixmap(self._get_icon("caret-up", self.indicator_icon_color))
