from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRectF

class RoundedVideoWidget(QVideoWidget):
    def __init__(self, radius=28, parent=None):
        super().__init__(parent)
        self.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.setStyleSheet("background: transparent;")  # No background

    def paintEvent(self, event):
        # No rounded corners, no custom painting, just show the video
        super().paintEvent(event)
