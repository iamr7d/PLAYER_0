from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QStyle, QWidget, QGraphicsOpacityEffect, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl, QTimer, QEasingCurve, QPropertyAnimation, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFontDatabase, QFont
from controller_icons import PLAY_ICON, PAUSE_ICON, OPEN_ICON, VOLUME_ICON, FULLSCREEN_ICON, EXIT_FULLSCREEN_ICON
from PyQt6.QtSvgWidgets import QSvgWidget
from gradient_slider import GradientSlider
from blink_counter_thread import BlinkCounterThread
import base64
import os

from PyQt6.QtCore import pyqtSignal

class ControlsBar(QHBoxLayout):
    fullscreen_toggled = pyqtSignal()

    def emit_fullscreen_toggle(self):
        self.fullscreen_toggled.emit()

    def __init__(self, mediaPlayer, audio_output, videoWidget, parent=None):
        super().__init__()
        self.setContentsMargins(24, 16, 24, 32)
        self.setSpacing(22)
        self.mediaPlayer = mediaPlayer
        self.audio_output = audio_output
        self.videoWidget = videoWidget
        self.parent = parent
        self.fullscreen = False
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setInterval(1800)  # ms
        self.auto_hide_timer.timeout.connect(self.hide_controls)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(320)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.widget = QWidget()
        self.widget.setObjectName("controlsBar")
        self.widget.setGraphicsEffect(self.opacity_effect)
        self.widget.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")
        self.blink_thread = None
        self.init_controls()

    def init_controls(self):
        # Only use the modern openBtn with PNG icon
        self.openBtn = QPushButton()
        self.openBtn.setIcon(QIcon(r"icons/open-folder.png"))
        self.openBtn.setIconSize(QSize(32, 32))
        self.openBtn.setFixedSize(40, 40)
        self.openBtn.setObjectName("openBtn")
        self.openBtn.clicked.connect(self.open_file)

        self.playBtn = QPushButton()
        self.play_icon = QIcon(r"icons/play.png")
        self.pause_icon = QIcon(r"icons/pause.png")
        self.playBtn.setIcon(self.play_icon)
        self.playBtn.setFixedSize(48, 48)
        self.playBtn.setIconSize(QSize(40, 40))
        self.playBtn.setObjectName("playBtn")
        self.playBtn.clicked.connect(self.toggle_play)

        self.positionSlider = GradientSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setObjectName("positionSlider")
        self.positionSlider.sliderMoved.connect(self.set_position)

        # --- Preview popup for progress bar hover ---
        from PyQt6.QtWidgets import QApplication
        main_window = QApplication.activeWindow()
        if main_window is None:
            print("[WARNING] QApplication.activeWindow() is None, using fallback parent for previewLabel.")
            main_window = self.parent if self.parent else self.widget
        # Removed previewLabel and percentage popup logic
        # self.positionSlider.setMouseTracking(True)

        self.timeLabel = QLabel('<span style="font-family: monospace, Gotham, GothamRegular, Arial, sans-serif; font-size:16px; color:#e0e6f0; letter-spacing: 0.5px;">00:00:00.00 <span style="color:#4f8cff; font-weight: bold; margin-left:16px;">00.00 %</span></span>')
        self.timeLabel.setObjectName("timeLabel")
        self.timeLabel.mousePressEvent = self.toggle_time_display
        self.show_remaining = False

        self.volumeSlider = GradientSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeSlider.setValue(50)
        self.volumeSlider.setMinimumHeight(12)
        self.volumeSlider.setMaximumHeight(16)
        self.volumeSlider.setMinimumWidth(200)
        self.volumeSlider.setMaximumWidth(320)
        self.volumeSlider.setStyleSheet("")  # Use QSS from styles.py
        self.volumeSlider.valueChanged.connect(self.audio_output.setVolume)
        self.volumeSlider.valueChanged.connect(self.update_volume_icon_opacity)
        # Premium gradient: blue to purple
        self.volumeSlider.set_gradient_colors([
            (0.0, '#4f8cff'),
            (1.0, '#8f5cff')
        ])
        self.volumeSlider.set_glow_color(QColor(79, 140, 255, 60))  # Soft blue glow
        self.volumeSlider.set_buffering(False)  # No buffering animation for volume

        # Blink count label
        self.blinkLabel = QLabel()
        self.blinkLabel.setText("BLINKS: 0")
        self.blinkLabel.setObjectName("blinkLabel")
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        gotham_path = os.path.join(fonts_dir, 'GothamBook.ttf')
        font_loaded = False
        if os.path.exists(gotham_path):
            font_id = QFontDatabase.addApplicationFont(gotham_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self.blinkLabel.setFont(QFont(family, 13, QFont.Weight.Normal))
                font_loaded = True
        if not font_loaded:
            self.blinkLabel.setFont(QFont("Arial", 13, QFont.Weight.Normal))
        self.blinkLabel.setStyleSheet('''
            QLabel {
                font-size: 13px;
                color: #e0e6f0;
                letter-spacing: 0.5px;
                margin-left: 8px;
                font-family: Gotham, GothamRegular, Arial, sans-serif;
                font-weight: 400;
            }
        ''')
        # Neon blink circle

        self.volumeIcon = QPushButton()
        self.volumeIcon.setIcon(QIcon(r"icons/wave-sound.png"))
        self.volumeIcon.setIconSize(QSize(32, 32))
        self.volumeIcon.setFixedSize(40, 40)
        self.volumeIcon.setObjectName("volumeIcon")
        self.volumeIcon.setEnabled(False)
        self.volumeIcon.setStyleSheet("background: transparent; border: none;")
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        self.volume_icon_opacity = QGraphicsOpacityEffect()
        self.volumeIcon.setGraphicsEffect(self.volume_icon_opacity)
        self.update_volume_icon_opacity(self.volumeSlider.value())

        from PyQt6.QtCore import pyqtSignal
        self.fullscreenBtn = QPushButton()
        self.fullscreenBtn.setIcon(QIcon(r"icons/expand.png"))
        self.fullscreenBtn.setIconSize(QSize(32, 32))
        self.fullscreenBtn.setFixedSize(40, 40)
        self.fullscreenBtn.setObjectName("fullscreenBtn")
        self.fullscreenBtn.clicked.connect(self.emit_fullscreen_toggle)
        self.fullscreenBtn.setStyleSheet("background-color: rgba(0,0,0,0); border: none; margin: 0; padding: 0;")

        # Modern minimal layout: buttons, progress, time, volume, fullscreen
        inner_layout = QHBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(18)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # Only add: [Open] [Play] [TimeLabel] [ProgressBar] [Volume] [Fullscreen]

        inner_layout.addWidget(self.openBtn, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.playBtn, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.timeLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.positionSlider, 4, Qt.AlignmentFlag.AlignVCenter)
        # Add blink circle just before blink label
        self.blinkCircle = QLabel()
        self.blinkCircle.setFixedSize(22, 22)
        self.blinkCircle.setStyleSheet('''
            QLabel {
                background: rgba(20, 20, 30, 0.62);
                border-radius: 11px;
                border: 2.5px solid #4f8cff;
            }
        ''')
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(79, 140, 255, 120))
        shadow.setOffset(0, 0)
        self.blinkCircle.setGraphicsEffect(shadow)
        self.blinkCircle.setObjectName("blinkCircle")
        inner_layout.addWidget(self.blinkCircle, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.blinkLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.volumeIcon, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.volumeSlider, 0, Qt.AlignmentFlag.AlignVCenter)
        inner_layout.addWidget(self.fullscreenBtn, 0, Qt.AlignmentFlag.AlignVCenter)
        # Connect playback state to blink counting
        self.mediaPlayer.playbackStateChanged.connect(self._on_playback_state_changed)

        self.fullscreenBtn.setIconSize(QSize(28, 28))
        self.fullscreenBtn.setFixedSize(36, 36)
        self.fullscreenBtn.setObjectName("fullscreenBtn")
        self.widget.setLayout(inner_layout)
        self.addWidget(self.widget)

        # Connections
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.playbackStateChanged.connect(self.update_play_icon)
        self.mediaPlayer.errorOccurred.connect(self.handle_error)
        self.audio_output.setVolume(0.5)

    def update_volume_icon_opacity(self, value):
        # Minimum opacity at 0 volume, max at 100
        min_opacity = 0.25
        max_opacity = 1.0
        opacity = min_opacity + (max_opacity - min_opacity) * (value / 100)
        self.volume_icon_opacity.setOpacity(opacity)

    def show_movie_info(self):
        # This method will be connected to the info button. It should trigger the overlay in the player window.
        if hasattr(self.parent, 'show_movie_info_overlay'):
            self.parent.show_movie_info_overlay()

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self.parent, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if fileName:
            # Set file name on window controls if available
            if hasattr(self.parent, 'windowControls'):
                import os
                self.parent.windowControls.set_title(os.path.basename(fileName))
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.play()

    def toggle_play(self):
        if self.mediaPlayer.playbackState() == self.mediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def update_play_icon(self, state):
        if state == self.mediaPlayer.PlaybackState.PlayingState:
            self.playBtn.setIcon(self.pause_icon)
        else:
            self.playBtn.setIcon(self.play_icon)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.positionSlider.setValue(position)
        self.update_time_label()

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)
        self.update_time_label()

    def _on_playback_state_changed(self, state):
        import os
        if not hasattr(self, '_last_blink_count'):
            self._last_blink_count = 0
        # Get movie file name (without extension)
        movie_path = None
        if hasattr(self.mediaPlayer, 'source'):
            src = self.mediaPlayer.source()
            if hasattr(src, 'toLocalFile'):
                movie_path = src.toLocalFile()
        movie_base = os.path.splitext(os.path.basename(movie_path))[0] if movie_path else "blink_log"
        if state == self.mediaPlayer.PlaybackState.PlayingState:
            if not self.blink_thread or not self.blink_thread.isRunning():
                self.blink_thread = BlinkCounterThread(log_base_name=movie_base, movie_name=movie_path if movie_path else "")
                self.blink_thread.blink_count = self._last_blink_count
                self.blink_thread.blink_count_changed.connect(self._update_and_store_blink_label)
                self.blink_thread.start()
        else:
            if self.blink_thread and self.blink_thread.isRunning():
                self.blink_thread.stop()

    def _update_and_store_blink_label(self, count):
        self._last_blink_count = count
        self.update_blink_label(count)


    def update_blink_label(self, count):
        self.blinkLabel.setText(f"BLINKS: {count}")
        # Animate blink icon: flash to bright color then return
        base_style = '''
            QLabel {
                background: rgba(20, 20, 30, 0.62);
                border-radius: 11px;
                border: 2.5px solid #4f8cff;
            }
        '''
        flash_style = '''
            QLabel {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 #b8e0ff, stop:1 #4f8cff);
                border-radius: 11px;
                border: 2.5px solid #4f8cff;
            }
        '''
        if hasattr(self, 'blinkCircle') and self.blinkCircle:
            self.blinkCircle.setStyleSheet(flash_style)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(180, lambda: self.blinkCircle.setStyleSheet(base_style))

    def update_time_label(self):
        pos_ms = self.mediaPlayer.position()
        dur_ms = self.mediaPlayer.duration()
        def format_time(ms):
            total_seconds = abs(ms) // 1000
            cs_part = round((abs(ms) % 1000) / 10)  # centiseconds, 2 digits
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}.{cs_part:02}"  # Always show centiseconds
        if getattr(self, 'show_remaining', False) and dur_ms > 0:
            time_str = format_time(pos_ms - dur_ms)
        else:
            time_str = format_time(pos_ms)
        percent = (pos_ms / dur_ms * 100) if dur_ms else 0.0
        percent_str = f"{percent:05.2f} %"
        self.timeLabel.setText(
            f'<span style="font-family: monospace, Gotham, GothamRegular, Arial, sans-serif; font-size:16px; color:#e0e6f0; letter-spacing: 0.5px;">'
            f'{time_str} <span style="color:#4f8cff; font-weight: bold; margin-left:16px;">{percent_str}</span>'
            f'</span>'
        )

    def toggle_time_display(self, event):
        self.show_remaining = not getattr(self, 'show_remaining', False)
        self.update_time_label()


    # Also set the initial label HTML in __init__ or init_controls (wherever QLabel("00:00 / 00:00") is set)


    def change_speed(self, idx):
        speed_map = {0: 0.5, 1: 1.0, 2: 1.5, 3: 2.0}
        speed = speed_map.get(idx, 1.0)
        if hasattr(self.mediaPlayer, 'setPlaybackRate'):
            self.mediaPlayer.setPlaybackRate(speed)
        print(f"[Speed] Playback speed set to {speed}x")

    def handle_error(self, error, errorString):
        self.timeLabel.setText(f"Error: {errorString}")

    def toggle_maximize(self):
        mw = self.parent.window() if self.parent else None
        if mw is not None:
            if mw.isMaximized():
                mw.showNormal()
            else:
                mw.showMaximized()

    def toggle_ai_sidebar(self):
        mw = self.parent.window() if self.parent else None
        if mw is None:
            return
        if not hasattr(self, '_aiSidebar'):
            from PyQt6.QtWidgets import QWidget
            self._aiSidebar = QWidget(mw)
            self._aiSidebar.setFixedWidth(320)
            self._aiSidebar.setStyleSheet('background: #181e26; border-left: 2px solid #222;')
            self._aiSidebar.setGeometry(mw.width()-320, 0, 320, mw.height())
            self._aiSidebar.hide()
        if self._aiSidebar.isVisible():
            self._aiSidebar.hide()
            mw.showFullScreen()
            self.set_controls_visible(True, instant=True)
            self.fullscreen = True
            self.widget.setProperty("fullscreen", True)
            self.widget.style().unpolish(self.widget)
            self.widget.style().polish(self.widget)
            self.fullscreenBtn.setIcon(self.svg_icon(EXIT_FULLSCREEN_ICON))

    def set_controls_visible(self, visible, instant=False):
        if instant:
            self.opacity_anim.stop()
            self.opacity_effect.setOpacity(1.0 if visible else 0.0)
            self.widget.setVisible(visible)
        else:
            self.opacity_anim.stop()
            self.opacity_anim.setStartValue(self.opacity_effect.opacity())
            self.opacity_anim.setEndValue(1.0 if visible else 0.0)
            self.opacity_anim.start()
            if visible:
                self.widget.setVisible(True)
            else:
                QTimer.singleShot(self.opacity_anim.duration(), lambda: self.widget.setVisible(False))

    def hide_controls(self):
        if self.fullscreen:
            self.set_controls_visible(False)

    def show_controls(self):
        self.set_controls_visible(True)
        if self.fullscreen:
            self.auto_hide_timer.start()

    def on_mouse_move(self):
        if self.fullscreen:
            self.show_controls()

    def svg_icon(self, svg_str):
        # Convert SVG string to QPixmap and then to QIcon
        try:
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtGui import QPixmap, QPainter
            import io
            svg_bytes = bytes(svg_str, encoding='utf-8')
            renderer = QSvgRenderer(svg_bytes)
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except Exception as e:
            return QIcon()
