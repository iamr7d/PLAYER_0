import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QPushButton, QSizePolicy, QStackedLayout
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen
import pyqtgraph as pg
from collections import deque
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

class AttentionPlotterQtGraph(QMainWindow):
    def __init__(self, max_points=300):
        super().__init__()
        self.setWindowTitle('Real-Time Attention Metrics (PyQtGraph)')
        self.setGeometry(150, 150, 1200, 900)
        self.max_points = max_points
        # Data
        self.time_data = deque(maxlen=max_points)
        self.ear_data = deque(maxlen=max_points)
        self.gaze_data = deque(maxlen=max_points)
        self.yaw_data = deque(maxlen=max_points)
        self.attention_state_data = deque(maxlen=max_points)
        self.blink_rate_data = deque(maxlen=max_points)
        self.closure_duration_data = deque(maxlen=max_points)
        self.distraction_duration_data = deque(maxlen=max_points)
        self.state_colors = {
            'Attentive': (0,255,0),
            'Distracted': (255,255,0),
            'Drowsy': (255,0,0),
            'Sleeping': (128,0,128),
            'Not Focused': (128,128,128),
            'Not Present': (0,0,0),
            'Low Light': (255,128,0)
        }
        # UI
        self.selected_metric_idx = 0  # Track selected metric index
        self._init_ui()
        # Timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(600)

    def _init_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Modern dark theme & grid card palette
        accent = '#4f8cff'
        bg_dark = '#101014'
        card_bg = '#18181c'
        fg_text = '#fff'
        font_family = 'Segoe UI, Arial, sans-serif'
        main_layout.setContentsMargins(36, 36, 36, 36)
        main_layout.setSpacing(24)
        self.setStyleSheet(f"background-color: {bg_dark}; font-family: {font_family}; color: {fg_text};")
        pg.setConfigOption('background', card_bg)
        pg.setConfigOption('foreground', fg_text)

        # Sidebar + main content horizontal layout
        main_hbox = QHBoxLayout()
        main_layout.addLayout(main_hbox)

        # Sidebar: vertical icon switcher
        sidebar = QFrame()
        sidebar.setStyleSheet("background: #18181c; border-radius: 18px; border: 1.5px solid #23232a;")
        sidebar.setFixedWidth(82)
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(28)
        sidebar_shadow.setColor(QColor(0,0,0,120))
        sidebar_shadow.setOffset(0, 8)
        sidebar.setGraphicsEffect(sidebar_shadow)
        sidebar_vbox = QVBoxLayout()
        sidebar_vbox.setSpacing(22)
        sidebar_vbox.setContentsMargins(0, 32, 0, 32)
        # Logo/avatar at top: material-style circle
        logo = QLabel()
        avatar_pix = QPixmap(48, 48)
        avatar_pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(avatar_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor('#4f8cff')))
        painter.setPen(QPen(QColor('#222'), 2))
        painter.drawEllipse(2, 2, 44, 44)
        painter.end()
        logo.setPixmap(avatar_pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_vbox.addWidget(logo)
        sidebar_vbox.addSpacing(18)
        # Metric icons
        self.metric_names = [
            'EAR (Eye Aspect Ratio)',
            'Gaze Centered (0-1)',
            'Head Yaw (deg)',
            'Blink Rate (blinks/min)',
            'Closure Duration (ms)',
            'Distraction Duration (s)'
        ]
        self.metric_attrs = [
            'ear_data',
            'gaze_data',
            'yaw_data',
            'blink_rate_data',
            'closure_duration_data',
            'distraction_duration_data'
        ]
        self.metric_colors = [accent, '#2ee7b6', '#ffe066', '#fff', '#fb42a7', '#42fb8d']
        # Use Unicode emoji as icons for cross-platform compatibility
        self.metric_emojis = ["👁️", "🎯", "🧑‍🦲", "👀", "⏲️", "⚠️"]
        self.sidebar_buttons = []
        for i, name in enumerate(self.metric_names):
            btn = QPushButton(self.metric_emojis[i])
            btn.setFont(QFont('Segoe UI Emoji', 24))
            btn.setFixedSize(56,56)
            btn.setToolTip(name)
            btn.clicked.connect(lambda _, idx=i: self._switch_metric(idx))
            # Material/minimal style: solid background, accent for active, no gradients or box-shadow
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #fff; border-radius: 14px; border: 2px solid transparent;
                }
                QPushButton:pressed {
                    background: #23232a;
                }
            """)
            self.sidebar_buttons.append(btn)
            sidebar_vbox.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        sidebar_vbox.addStretch()
        sidebar.setLayout(sidebar_vbox)
        main_hbox.addWidget(sidebar)

        # Main content vertical layout
        content_vbox = QVBoxLayout()
        main_hbox.addLayout(content_vbox)

        # Header and status pill, aligned on same row
        header_bar = QHBoxLayout()
        header_lbl = QLabel('Attention Metrics Dashboard')
        header_lbl.setStyleSheet(f"font-size: 26px; font-weight: 800; color: #fff; letter-spacing: 1.2px; margin-bottom: 0px;")
        header_bar.addWidget(header_lbl)
        header_bar.addStretch()
        self.status_pill = QLabel()
        self.status_pill.setStyleSheet(f"background: {accent}; border-radius: 18px; padding: 10px 32px; font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px;")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill_shadow = QGraphicsDropShadowEffect()
        pill_shadow.setBlurRadius(24)
        pill_shadow.setColor(QColor(0,0,0,120))
        pill_shadow.setOffset(0, 4)
        self.status_pill.setGraphicsEffect(pill_shadow)
        header_bar.addWidget(self.status_pill, alignment=Qt.AlignmentFlag.AlignRight)
        content_vbox.addLayout(header_bar)

        # Stat cards and insights in a compact row above the graph
        stats_insights_row = QHBoxLayout()
        stats_insights_row.setSpacing(12)
        # Stat cards (smaller)
        self.stat_cards = []
        stat_defs = [
            ("Current", accent),
            ("Average", "#ffe066"),
            ("Max", "#fb42a7"),
            ("Min", "#2ee7b6"),
            ("Total Blinks", accent),
            ("Total Distractions", "#ffe066")
        ]
        for i, (stat_label, color) in enumerate(stat_defs):
            card = QFrame()
            card.setStyleSheet(f"background: #23232a; border-radius: 12px; border: 1.5px solid #23232a; color: #fff; font-size: 18px; font-weight: 700; padding: 10px 8px 6px 8px;")
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0,0,0,60))
            shadow.setOffset(0, 2)
            card.setGraphicsEffect(shadow)
            vbox = QVBoxLayout()
            vbox.setSpacing(2)
            num_lbl = QLabel("-")
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_lbl.setFont(QFont(font_family, 14, QFont.Weight.Bold))
            vbox.addWidget(num_lbl)
            vbox.addWidget(QLabel(stat_label, alignment=Qt.AlignmentFlag.AlignCenter))
            card.setLayout(vbox)
            stats_insights_row.addWidget(card)
            self.stat_cards.append(num_lbl)
        # Insights (smaller, next to stat cards)
        insights_icons = ["👁️", "👀", "⚠️", "⏲️", "📊"]
        self.insights_labels = []
        for i, label in enumerate(["Current State", "Total Blinks", "Total Distractions", "Longest Closure (ms)", "Avg. Attention (%)"]):
            card = QFrame()
            card.setStyleSheet(f"background: #23232a; border-radius: 12px; border: 1.5px solid #23232a; color: #fff; font-size: 16px; font-weight: 600; padding: 8px 6px 4px 6px;")
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0,0,0,60))
            shadow.setOffset(0, 2)
            card.setGraphicsEffect(shadow)
            vbox = QVBoxLayout()
            vbox.setSpacing(2)
            icon_lbl = QLabel(insights_icons[i])
            icon_lbl.setFont(QFont('Segoe UI Emoji', 14))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            val_lbl = QLabel('-')
            val_lbl.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            vbox.addWidget(icon_lbl)
            vbox.addWidget(val_lbl)
            vbox.addWidget(QLabel(label, alignment=Qt.AlignmentFlag.AlignHCenter))
            card.setLayout(vbox)
            stats_insights_row.addWidget(card)
            self.insights_labels.append(val_lbl)
        content_vbox.addLayout(stats_insights_row)

        # Main graph card (much larger, visually dominant)
        self.card = QFrame()
        self.card.setStyleSheet(f"background: #23232a; border-radius: 22px; border: 2px solid #222;")
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(18)
        card_shadow.setColor(QColor(0,0,0,90))
        card_shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(card_shadow)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 12, 18, 12)
        card_layout.setSpacing(8)
        self.card.setLayout(card_layout)
        # Card header: title + value
        self.metric_title_lbl = QLabel(self.metric_names[0])
        self.metric_title_lbl.setStyleSheet(f"color: #fff; font-size: 26px; font-weight: 800; letter-spacing: 0.5px;")
        card_layout.addWidget(self.metric_title_lbl)
        self.metric_value_lbl = QLabel("-")
        self.metric_value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.metric_value_lbl.setStyleSheet(f"color: {accent}; font-size: 48px; font-weight: 900; padding: 0 0 0 0;")
        card_layout.addWidget(self.metric_value_lbl)
        self.underline = QFrame()
        self.underline.setFixedHeight(2)
        self.underline.setStyleSheet(f"background: {accent}; border-radius: 1px; margin-bottom: 8px;")
        card_layout.addWidget(self.underline)
        # Plot + No data message overlay
        plot_container = QStackedLayout()
        self.pw = pg.PlotWidget(title="")
        self.pw.setStyleSheet(f"background: transparent; border-radius: 8px;")
        self.pw.showGrid(x=True, y=True, alpha=0.10)
        self.pw.getAxis('bottom').setPen(pg.mkPen(color='#aaa', width=1))
        self.pw.getAxis('left').setPen(pg.mkPen(color='#aaa', width=1))
        self.pw.getAxis('bottom').setTextPen(pg.mkPen(color='#ccc', width=1))
        self.pw.getAxis('left').setTextPen(pg.mkPen(color='#ccc', width=1))
        self.pw.getAxis('bottom').setStyle(tickFont=QFont(font_family, 20))
        self.pw.getAxis('left').setStyle(tickFont=QFont(font_family, 20))
        self.curve = self.pw.plot([], [], pen=pg.mkPen(color=self.metric_colors[0], width=4, style=Qt.PenStyle.SolidLine))
        self.pw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.no_data_lbl = QLabel("No data yet")
        self.no_data_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_data_lbl.setStyleSheet("color: #888; font-size: 28px; font-weight: 600;")
        plot_container.addWidget(self.pw)
        plot_container.addWidget(self.no_data_lbl)
        card_layout.addLayout(plot_container, stretch=1)
        self.plot_container = plot_container
        content_vbox.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)

    def add_point(self, timestamp, ear, gaze_centered, yaw, attention_state, blink_rate, closure_duration, distraction_duration):
        self.time_data.append(timestamp)
        self.ear_data.append(ear)
        self.gaze_data.append(gaze_centered)
        self.yaw_data.append(yaw)
        self.attention_state_data.append(attention_state)
        self.blink_rate_data.append(blink_rate)
        self.closure_duration_data.append(closure_duration)
        self.distraction_duration_data.append(distraction_duration)

    def _switch_metric(self, idx=None):
        # idx: int or None (from sidebar button)
        if idx is not None:
            self.selected_metric_idx = idx
        self.update_plot()

    def update_plot(self):
        idx = self.selected_metric_idx
        data_attr = self.metric_attrs[idx]
        color = self.metric_colors[idx]
        t = list(self.time_data)
        y = list(getattr(self, data_attr))
        self.curve.setData(t, y)
        self.metric_title_lbl.setText(self.metric_names[idx])
        self.metric_value_lbl.setStyleSheet(f"font-size: 32px; font-weight: 900; color: {color}; margin-left: 18px;")
        if y:
            self.metric_value_lbl.setText(f"{y[-1]:.2f}")
            self.plot_container.setCurrentIndex(0)  # show plot
        else:
            self.metric_value_lbl.setText("-")
            self.plot_container.setCurrentIndex(1)  # show 'No data yet'
        self.underline.setStyleSheet(f"background: {color}; height: 4px; border-radius: 2px; margin-bottom: 6px;")
        self.curve.setPen(pg.mkPen(color=color, width=4, style=Qt.PenStyle.SolidLine))

        # --- Stat cards ---
        # Current, Average, Max, Min, Total Blinks, Total Distractions
        stat_emojis = [self.metric_emojis[idx], "📊", "🔺", "🔻", "👀", "⚠️"]
        stats = [
            y[-1] if y else '-',
            sum(y)/len(y) if y else '-',
            max(y) if y else '-',
            min(y) if y else '-',
            sum(self.blink_rate_data) if self.blink_rate_data else '-',
            sum(self.distraction_duration_data) if self.distraction_duration_data else '-',
        ]
        for i, val in enumerate(stats):
            emoji = stat_emojis[i]
            if isinstance(val, float):
                self.stat_cards[i].setText(f"{emoji}  {val:.2f}")
            elif isinstance(val, int):
                self.stat_cards[i].setText(f"{emoji}  {val}")
            else:
                self.stat_cards[i].setText(f"{emoji}  -")

        # Highlight selected sidebar button
        for i, btn in enumerate(self.sidebar_buttons):
            if i == idx:
                btn.setStyleSheet(f"background: {color}; color: #18181c; border-radius: 14px; font-weight: bold; border: 2px solid {color};")
            else:
                btn.setStyleSheet(f"background: transparent; color: #fff; border-radius: 14px; border: 2px solid transparent;")

        # --- Insights panel ---
        # Current State, Total Blinks, Total Distractions, Longest Closure, Avg. Attention (%)
        state_list = list(self.attention_state_data)
        state = state_list[-1] if state_list else '-'
        total_blinks = int(sum(self.blink_rate_data)) if self.blink_rate_data else '-'
        total_distractions = int(sum(self.distraction_duration_data)) if self.distraction_duration_data else '-'
        longest_closure = max(self.closure_duration_data) if self.closure_duration_data else '-'
        avg_attention = 100.0 * sum(1 for s in state_list if s == 'Attentive') / len(state_list) if state_list else '-'
        insights_vals = [
            state,
            total_blinks,
            total_distractions,
            f"{longest_closure:.0f}" if isinstance(longest_closure, (int, float)) else '-',
            f"{avg_attention:.1f}%" if isinstance(avg_attention, float) else '-',
        ]
        for i, val in enumerate(insights_vals):
            self.insights_labels[i].setText(str(val))
        # Update floating status pill (top right)
        if state_list:
            self.status_pill.setText(f'Current State: {state}')
            rgb = self.state_colors.get(state, (79,140,255))
            self.status_pill.setStyleSheet(f"background: rgb({rgb[0]},{rgb[1]},{rgb[2]}); border-radius: 18px; padding: 10px 32px; font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px;")

# Example usage (uncomment for standalone test):
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     plotter = AttentionPlotterQtGraph()
#     import random, time
#     t0 = time.time()
#     for i in range(100):
#         plotter.add_point(time.time()-t0, random.random(), random.random(), random.uniform(-30,30), random.choice(list(plotter.state_colors.keys())), random.randint(0,40), random.uniform(0,500), random.uniform(0,10))
#         app.processEvents()
#         time.sleep(0.1)
#     sys.exit(app.exec())
