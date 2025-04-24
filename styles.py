MODERN_STYLESHEET = """
QMainWindow {
    background-color: #000;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    border-radius: 48px;
    border: 0.25px solid #4f8cff;
    
    margin: 0px;
    padding: 0px;
    
}
QWidget {
    background-color: #000;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}
QVideoWidget {
    background: #000;
    padding: 0;
    margin: 0;
}
QWidget#controlsBar {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 0 !important;
    margin: 0 0 0 0 !important;
}

QWidget#windowControlsBar {
    background: #000 !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 0 !important;
    margin: 0 0 0 0 !important;
    min-height: 24px;
    max-height: 28px;
}
QLabel#windowTitleLabel {
    font-size: 11px;
    color: #e0e6f0;
    font-weight: 500;
    padding-left: 8px;
    padding-right: 10px;
    min-width: 60px;
    max-width: 200px;
}
QPushButton#minBtn, QPushButton#maxBtn, QPushButton#closeBtn {
    border: none !important;
    background: transparent !important;
    color: #fff;
    min-width: 28px;
    min-height: 28px;
    max-width: 28px;
    max-height: 28px;
    font-size: 18px;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0.8;
}
QPushButton#minBtn:hover, QPushButton#maxBtn:hover, QPushButton#closeBtn:hover,
QPushButton#minBtn:pressed, QPushButton#maxBtn:pressed, QPushButton#closeBtn:pressed {
    background: transparent !important;
    opacity: 1;
}

QWidget#windowControlsBar {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 0 !important;
    margin: 0 0 0 0 !important;
    min-height: 44px;
    max-height: 48px;
}
QPushButton#minBtn, QPushButton#maxBtn, QPushButton#closeBtn {
    border: none;
    border-radius: 0;
    background: transparent;
    color: #fff;
    min-width: 28px;
    min-height: 28px;
    max-width: 28px;
    max-height: 28px;
    font-size: 18px;
    margin: 0 6px;
    padding: 0;
    opacity: 0.8;
    : none;
}
QPushButton#closeBtn:hover, QPushButton#minBtn:hover, QPushButton#maxBtn:hover,
QPushButton#closeBtn:pressed, QPushButton#minBtn:pressed, QPushButton#maxBtn:pressed {
    background: transparent !important;
    color: #fff;
    opacity: 1;
    border-radius: 0;
    : none;
}

    
}
QPushButton {
    border: none !important;
    background: transparent !important;
    color: #f8f8f8;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    font-size: 22px;
    padding: 0 !important;
    margin: 0 !important;
    /* Layout and alignment handled by layout manager */
}
QPushButton:hover {
    background: transparent !important;
    color: #fff;
}
QPushButton:pressed {
    background: transparent !important;
    color: #fff;
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
    /* Subtle circular highlight, never a rectangle */
}
QPushButton#playBtn:pressed, QPushButton#openBtn:pressed, QPushButton#volumeIcon:pressed {
    background: rgba(52, 120, 255, 0.20) !important;
    border-radius: 50% !important;
}
QSlider#positionSlider {
    height: 18px;
    border-radius: 0;
    background: #2f343a;
    margin: 0;
    border: none;
    }

QSlider#positionSlider::groove:horizontal {
    border-radius: 0;
    background: #2f343a;
    height: 20px;
}
QSlider#positionSlider::add-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(180,200,255,0.04), stop:1 rgba(60,80,120,0.07));
    border: none;
    : none;
    /* Ultra subtle glassy look */
}
QSlider#positionSlider::sub-page:horizontal {
    border-radius: 9px 9px 9px 9px; /* Fully rounded for played section */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(180,200,255,0.14), stop:1 rgba(60,80,120,0.18));
    height: 20px;
    border: 1.5px solid rgba(180,200,255,0.18);
    : 0 2px 8px rgba(120,160,255,0.08);
    /* Glassy, frosted look */
}
QSlider#positionSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8e44ad, stop:1 #7f3ff7);
    border: none;
    width: 18px;
    height: 18px;
    margin: -1px 0;
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
QSlider#volumeSlider::handle:horizontal {
    background: #4f8cff;
    border: none;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
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
