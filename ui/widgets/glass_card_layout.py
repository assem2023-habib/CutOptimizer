from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QGraphicsBlurEffect, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

class GlassCardLayout(QWidget):
    """
    مكون واجهة مستخدم قابل لإعادة الاستخدام يوفر تخطيط بطاقة زجاجية (Glassmorphism).
    يتضمن عنواناً رئيسياً وقسماً للمحتوى (عادةً مربعين جنباً إلى جنب).
    """
    
    def __init__(self, title, icon_svg=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_svg = icon_svg
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """إعداد الهيكل العام للبطاقة"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create background blur layer for glass effect
        self.blur_background = QFrame()
        self.blur_background.setObjectName("blurBackground")
        self.blur_background.setMinimumHeight(450) # Default height, can be adjusted
        
        # Apply blur effect to background
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(15)
        blur_effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.blur_background.setGraphicsEffect(blur_effect)
        
        # Card container with vertical layout
        self.card = QFrame()
        self.card.setObjectName("glassCard")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(30, 25, 30, 30)
        self.card_layout.setSpacing(20)
        
        # Setup Title Section
        self._setup_title()
        
        # Content Layout (Horizontal for side-by-side boxes)
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(40)
        self.card_layout.addLayout(self.content_layout)
        
        self.main_layout.addWidget(self.card)
        
    def _setup_title(self):
        """إعداد قسم العنوان والأيقونة"""
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        if self.icon_svg:
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            
            renderer = QSvgRenderer(self.icon_svg.encode())
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            icon_label.setPixmap(pixmap)
            title_layout.addWidget(icon_label)
            
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("mainTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        self.card_layout.addLayout(title_layout)
        
    def add_content_widget(self, widget, stretch=1):
        """إضافة عنصر واجهة مستخدم إلى منطقة المحتوى"""
        self.content_layout.addWidget(widget, stretch)
        
    def _apply_styles(self):
        """تطبيق أنماط Glassmorphism"""
        # Add soft shadow effect for the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(107, 78, 235, 60))  # Purple shadow matching theme
        self.card.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            /* Blur background layer */
            #blurBackground {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }
            
            /* Card container with Glassmorphism effect */
            #glassCard {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 18px;
                border: 0.5px solid rgba(255, 255, 255, 0.4);
            }
            
            /* Main Title */
            #mainTitle {
                color: #1a1a1a;
                font-weight: 700;
            }
        """)
