#!/usr/bin/env python3
"""
Test script to verify background image functionality
"""
import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette

def test_background_image():
    """Test if background image loads correctly"""
    app = QApplication(sys.argv)

    # Create a test window
    window = QWidget()
    window.setObjectName("mainWindow")
    window.setWindowTitle("Background Image Test")
    window.resize(800, 600)

    # Set stylesheet with background image
    stylesheet = """
    QWidget#mainWindow {
        background-image: url(./assets/images/backgrounds/background_image_light.png);
        background-repeat: no-repeat;
        background-position: center center;
        background-color: #1A1A1A;
    }
    """
    window.setStyleSheet(stylesheet)

    # Add some content to see if it's visible
    layout = QVBoxLayout(window)
    label = QLabel("Testing background image...")
    label.setStyleSheet("color: white; font-size: 24px; padding: 20px;")
    layout.addWidget(label)

    print("Current working directory:", os.getcwd())
    print("Image path exists:", os.path.exists('./assets/images/backgrounds/background_image_light.png'))

    window.show()
    return app.exec()

if __name__ == "__main__":
    test_background_image()
