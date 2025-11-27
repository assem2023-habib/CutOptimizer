from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon, QColor, QPalette 
from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve, Property, QRect, Qt

class AppButton(QPushButton):
    def __init__(
            self,
            text: str="",
            color: str  = "#0078D7",
            text_color: str = "#FFFFFF",
            hover_color: str = "#3399FF",
            fixed_size: QSize = QSize(180, 40),
            pressed_backgroundColor: str = "#1E1E1E",
            disabled_backgroundColor: str = "#555555",
            disabled_color: str = "#AAAAAA",
            parent = None,
    ):
        super().__init__(text, parent)
        self._base_color = QColor(color)
        self.text_color = text_color
        self._hover_color =  QColor(hover_color)
        self._current_color = self._base_color
        self.fixed_size =fixed_size
        self.pressed_backgroundColor = pressed_backgroundColor
        self.disabled_backgroundColor = disabled_backgroundColor
        self.disabled_color = disabled_color
        self._animation = None

        self._setup_ui()


    def getColor(self):
        return self._current_color
    
    def setColor(self, color):
        self._current_color = color
        self._update_style()

    colorProp = Property(QColor, getColor, setColor) 

    def _setup_ui(self):
        self.setFixedSize(self.fixed_size)
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
                    QPushButton {{
                               background-color: {self._current_color.name()};
                               color: {self.text_color};
                               border: none;
                               border-radius: 5px;
                               font-size: 14px;
                               font-weight: 500;
                               padding: 8px 12px;
                    }}
                    QPushButton:pressed {{
                            background-color: {self.pressed_backgroundColor};
                    }}
                    QPushButton:disabled {{
                            background-color: {self.disabled_backgroundColor};
                            color: {self.disabled_color};
                    }}
            """)
        
    def setDisabled(self, disabled):
        super().setDisabled(disabled)
        if disabled and self._animation:
            self._animation.stop()

        
    def enterEvent(self, event):
        self.animate_color(self._hover_color)
        self.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,120))
        shadow.setOffset(2, 0)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_color(self._base_color)
        self.unsetCursor()
        self.setGraphicsEffect(None)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if not self.isEnabled():
            return super().mousePressEvent(event)
        self._original_geometry = self.geometry()
        new_width = int(self.width() * 0.95)
        new_height = int(self.height() * 0.95)
        dx = (self.width() - new_width) // 2
        dy = (self.height() - new_height) // 2
        target_rect = QRect(
            self.x() + dx,
            self.y() + dy,
            new_width,
            new_height
        )
        self._press_anim = QPropertyAnimation(self, b"geometry")
        self._press_anim.setDuration(100)
        self._press_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._press_anim.setStartValue(self.geometry())
        self._press_anim.setEndValue(target_rect)
        self._press_anim.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, e):
        if hasattr(self, "_original_geometry"):
                anim = QPropertyAnimation(self, b"geometry")
                anim.setDuration(100)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setStartValue(self.geometry())
                anim.setEndValue(self._original_geometry)
                anim.start()
                self._release_anim = anim

        super().mouseReleaseEvent(e)
    
    def animate_color(self, target_color: QColor):
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"colorProp")
        self._animation.setDuration(250)
        self._animation.setStartValue(self._current_color)
        self._animation.setEndValue(target_color)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._animation.start()
