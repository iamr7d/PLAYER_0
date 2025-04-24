MODERN_STYLESHEET = """
QMainWindow {
    background-color: #000;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}
QWidget {
    background-color: #000;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}
QVideoWidget {
    border-radius: 28px;
    border: 4px solid #1e3a7a;
    background: #000;
    padding: 0;
    margin: 0;
}
QWidget#controlsBar {
    background: transparent !important;
    border-radius: 36px;
    padding: 14px 28px;
    margin: 0 28px 26px 28px;
    box-shadow: none;
}
QWidget#controlsBar[fullscreen="true"] {
    background: transparent !important;
    opacity: 1.0;
    border-radius: 40px;
    transition: none;
}
QPushButton {
    border: none;
    border-radius: 50%;
    background: #2f343a;
    color: #f8f8f8;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    font-size: 22px;
    padding: 0;
    margin: 0 10px;
    /* Layout and alignment handled by layout manager */
}
QPushButton:hover {
    background: rgba(52, 120, 255, 0.10);
    color: #fff;
    border-radius: 50%;
}
QPushButton:pressed {
    background: rgba(52, 120, 255, 0.18);
    color: #fff;
    border-radius: 50%;
}

QPushButton#playBtn, QPushButton#openBtn, QPushButton#volumeIcon {
    background: transparent !important;
    color: white;
    border-radius: 50% !important;
    min-width: 44px;
    min-height: 44px;
    max-width: 44px;
    max-height: 44px;
    font-size: 23px;
    border: none !important;
    outline: none !important;
    padding: 0;
    /* Ensures icon is centered and not clipped */
}
QPushButton#playBtn > *:not(:only-child),
QPushButton#openBtn > *:not(:only-child),
QPushButton#volumeIcon > *:not(:only-child) {
    margin: auto;
}

QPushButton#playBtn:hover, QPushButton#openBtn:hover, QPushButton#volumeIcon:hover {
    background: rgba(52, 120, 255, 0.13) !important;
    border-radius: 50% !important;
    box-shadow: 0 0 0 2px rgba(52,120,255,0.08);
    /* Subtle circular highlight, never a rectangle */
}
QPushButton#playBtn:pressed, QPushButton#openBtn:pressed, QPushButton#volumeIcon:pressed {
    background: rgba(52, 120, 255, 0.20) !important;
    border-radius: 50% !important;
    }
QSlider#positionSlider {
    height: 14px;
    border-radius: 7px;
    background: #2f343a;
    margin: 0 16px;
    border: none;
    }
QSlider#positionSlider::groove:horizontal {
    border-radius: 4px;
    background: #2f343a;
    height: 7px;
}
QSlider#positionSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8e44ad, stop:1 #7f3ff7);
    border: none;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider#volumeSlider {
    background: #23242a;
    height: 16px;
    border-radius: 8px;
    margin: 0 36px; /* Increased length */
    min-width: 180px;
    max-width: 260px;
    border: none;
}
QSlider#volumeSlider::groove:horizontal {
    background: #23242a;
    border-radius: 7px;
    height: 8px;
    margin: 0 0;
}
QSlider#volumeSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #8f5cff);
    border-radius: 7px;
    height: 8px;
}
QSlider#volumeSlider::add-page:horizontal {
    background: #23242a;
    border-radius: 7px;
    height: 8px;
}
QSlider#volumeSlider::handle:horizontal {
    background: #4f8cff;
    border: none;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(79,140,255,0.18);
    transition: background 0.2s;
}
QSlider#volumeSlider::handle:horizontal:hover {
    background: #8f5cff;
}

QLabel#timeLabel {
    color: #e0e6f0;
    font-size: 16px;
    font-weight: 500;
    min-width: 80px;
    qproperty-alignment: AlignCenter;
    letter-spacing: 0.5px;
    margin: 0 10px;
}
"""
