from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget
import qtawesome as qta

class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(
            self,
            parent = None,
            checked = False,
            day_color= "#E0E0E0",
            night_color= "#4A90E2",
            thumb_color= "#FFFFFF",
            animation_duration= 250):
        super().__init__(parent)

        self._checked = checked

        self._day_color = QColor(day_color)
        self._night_color = QColor(night_color)
        self._thumb_color = QColor(thumb_color)
        self._current_color = QColor(day_color if not checked else night_color)

        self._track_width = 60
        self._track_height = 28
        self._thumb_radius = 11

        self._thumb_x = 3 if not checked else self._track_height - self._thumb_radius * 2 - 3

        self._animation_duration = animation_duration

        self._thumb_anim = QPropertyAnimation(self, b"thumb_x")
        self._thumb_anim.setDuration(animation_duration)
        self._thumb_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._color_anim = QPropertyAnimation(self, b"track_color")
        self._color_anim.setDuration(animation_duration)
        self._color_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._sun_icon = qta.icon("fa5s.sun", color="#FFD700")
        self._moon_icon = qta.icon("fa5s.moon", color="#FFFFFF")

        self.setFixedSize(self._track_width,self._track_height)

    def getTrackColor(self):
        return self._current_color
    
    def setTrackColor(self, color):
        self._current_color = color
        self.update()

    track_color = Property(QColor, getTrackColor, setTrackColor)

    def getThumbX(self):
        return self._thumb_x
    
    def setThumbX(self, x):
        self._thumb_x = x
        self.update()

    thumb_x = Property(float, getThumbX, setThumbX)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(self._current_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            QRectF(0, 0, self._track_width, self._track_height),
            self._track_height / 2,
            self._track_height / 2,
        )
        
        painter.setBrush(self._thumb_color)
        painter.drawEllipse(self._thumb_x, (self._track_height - self._thumb_radius * 2) / 2,
                            self._thumb_radius * 2, self._thumb_radius * 2)
        
        icon = self._moon_icon if self._checked else self._sun_icon
        pixmap = icon.pixmap(14, 14)
        if self._checked:
            painter.drawPixmap(6, (self._track_height - 14) // 2, pixmap)
        else: 
            painter.drawPixmap(self._track_width - 20, (self._track_height -14) // 2, pixmap)
    
    def mouseReleaseEvent(self, event):
        self._checked = not self._checked
        self.animate_switch()
        self.toggled.emit(self._checked)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.unsetCursor()
        return super().leaveEvent(event)

    def animate_switch(self):
        start_x = self._thumb_x
        end_x = self._track_width - self._thumb_radius * 2 - 3 if self._checked else 3

        self._thumb_anim.stop()
        self._thumb_anim.setStartValue(start_x)
        self._thumb_anim.setEndValue(end_x)
        self._thumb_anim.start()

        self._color_anim.stop()
        self._color_anim.setStartValue(self._current_color)
        self._color_anim.setEndValue(self._night_color if self._checked else self._day_color)
        self._color_anim.start()

    def isChecked(self):
        return self._checked
