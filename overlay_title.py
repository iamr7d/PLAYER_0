from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QFontDatabase
import os
import re

class OverlayTitleLabel(QLabel):
    """
    QLabel subclass that displays a styled overlay title over the video player.
    Handles font loading with fallback, cleans and extracts movie/show titles from filenames,
    and animates fade-in/fade-out for a Netflix-like overlay experience.
    """
    def __init__(self, parent=None):
        """
        Initialize the overlay label, load Gotham font if available (fallback to Arial),
        and set up animation and timer for fade effects.
        """
        super().__init__(parent)
        # Attempt to load Gotham Regular font for premium look; fallback to Arial if unavailable
        # Enhanced font loading: search 'fonts' directory for Gotham variants
        font_loaded = False
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        preferred_fonts = [
            'GothamBook.ttf', 'GothamMedium.ttf', 'Gotham-Regular.ttf', 'GothamBook.otf', 'GothamMedium.otf',
            'Gotham-Book.otf', 'Gotham-Medium.otf', 'Gotham-Bold.otf', 'GothamBold.ttf', 'GothamLight.ttf', 'Gotham-Light.otf'
        ]
        if os.path.isdir(fonts_dir):
            for fname in preferred_fonts:
                font_path = os.path.join(fonts_dir, fname)
                if os.path.exists(font_path):
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.setFont(QFont(families[0], 24))
                        font_loaded = True
                        print(f'[INFO] Loaded Gotham font: {fname}')
                        break
        # Fallback to old location (legacy)
        if not font_loaded:
            legacy_font = os.path.join(os.path.dirname(__file__), 'gotham-regular.ttf')
            if os.path.exists(legacy_font):
                font_id = QFontDatabase.addApplicationFont(legacy_font)
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    self.setFont(QFont(families[0], 24))
                    font_loaded = True
                    print('[INFO] Loaded Gotham font from legacy location.')
        if not font_loaded:
            print('[WARNING] Failed to load Gotham font, falling back to Arial.')
            self.setFont(QFont('Arial', 24))
        # Set overlay style: white text, semi-transparent background, rounded corners, padding
        self.setStyleSheet('color: white; background: rgba(0,0,0,0.42); border-radius: 8px; padding: 10px 20px;')
        # Align text left and vertically centered
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Start hidden until triggered
        self.setVisible(False)
        # Allow mouse events to pass through overlay
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Animation for fade-in/out
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(420)  # Duration in ms for fade
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Smooth fade
        # Timer to auto-hide overlay after a duration
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)  # Only fires once per show
        self.hide_timer.timeout.connect(self.hide_with_fade)  # Connect to fade-out

    def show_title(self, file_name, duration=2300):
        """
        Extract and display a cleaned title from the given filename as an overlay.
        Optionally includes season/episode info if detected. Overlay fades in and auto-hides after `duration` ms.
        Args:
            file_name (str): The video file name (with or without path).
            duration (int): Milliseconds to display overlay before fading out.
        """
        # --- Title Extraction Logic ---
        import re
        # Remove file extension (e.g., .mkv, .mp4)
        name = re.sub(r'\.[^.]+$', '', file_name)
        # Replace dots and underscores with spaces for readability
        name = re.sub(r'[._]+', ' ', name)
        # Try to stop at first occurrence of a year (e.g., 2024, 1999)
        match_year = re.search(r'(19|20)\d{2}', name)
        cut_idx = match_year.end() if match_year else None
        # Remove known tags (quality, encoding, sources, etc.) and everything after first occurrence
        tag_regex = r'\b(1080p|720p|2160p|4k|8k|blu[- ]?ray|brrip|web[- ]?dl|webrip|hdrip|dvdrip|x264|x265|hevc|aac|ac3|mp3|h264|dsr|ds4k|ds|repack|remux|remastered|subs|dubbed|dual[- ]?audio|proper|uncut|extended|limited|hd|sd|cam|hdtv|yts|yify|rarbg|smg|ettv|etrg|evo|galaxy|mkvcage|mkvhub|sonyliv|amazon|netflix|prime|hotstar|zee5|voot|disney|apple|atv|amzn|hmax|web|tc|ts|dv|rip|hdr|uhd|sdr|avc|vc1|dts|truehd|flac|mka|mks|mkv|mp4|avi|mov|wmv|mov|mpg|mpeg|ogg|ogm|wmv|rmvb|rm|divx|xvid|fgt|rarbg|evo|yify|yts)\b'
        match_tag = re.search(tag_regex, name, re.IGNORECASE)
        if match_tag:
            cut_idx = min(cut_idx, match_tag.start()) if cut_idx else match_tag.start()
        if cut_idx:
            # If the original filename has ")" right after the year, include it
            orig = re.sub(r'\.[^.]+$', '', file_name)
            if orig[cut_idx:cut_idx+1] == ')':
                name = name[:cut_idx] + ')'
            else:
                name = name[:cut_idx]
        # Remove trailing non-word characters (punctuation, etc.)
        name = re.sub(r'[^\w\s\)]+$', '', name)
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        # Safety: If name is too short, fallback to first 2 words from original filename
        if len(name) < 4:
            name = ' '.join(file_name.replace('.', ' ').replace('_', ' ').split()[:2])
        # Convert to Title Case for display
        name = name.title()
        # Detect season/episode pattern (e.g., S01E02)
        match = re.search(r'(S\d{1,2}[\s._-]*E\d{1,2})', file_name, re.IGNORECASE)
        # --- Overlay Display Logic ---
        if match:
            # If season/episode found, append as stylized subtitle
            episode = match.group(1).replace('_', ' ').replace('.', ' ').replace('-', ' ').upper()
            title_text = f"{name.strip()}  <span style='font-size:18px; color:#ccc;'>{episode}</span>"
        else:
            title_text = name.strip()
        # Set rich text for overlay
        print(f'[DEBUG] Overlay text being set: {title_text}')
        self.setText(f"<span style='font-family: Gotham, Arial, sans-serif; font-size:24px; font-weight:500;'>{title_text}</span>")
        self.adjustSize()  # Ensure label fits text
        self.setVisible(True)
        self.raise_()  # Ensure overlay is on top
        # Netflix-style: align overlay left, near top-left of video
        parent = self.parentWidget()
        if parent:
            width = min(self.width(), parent.width() - 40)
            self.setGeometry(32, 32, width, self.height())
        print(f'[DEBUG] Overlay geometry: {self.geometry()}, parent: {self.parentWidget().geometry() if self.parentWidget() else None}')
        self.setWindowOpacity(1.0)
        # Comment out fade/auto-hide for debug
        #self.anim.stop()
        #self.anim.setStartValue(0.0)
        #self.anim.setEndValue(1.0)
        #self.anim.start()
        #self.hide_timer.start(duration)


    def hide_with_fade(self):
        """
        Fade out the overlay label and hide it after the animation completes.
        """
        self.anim.stop()
        self.anim.setStartValue(1.0)  # Start fade from visible
        self.anim.setEndValue(0.0)    # End fade at invisible
        self.anim.start()
        self.anim.finished.connect(self.hide)  # Hide widget after fade

    def resizeEvent(self, event):
        """
        Re-center the overlay label horizontally near the top of the parent video widget on resize.
        """
        # Center the label horizontally, near top (32px from top edge)
        parent = self.parentWidget()
        if parent:
            width = min(self.width(), parent.width() - 40)
            self.setGeometry((parent.width()-width)//2, 32, width, self.height())
        super().resizeEvent(event)
