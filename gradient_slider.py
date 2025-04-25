from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QPen, QLinearGradient, QColor, QPainterPath
import math

class GradientSlider(QSlider):
    hoverPositionChanged = pyqtSignal(float)

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setObjectName("positionSlider")
        self.setMinimumHeight(24)
        self.gradient_shift = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_gradient)
        self.timer.start(40)  # ~25 FPS
        self._gradient_colors = [  # Default gradient (progress bar style)
            (0.0, '#4f8cff'),
            (0.5, '#8f5cff'),
            (1.0, '#ff6ec4')
        ]
        self._glow_color = QColor(79, 140, 255, 80)
        self._buffering = False
        self._buffer_anim_offset = 0

    def set_buffering(self, buffering: bool):
        self._buffering = buffering
        self.update()

    def set_gradient_colors(self, stops):
        """
        Set gradient stops: list of (position, color_str) tuples, e.g. [(0.0, '#4f8cff'), (1.0, '#8f5cff')]
        """
        self._gradient_colors = stops
        self.update()

    def set_glow_color(self, color):
        self._glow_color = color
        self.update()

    def animate_gradient(self):
        self.gradient_shift = (self.gradient_shift + 0.0125) % 1.0
        if self._buffering:
            self._buffer_anim_offset = (self._buffer_anim_offset + 4) % 32
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x() if hasattr(event, 'position') else event.x()
            groove_rect = self.rect().adjusted(16, (self.rect().height() - 18) // 2, -16, -(self.rect().height() - 18) // 2)
            percent = (x - groove_rect.left()) / groove_rect.width()
            percent = min(max(percent, 0.0), 1.0)
            value = int(self.minimum() + percent * (self.maximum() - self.minimum()))
            self.setValue(value)
            self.sliderMoved.emit(value)
            self.sliderReleased.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x = event.position().x() if hasattr(event, 'position') else event.x()
        groove_rect = self.rect().adjusted(16, (self.rect().height() - 18) // 2, -16, -(self.rect().height() - 18) // 2)
        percent = (x - groove_rect.left()) / groove_rect.width()
        percent = min(max(percent, 0.0), 1.0)
        self.hoverPositionChanged.emit(percent)
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        groove_height = 22  # Slightly taller for modern look
        groove_y = (rect.height() - groove_height) // 2
        groove_rect = rect.adjusted(14, groove_y, -14, -groove_y)
        # Draw a full-length, low-opacity groove (background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        pill_radius = min(groove_rect.width(), groove_rect.height()) / 2
        groove_color = QColor(79, 140, 255, int(255 * 0.13))  # Low opacity blue
        painter.setBrush(groove_color)
        painter.drawRoundedRect(groove_rect, pill_radius, pill_radius)
        # Buffering animation overlay
        if getattr(self, '_buffering', False):
            stripe_width = 18
            stripe_spacing = 14
            offset = getattr(self, '_buffer_anim_offset', 0)
            painter.save()
            painter.setClipRect(groove_rect)
            painter.setPen(Qt.PenStyle.NoPen)
            for x in range(int(groove_rect.left()) - 40, int(groove_rect.right()) + 40, stripe_width + stripe_spacing):
                path = QPainterPath()
                path.moveTo(x + offset, groove_rect.top())
                path.lineTo(x + offset + stripe_width, groove_rect.top())
                path.lineTo(x + offset + stripe_width - groove_rect.height(), groove_rect.bottom())
                path.lineTo(x + offset - groove_rect.height(), groove_rect.bottom())
                path.closeSubpath()
                painter.setBrush(QColor(255,255,255,55))
                painter.drawPath(path)
            painter.restore()
        # Draw animated vibrant gradient progress
        if self.maximum() > 0:
            percent = float(self.value() - self.minimum()) / float(self.maximum() - self.minimum())
        else:
            percent = 0.0
        # Use floating-point for smooth progress
        progress_width = groove_rect.width() * percent
        progress_rect = groove_rect.adjusted(0, 0, int(progress_width - groove_rect.width()), 0)
        shift = self.gradient_shift
        grad = QLinearGradient(
            progress_rect.left() + progress_rect.width() * shift,
            0,
            progress_rect.right() + progress_rect.width() * shift,
            0
        )
        # Use custom gradient stops
        for stop, color in getattr(self, '_gradient_colors', [ (0.0, '#4f8cff'), (0.5, '#8f5cff'), (1.0, '#ff6ec4') ]):
            grad.setColorAt(stop, QColor(color))
        painter.setBrush(QBrush(grad))
        # Soft glow effect
        glow_rect = progress_rect.adjusted(-2, -3, 2, 3)
        glow_color = getattr(self, '_glow_color', QColor(79, 140, 255, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow_color)
        painter.drawRoundedRect(glow_rect, groove_height/2+2, groove_height/2+2)
        # Draw the main progress bar on top
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(progress_rect, pill_radius, pill_radius)
        painter.end()
