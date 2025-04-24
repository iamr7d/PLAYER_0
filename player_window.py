from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStyle, QLabel, QSlider, QPushButton
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from rounded_video_widget import RoundedVideoWidget
from controls import ControlsBar
from styles import MODERN_STYLESHEET

import os





class ModernVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cascade Modern Video Player")
        self.setGeometry(200, 100, 980, 600)
        self.setStyleSheet(MODERN_STYLESHEET)
        self.setMouseTracking(True)
        self.info_overlay = None
        self.init_ui()

    def init_ui(self):

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.mediaPlayer = QMediaPlayer(self)
        self.audio_output = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audio_output)
        self.videoWidget = RoundedVideoWidget(radius=28, parent=self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.controls = ControlsBar(self.mediaPlayer, self.audio_output, self.videoWidget, self)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.videoWidget, stretch=1)
        # Add progress bar above controls
        self.progressBar = self.controls.positionSlider
        self.progressBar.setMinimumHeight(24)
        self.progressBar.setMaximumHeight(36)
        self.progressBar.setContentsMargins(32, 18, 32, 10)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addLayout(self.controls)
        self.widget.setLayout(mainLayout)

        # Mouse tracking for video widget (fullscreen auto-hide)
        self.videoWidget.setMouseTracking(True)
        self.widget.setMouseTracking(True)
        self.controls.widget.setMouseTracking(True)

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
                self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
                self.mediaPlayer.play()
                break

    def mouseMoveEvent(self, event):
        # Forward mouse movement to controls for auto-hide/show
        self.controls.on_mouse_move()
        super().mouseMoveEvent(event)
