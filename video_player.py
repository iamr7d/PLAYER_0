import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QStyle, QSizePolicy
)
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class ModernVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cascade Modern Video Player")
        self.setGeometry(200, 100, 980, 600)
        self.setStyleSheet(self.modern_stylesheet())
        self.init_ui()

    def init_ui(self):
        # Central widget
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # Video player
        self.mediaPlayer = QMediaPlayer(self)
        self.audio_output = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audio_output)
        self.videoWidget = QVideoWidget(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Controls
        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playBtn.setFixedSize(48, 48)
        self.playBtn.setObjectName("playBtn")
        self.playBtn.clicked.connect(self.toggle_play)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setObjectName("positionSlider")
        self.positionSlider.sliderMoved.connect(self.set_position)

        self.openBtn = QPushButton()
        self.openBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.openBtn.setFixedSize(40, 40)
        self.openBtn.setObjectName("openBtn")
        self.openBtn.clicked.connect(self.open_file)

        self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setFixedWidth(120)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeSlider.valueChanged.connect(self.audio_output.setVolume)

        self.fullscreenBtn = QPushButton()
        self.fullscreenBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.fullscreenBtn.setFixedSize(40, 40)
        self.fullscreenBtn.setObjectName("fullscreenBtn")
        self.fullscreenBtn.clicked.connect(self.toggle_fullscreen)

        self.timeLabel = QLabel('<span style="font-family: Gotham, GothamRegular, monospace, Arial, sans-serif; font-size:16px; color:#e0e6f0;"><b>00:00:00.00</b> / <span style="color:#b0b3ba;">00:00:00.00</span></span> <span style="font-family: Gotham, GothamRegular, monospace, Arial, sans-serif; font-size:16px; color:#4f8cff; font-weight: bold; margin-left:10px;">00.00 %</span>')
        self.timeLabel.setObjectName("timeLabel")

        # Layouts
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(20, 10, 20, 10)
        controlLayout.setSpacing(18)
        controlLayout.addWidget(self.openBtn)
        controlLayout.addWidget(self.playBtn)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.timeLabel)
        controlLayout.addWidget(self.volumeSlider)
        controlLayout.addWidget(self.fullscreenBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.videoWidget, stretch=1)
        mainLayout.addLayout(controlLayout)
        self.widget.setLayout(mainLayout)

        # Connections
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.playbackStateChanged.connect(self.update_play_icon)
        self.mediaPlayer.errorOccurred.connect(self.handle_error)
        self.audio_output.setVolume(0.5)

        # Drag & Drop
        self.setAcceptDrops(True)

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if fileName:
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.play()

    def toggle_play(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def update_play_icon(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.positionSlider.setValue(position)
        self.update_time_label()

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        pos = self.mediaPlayer.position() // 1000
        dur = self.mediaPlayer.duration() // 1000
        pos_str = f"{pos // 60:02}:{pos % 60:02}"
        dur_str = f"{dur // 60:02}:{dur % 60:02}"
        self.timeLabel.setText(f"{pos_str} / {dur_str}")

    def handle_error(self, error, errorString):
        self.timeLabel.setText(f"Error: {errorString}")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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

    def modern_stylesheet(self):
        return """
        QMainWindow {
            background-color: #17181c;
        }
        QWidget {
            background-color: transparent;
        }
        QVideoWidget {
            border-radius: 18px;
            background: #111116;
            box-shadow: 0 4px 32px rgba(0,0,0,0.25);
        }
        QPushButton {
            border: none;
            border-radius: 20px;
            background: #23242a;
            color: #f8f8f8;
            transition: background 0.2s;
        }
        QPushButton:hover {
            background: #3a3b41;
        }
        QPushButton#playBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4f8cff, stop:1 #2351a2);
            color: white;
            border-radius: 24px;
            box-shadow: 0 2px 8px rgba(79,140,255,0.25);
        }
        QPushButton#playBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2351a2, stop:1 #4f8cff);
        }
        QSlider#positionSlider {
            height: 10px;
            border-radius: 5px;
            background: #23242a;
        }
        QSlider#positionSlider::groove:horizontal {
            border-radius: 5px;
            background: #23242a;
            height: 10px;
        }
        QSlider#positionSlider::handle:horizontal {
            background: #4f8cff;
            border: none;
            width: 22px;
            height: 22px;
            margin: -6px 0;
            border-radius: 11px;
        }
        QSlider#volumeSlider {
            background: #23242a;
            height: 10px;
            border-radius: 5px;
        }
        QSlider#volumeSlider::groove:horizontal {
            background: #23242a;
            border-radius: 5px;
            height: 10px;
        }
        QSlider#volumeSlider::handle:horizontal {
            background: #4f8cff;
            border: none;
            width: 18px;
            height: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        QLabel#timeLabel {
            color: #b8b8c2;
            font-size: 16px;
            min-width: 110px;
            qproperty-alignment: AlignCenter;
        }
        """

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = ModernVideoPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
