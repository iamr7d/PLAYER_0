from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFontMetrics, QPainterPath

class ModernWindowControls(QWidget):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            self._dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_dragging'):
            self._dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("windowControlsBar")
        # Black background for top bar (or transparent if you want no bar)
        self.setStyleSheet("background: #000; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Branding label (left)
        # --- Premium animated branding label: gradient shine sweep ---
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QBrush

        class AnimatedBrandingLabel(QLabel):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setText("")
                self.offset = 0
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.animate)
                self.timer.start(30)
                self.setStyleSheet("padding-left:13px; padding-right:10px; background: transparent;")
                # Load Gotham-UltraItalic.otf from fonts directory
                import os
                from PyQt6.QtGui import QFontDatabase, QFont
                fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
                gotham_ultra_italic_path = os.path.join(fonts_dir, 'Gotham-UltraItalic.otf')
                font_loaded = False
                if os.path.exists(gotham_ultra_italic_path):
                    font_id = QFontDatabase.addApplicationFont(gotham_ultra_italic_path)
                    if font_id != -1:
                        family = QFontDatabase.applicationFontFamilies(font_id)[0]
                        self.gotham_font = QFont(family, 13, QFont.Weight.Bold, italic=True)
                        font_loaded = True
                    else:
                        print('[WARNING] Failed to load Gotham-UltraItalic.otf, using fallback font.')
                if not font_loaded:
                    self.gotham_font = QFont("Arial", 13, QFont.Weight.Bold, italic=True)
                self.setFont(self.gotham_font)
                self.text_main = "FILMDA."
                self.text_sub = "AI Player"

            def sizeHint(self):
                fm_main = QFontMetrics(QFont("Gotham Bold Italic", 13, QFont.Weight.Bold, italic=True))
                fm_sub = QFontMetrics(QFont("Gotham", 11))
                total_width = 13 + fm_main.horizontalAdvance(self.text_main) + 6 + fm_sub.horizontalAdvance(self.text_sub) + 13
                total_height = max(fm_main.height(), fm_sub.height()) + 6
                return QSize(total_width, total_height)

            def animate(self):
                self.offset = (self.offset + 4) % (self.width() + 80)
                self.update()

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                # --- Animate FILMDA. AI with a wide, bright shine ---
                painter.setFont(self.gotham_font)
                fm = QFontMetrics(self.gotham_font)
                y = (self.height() + fm.ascent() - fm.descent()) // 2
                text_x = 13
                text_main = self.text_main
                text_sub = self.text_sub
                text_main_width = fm.horizontalAdvance(text_main)
                # Draw animated gradient only over FILMDA. AI
                grad = QLinearGradient(text_x + self.offset - 120, 0, text_x + self.offset + 80, 0)
                grad.setColorAt(0.0, QColor("#3e4b8a"))
                grad.setColorAt(0.35, QColor("#3e4b8a"))
                grad.setColorAt(0.45, QColor(255,255,255,235))  # Brighter, wider shine
                grad.setColorAt(0.55, QColor("#3e4b8a"))
                grad.setColorAt(1.0, QColor("#3e4b8a"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(grad))
                # Draw FILMDA. AI with animated brush
                path = QPainterPath()
                path.addText(text_x, y, self.gotham_font, text_main)
                painter.drawPath(path)
                # Draw 'Player' static, regular
                painter.setPen(QColor("#666"))
                painter.setFont(QFont("Gotham", 11, QFont.Weight.Normal, italic=False))
                x = text_x + text_main_width + 6
                painter.drawText(x, y, text_sub)

        self.brandingLabel = AnimatedBrandingLabel()
        layout.addWidget(self.brandingLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        # Add a stretch/spacer after branding, so file name is right-aligned
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # File name label (always visible, now right-aligned)
        self.titleLabel = QLabel()
        self.titleLabel.setObjectName("windowTitleLabel")
        self.titleLabel.setStyleSheet("font-size: 10px; color: #b0b8c9; font-family: 'Gotham', 'GothamRegular', Arial, sans-serif; font-weight: 400; padding: 0 2px 0 0; background: transparent; text-align: right;")
        self.titleLabel.setMinimumWidth(32)
        self.titleLabel.setMaximumWidth(140)
        self.titleLabel.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)

        # Window control buttons (min, max, close)
        self.minBtn = QPushButton()
        self.maxBtn = QPushButton()
        self.closeBtn = QPushButton()
        self.minBtn.setObjectName("minBtn")
        self.maxBtn.setObjectName("maxBtn")
        self.closeBtn.setObjectName("closeBtn")
        self.minBtn.setIcon(QIcon(r"icons/minimise.png"))
        self.maxBtn.setIcon(QIcon(r"icons/maximize.png"))
        self.closeBtn.setIcon(QIcon(r"icons/close.png"))
        for btn in (self.minBtn, self.maxBtn, self.closeBtn):
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)
        # Connect signals
        self.closeBtn.clicked.connect(self.on_close)
        self.minBtn.clicked.connect(self.on_min)
        self.maxBtn.clicked.connect(self.on_max)

    def set_buttons_visible(self, visible):
        for btn in (self.minBtn, self.maxBtn, self.closeBtn):
            btn.setVisible(visible)

    def set_branding_visible(self, visible):
        self.brandingLabel.setVisible(visible)

    def set_title(self, text):
        """
        Set the window title label to a cleaned movie/show name using robust extraction logic (same as overlay).
        """
        import re
        if text:
            # Remove extension
            name = re.sub(r'\.[^.]+$', '', text)
            # Replace dots and underscores with spaces
            name = re.sub(r'[._]+', ' ', name)
            # Try to stop at year if present (e.g. 2024, 1999)
            match_year = re.search(r'(19|20)\d{2}', name)
            cut_idx = match_year.end() if match_year else None
            # Remove known tags and everything after first occurrence
            tag_regex = r'\b(1080p|720p|2160p|4k|8k|blu[- ]?ray|brrip|web[- ]?dl|webrip|hdrip|dvdrip|x264|x265|hevc|aac|ac3|mp3|h264|dsr|ds4k|ds|repack|remux|remastered|subs|dubbed|dual[- ]?audio|proper|uncut|extended|limited|hd|sd|cam|hdtv|yts|yify|rarbg|smg|ettv|etrg|evo|galaxy|mkvcage|mkvhub|sonyliv|amazon|netflix|prime|hotstar|zee5|voot|disney|apple|atv|amzn|hmax|web|tc|ts|dv|rip|hdr|uhd|sdr|avc|vc1|dts|truehd|flac|mka|mks|mkv|mp4|avi|mov|wmv|mov|mpg|mpeg|ogg|ogm|wmv|rmvb|rm|divx|xvid|fgt|rarbg|evo|yify|yts)\b'
            match_tag = re.search(tag_regex, name, re.IGNORECASE)
            if match_tag:
                cut_idx = min(cut_idx, match_tag.start()) if cut_idx else match_tag.start()
            if cut_idx:
                name = name[:cut_idx]
            # Remove trailing non-word chars
            name = re.sub(r'[^\w\s]+$', '', name)
            # Remove extra spaces
            name = re.sub(r'\s+', ' ', name).strip()
            # Safety: If name is too short, fall back to first 2 words
            if len(name) < 4:
                name = ' '.join(text.replace('.', ' ').replace('_', ' ').split()[:2])
            # Title case for display
            name = name.title()
            self.titleLabel.setText(f"<span style='font-family: Gotham, Arial, sans-serif; font-size:10px; color:#b0b8c9; font-weight:400;'>{name} |</span>")
        else:
            self.titleLabel.setText("")

    def on_close(self):
        self.window().close()
    def on_min(self):
        self.window().showMinimized()
    def on_max(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()
