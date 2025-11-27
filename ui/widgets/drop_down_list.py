from PySide6.QtWidgets import (
    QWidget, QLabel, QListWidget, QListWidgetItem, QVBoxLayout,
    QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QGraphicsBlurEffect,
    QApplication
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent, QSize, QRect
from PySide6.QtGui import QColor, QPixmap, QPainter, QPolygon, QBrush, QIcon

class DropDownList(QWidget):
    def __init__(self,
                 selected_value_text="Select....",
                 dropdown_background_color="#3C3C3C",
                 dropdown_border_color="#666666",
                 selected_value_text_color="#FFFFFF",
                 indicator_icon_type="caret-down",
                 indicator_icon_color="#CCCCCC",
                 options_list=None,
                 option_text_color="#FFFFFF",
                 option_hover_color="#505050",
                 is_enabled=True,
                 custom_height=40,
                 parent=None,
                 ):
        super().__init__(parent)
        self.selected_value_text = selected_value_text
        self.dropdown_background_color = dropdown_background_color
        self.dropdown_border_color = dropdown_border_color
        self.selected_value_text_color = selected_value_text_color
        self.indicator_icon_type = indicator_icon_type
        self.indicator_icon_color = indicator_icon_color
        self.options_list = options_list or ["Option 1", "Option 2", "Option 3"]
        self.option_text_color = option_text_color
        self.option_hover_color = option_hover_color
        self.is_enabled = is_enabled
        self.custom_height = custom_height

        self._menu_visible = False
        self._setup_ui()
        self._apply_styles()
        
        # Install event filter on the application to detect outside clicks
        QApplication.instance().installEventFilter(self)

    def _setup_ui(self):
        self.setFixedHeight(self.custom_height)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.selector_btn = QPushButton(self.selected_value_text)
        self.selector_btn.setFixedHeight(self.custom_height)
        self.selector_btn.setCursor(Qt.PointingHandCursor)
        self.selector_btn.clicked.connect(self.toggle_menu)

        self.arrow_label = QLabel()
        self.arrow_label.setPixmap(self._get_icon(self.indicator_icon_type, self.indicator_icon_color))
        self.arrow_label.setFixedSize(24, 24)
        self.arrow_label.setAlignment(Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(15, 0, 10, 0) # Increased left margin
        btn_layout.addStretch()
        btn_layout.addWidget(self.arrow_label)
        self.selector_btn.setLayout(btn_layout)

        layout.addWidget(self.selector_btn)

        # Setup List Widget
        self.list_widget = QListWidget()
        self.list_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        
        for item_text in self.options_list:
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self._on_item_selected)

        # Shadow for the button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Animation
        self.animation = QPropertyAnimation(self.list_widget, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300) # ms

    def _apply_styles(self):
        base_style = f"""
            QPushButton{{
                background-color: {self.dropdown_background_color};
                color: {self.selected_value_text_color};
                border: 1px solid {self.dropdown_border_color};
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover{{
                background-color: {self._adjust_color(self.dropdown_background_color, 10)};
                border: 1px solid {self._adjust_color(self.dropdown_border_color, 20)};
            }}
            QPushButton:pressed{{
                background-color: {self._adjust_color(self.dropdown_background_color, -10)};
            }}
            QPushButton:disabled{{
                background-color: #555555;
                color: #AAAAAA;
                border: 1px solid #555555;
            }}
        """
        self.selector_btn.setStyleSheet(base_style)
        
        list_style = f"""
            QListWidget{{
                background-color: {self.dropdown_background_color};
                color: {self.option_text_color};
                border: 2px solid {self.dropdown_border_color};
                border-radius: 8px;
                outline: none;
                padding: 5px;
            }}
            
            QListWidget::item {{
                height: 35px;
                padding-left: 10px;
                border-radius: 5px;
                margin-bottom: 2px;
            }}

            QListWidget::item:hover{{
                background-color: {self.option_hover_color};
            }}
            
            QListWidget::item:selected{{
                background-color: {self.option_hover_color};
                color: {self.option_text_color};
            }}
        """
        self.list_widget.setStyleSheet(list_style)
        self.setDisabled(not self.is_enabled)
    
    def _adjust_color(self, hex_color, factor):
        """Adjusts the brightness of a hex color."""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        l = max(min(l + factor, 255), 0)
        color.setHsl(h, s, l, a)
        return color.name()

    def _get_icon(self, icon_type, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.NoPen)

        if "down" in icon_type:
            polygon = QPolygon([QPoint(4, 6), QPoint(12, 6), QPoint(8, 10)])
        else:
            polygon = QPolygon([QPoint(4, 10), QPoint(12, 10), QPoint(8, 6)])
        
        painter.drawPolygon(polygon)
        painter.end()
        return pixmap
    
    def _on_item_selected(self, item):
        self.selected_value_text = item.text()
        self.selector_btn.setText(self.selected_value_text)
        self.hide_menu()
    
    def get_selected_value(self):
        return self.selected_value_text
    
    def setDisabled(self, disabled):
        self.selector_btn.setDisabled(disabled)
        super().setDisabled(disabled)

    def toggle_menu(self):
        if self._menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        if self._menu_visible:
            return

        # Calculate position
        global_pos = self.selector_btn.mapToGlobal(QPoint(0, 0))
        x = global_pos.x()
        y = global_pos.y() + self.selector_btn.height() + 5 # 5px gap
        
        width = self.width()
        # Calculate height based on items, max 200
        content_height = min(200, len(self.options_list) * 37 + 10) # 35px item + 2px margin + padding

        self.list_widget.setGeometry(x, y, width, 0)
        self.list_widget.show()
        
        # Animate height
        self.animation.setStartValue(QRect(x, y, width, 0))
        self.animation.setEndValue(QRect(x, y, width, content_height))
        self.animation.start()

        self._menu_visible = True
        self.arrow_label.setPixmap(self._get_icon("caret-up", self.indicator_icon_color))

    def hide_menu(self):
        if not self._menu_visible:
            return

        self._menu_visible = False
        self.arrow_label.setPixmap(self._get_icon("caret-down", self.indicator_icon_color))
        
        # Disconnect all previous connections to avoid accumulation
        try:
            self.animation.finished.disconnect()
        except:
            pass
        
        # Animate closing
        current_rect = self.list_widget.geometry()
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(QRect(current_rect.x(), current_rect.y(), current_rect.width(), 0))
        
        # Connect hide only once for this animation
        self.animation.finished.connect(self._on_hide_animation_finished)
        self.animation.start()
    
    def _on_hide_animation_finished(self):
        """Called when hide animation finishes"""
        self.list_widget.hide()
        # Disconnect to avoid repeated calls
        try:
            self.animation.finished.disconnect(self._on_hide_animation_finished)
        except:
            pass

    def eventFilter(self, obj, event):
        if self._menu_visible and event.type() == QEvent.MouseButtonPress:
            # Check if click is inside the list widget
            list_local_pos = self.list_widget.mapFromGlobal(event.globalPos())
            click_in_list = self.list_widget.rect().contains(list_local_pos)
            
            # Check if click is inside the selector button
            btn_local_pos = self.selector_btn.mapFromGlobal(event.globalPos())
            click_in_btn = self.selector_btn.rect().contains(btn_local_pos)
            
            # Only close if click is outside both
            if not click_in_list and not click_in_btn:
                self.hide_menu()
                return False  # Let the event propagate
        return super().eventFilter(obj, event)

