from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStyle, QLabel, QSlider, QPushButton
from window_controls import ModernWindowControls
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from rounded_video_widget import RoundedVideoWidget
from overlay_title import OverlayTitleLabel
from controls import ControlsBar
from styles import MODERN_STYLESHEET

import os





class ModernVideoPlayer(QMainWindow):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._dragging = True
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_dragging'):
            self._dragging = False
        super().mouseReleaseEvent(event)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cascade Modern Video Player")
        self.setGeometry(200, 100, 980, 600)
        self.setStyleSheet(MODERN_STYLESHEET)
        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.info_overlay = None
        self.init_ui()

    def init_ui(self):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # Add modern window controls at the top
        self.windowControls = ModernWindowControls(self)
        self.windowControls.set_title("")

        self.mediaPlayer = QMediaPlayer(self)
        self.audio_output = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audio_output)
        self.videoWidget = RoundedVideoWidget(radius=28, parent=self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.overlayTitle = OverlayTitleLabel(self.videoWidget)
        self.overlayTitle.raise_()

        self.controls = ControlsBar(self.mediaPlayer, self.audio_output, self.videoWidget, self)
        self.controls.fullscreen_toggled.connect(self.toggle_fullscreen)

        mainLayout = QVBoxLayout()
        self.default_margins = (4, 4, 4, 4)
        mainLayout.setContentsMargins(*self.default_margins)
        self.mainLayout = mainLayout  # Save for later margin adjustment
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.windowControls, 0, Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.videoWidget, stretch=1)
        # Add progress bar above controls
        self.progressBar = self.controls.positionSlider
        self.progressBar.setMinimumHeight(18)
        self.progressBar.setMaximumHeight(22)
        self.progressBar.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addLayout(self.controls)
        self.widget.setLayout(mainLayout)

        # Fullscreen auto-hide timer
        from PyQt6.QtCore import QTimer
        self.autoHideTimer = QTimer(self)
        self.autoHideTimer.setInterval(3000)
        self.autoHideTimer.timeout.connect(self.hide_controls)
        self.controls.widget.installEventFilter(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Mouse tracking for video widget (fullscreen auto-hide)
        self.videoWidget.setMouseTracking(True)
        self.widget.setMouseTracking(True)
        self.controls.widget.setMouseTracking(True)
        self.setMouseTracking(True)

        self.audio_output.setVolume(0.5)

        # For ControlsBar to call overlay
        if hasattr(self, 'controlsBar'):
            self.controlsBar.parent = self
        if hasattr(self, 'controls_bar'):
            self.controls_bar.parent = self
        # For direct call from ControlsBar
        self.show_movie_info_overlay = self.show_movie_info_overlay

        # Drag & Drop
        self.setAcceptDrops(True)

    def toggle_fullscreen(self):
        from PyQt6.QtWidgets import QSizePolicy
        if self.isFullScreen():
            self.showNormal()
            self.controls.widget.show()
            self.windowControls.setVisible(True)
            self.autoHideTimer.stop()
            # Restore margins in windowed mode
            self.mainLayout.setContentsMargins(*self.default_margins)
            self.videoWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self.showFullScreen()
            self.controls.widget.show()
            self.windowControls.setVisible(False)
            self.autoHideTimer.start()
            # Remove margins in fullscreen
            self.mainLayout.setContentsMargins(0, 0, 0, 0)
            self.videoWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Always force windowControls invisible in fullscreen
        self.windowControls.setVisible(not self.isFullScreen())


    def show_controls(self):
        self.controls.widget.show()
        self.progressBar.show()
        if self.isFullScreen():
            self.windowControls.set_buttons_visible(True)
            self.windowControls.set_branding_visible(True)  # Show branding in fullscreen on mouse move
            self.autoHideTimer.start()
        else:
            self.windowControls.set_branding_visible(True)  # Show branding in windowed mode

    def hide_controls(self):
        self.controls.widget.hide()
        self.progressBar.hide()
        if self.isFullScreen():
            self.windowControls.set_buttons_visible(False)
            self.windowControls.set_branding_visible(False)  # Hide branding in fullscreen
            # self.setCursor(Qt.CursorShape.BlankCursor)  # Disabled: Always show mouse cursor in fullscreen
        else:
            self.windowControls.set_branding_visible(True)  # Show branding in windowed mode
        self.autoHideTimer.start()

    def show_movie_info_overlay(self):
        # If overlay exists, remove it
        if self.info_overlay:
            self.info_overlay.setParent(None)
            self.info_overlay.deleteLater()
            self.info_overlay = None
        # Fetch movie info in background
        def fetch_and_show():
            movie_path = self.mediaPlayer.source().toLocalFile() if hasattr(self.mediaPlayer, 'source') else None
            movie_name = os.path.basename(movie_path) if movie_path else ""
            info = self.fetch_movie_info(movie_name)
            # UI must be created in the main thread
            def show_overlay():
                self.info_overlay = BlurredOverlayWidget(self)
                card = MovieInfoCard(info, self.info_overlay)
                card.setParent(self.info_overlay)
                card.move((self.width() - card.width()) // 2, (self.height() - card.height()) // 2)
                card.show()
                self.info_overlay.setGeometry(self.rect())
                self.info_overlay.show()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, show_overlay)
            # (No direct widget creation in this thread!)
        threading.Thread(target=fetch_and_show, daemon=True).start()

    def fetch_movie_info(self, movie_name):
        # Call Tavily API for search
        tavily_url = "https://api.tavily.com/search"
        headers = {"Authorization": f"Bearer {self.tavily_api_key}"}
        params = {"query": movie_name, "max_results": 1}
        try:
            resp = requests.get(tavily_url, headers=headers, params=params, timeout=8)
            results = resp.json().get("results", [])
            if results:
                content = results[0].get("content") or results[0].get("description")
                title = results[0].get("title")
                url = results[0].get("url")
            else:
                content, title, url = "", movie_name, ""
        except Exception as e:
            content, title, url = "", movie_name, ""
        # Call Gemini API for structured info
        try:
            import google.generativeai as genai
            prompt = f"""
                Extract and present the following movie details as a strict JSON object with these fields:
                {{
                    'title': str,
                    'year': str,
                    'genres': list,
                    'cast': list,
                    'ratings': dict,
                    'plot': str,
                    'poster': str
                }}
                Use this context:
                Title: {title}\nURL: {url}\nDetails: {content}
                Return only the JSON object.
            """
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            info = json.loads(response.text)
        except Exception as e:
            info = {"title": title, "plot": content, "year": "", "genres": [], "cast": [], "ratings": {}, "poster": ""}
        return info

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                fileName = url.toLocalFile()
                self.windowControls.set_title(os.path.basename(fileName))
                self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
                self.mediaPlayer.play()
                # Show overlay title on drop
                if hasattr(self, 'overlayTitle'):
                    self.overlayTitle.show_title(os.path.basename(fileName))
                break

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if fileName:
            self.windowControls.set_title(os.path.basename(fileName))
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.play()
            # Show overlay title on open
            if hasattr(self, 'overlayTitle'):
                self.overlayTitle.show_title(os.path.basename(fileName))

    def mouseMoveEvent(self, event):
        # Show controls and restart auto-hide timer in fullscreen
        if self.isFullScreen():
            self.show_controls()
            self.windowControls.set_buttons_visible(True)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        # Show overlay title on mouse move
        if hasattr(self, 'overlayTitle') and hasattr(self, 'mediaPlayer'):
            src = self.mediaPlayer.source() if hasattr(self.mediaPlayer, 'source') else None
            if src and hasattr(src, 'toLocalFile'):
                file_name = os.path.basename(src.toLocalFile())
                self.overlayTitle.show_title(file_name)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        # Toggle play/pause if video area is clicked
        if self.childAt(event.position().toPoint()) == self.videoWidget:
            if self.mediaPlayer.playbackState() == self.mediaPlayer.PlaybackState.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Return:
            self.toggle_fullscreen()
        elif key == Qt.Key.Key_Space:
            # Space bar toggles play/pause
            if self.mediaPlayer.playbackState() == self.mediaPlayer.PlaybackState.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
            # Show overlay title on play/pause
            if hasattr(self, 'overlayTitle') and hasattr(self, 'mediaPlayer'):
                src = self.mediaPlayer.source() if hasattr(self.mediaPlayer, 'source') else None
                if src and hasattr(src, 'toLocalFile'):
                    file_name = os.path.basename(src.toLocalFile())
                    self.overlayTitle.show_title(file_name)
        elif key == Qt.Key.Key_Right:
            # Right arrow seeks forward 5 seconds
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000)
        elif key == Qt.Key.Key_Left:
            # Left arrow seeks backward 5 seconds
            self.mediaPlayer.setPosition(max(0, self.mediaPlayer.position() - 5000))
        else:
            super().keyPressEvent(event)
