import sys
import os
import numpy as np
import joblib
import pyqtgraph as pg

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QProgressBar,
    QMessageBox,
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


# ------------------------------------------------------------
# تحميل الموديل بشكل آمن
# ------------------------------------------------------------

MODEL_PATH = "model.pkl"

try:
    model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
except Exception as error:
    print(f"Model loading failed: {error}")
    model = None


class RiverPureExactDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "RiverPure | Smart purification for living rivers"
        )
        self.resize(1280, 950)
        self.setMinimumSize(900, 700)

        self.sensor_history = list(
            np.random.uniform(10, 30, 20)
        )

        self.current_range = "24H"
        self.alert_frames = []

        self.apply_exact_stylesheet()
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(2000)

    # ------------------------------------------------------------
    # التنسيقات
    # ------------------------------------------------------------

    def apply_exact_stylesheet(self):

        self.setStyleSheet("""
            QMainWindow {
                background-color: #E2EFEA;
            }

            QLabel {
                font-family: "Segoe UI", "Inter", sans-serif;
            }

            QFrame.white-card {
                background-color: #FFFFFF;
                border-radius: 18px;
                border: none;
            }

            QPushButton[class="nav-btn"] {
                background-color: transparent;
                color: #2D4A43;
                font-weight: 600;
                font-size: 13px;
                border: none;
                padding: 6px 12px;
            }

            QPushButton[class="nav-btn"]:hover {
                color: #0C382E;
            }

            QPushButton[class="action-pill"] {
                background-color: rgba(255, 255, 255, 0.20);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.40);
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton[class="action-pill"]:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }

            QPushButton[class="emergency-btn"] {
                background-color: #C04318;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border-radius: 12px;
                padding: 12px;
                border: none;
            }

            QPushButton[class="emergency-btn"]:hover {
                background-color: #A3340D;
            }

            QPushButton[class="range-btn"] {
                background-color: transparent;
                color: #799A90;
                border: none;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 9px;
                font-weight: bold;
            }

            QPushButton[class="range-btn"]:checked {
                background-color: #0C382E;
                color: #FFFFFF;
            }

            QPushButton[class="range-btn"]:hover {
                color: #0C382E;
            }
        """)

    # ------------------------------------------------------------
    # بناء الواجهة
    # ------------------------------------------------------------

    def init_ui(self):

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #E2EFEA;
            }
        """)

        self.setCentralWidget(scroll_area)

        main_container = QWidget()
        main_container.setStyleSheet(
            "background-color: #E2EFEA;"
        )

        scroll_area.setWidget(main_container)

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(35, 20, 35, 25)
        main_layout.setSpacing(18)

        # --------------------------------------------------------
        # 1. NAVBAR
        # --------------------------------------------------------

        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        logo_box = QHBoxLayout()

        logo_icon = QLabel("")
        logo_icon.setFixedSize(34, 34)
        logo_icon.setStyleSheet("""
            background-color: #0C382E;
            color: white;
            border-radius: 12px;
            padding: 6px;
            font-size: 14px;
        """)

        logo_text_box = QVBoxLayout()

        logo_title = QLabel("RiverPure")
        logo_title.setFont(QFont("Georgia", 16, QFont.Weight.Bold))
        logo_title.setStyleSheet("""
            color: #0C382E;
            margin: 0;
            padding: 0;
        """)

        logo_sub = QLabel(
            "Smart purification for living rivers"
        )
        logo_sub.setFont(QFont("Segoe UI", 8))
        logo_sub.setStyleSheet("""
            color: #618278;
            margin: 0;
            padding: 0;
        """)

        logo_text_box.addWidget(logo_title)
        logo_text_box.addWidget(logo_sub)

        logo_box.addWidget(logo_icon)
        logo_box.addLayout(logo_text_box)

        nav_layout.addLayout(logo_box)
        nav_layout.addStretch()

        links_box = QHBoxLayout()

        btn_quality = QPushButton("Quality")
        btn_quality.setProperty("class", "nav-btn")

        btn_process = QPushButton("Process")
        btn_process.setProperty("class", "nav-btn")

        btn_controls = QPushButton("Controls")
        btn_controls.setProperty("class", "nav-btn")

        links_box.addWidget(btn_quality)
        links_box.addWidget(btn_process)
        links_box.addWidget(btn_controls)

        nav_layout.addLayout(links_box)
        nav_layout.addStretch()

        self.status_badge = QLabel("● SYSTEM HEALTHY")
        self.status_badge.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        self.status_badge.setStyleSheet("""
            background-color: #CDE8E1;
            color: #0C382E;
            padding: 6px 14px;
            border-radius: 14px;
        """)

        nav_layout.addWidget(self.status_badge)
        main_layout.addWidget(nav_frame)

        # --------------------------------------------------------
        # 2. HERO BANNER
        # --------------------------------------------------------

        hero_card = QFrame()
        hero_card.setStyleSheet("""
            background-color: #0C382E;
            border-radius: 22px;
            padding: 26px;
        """)

        hero_layout = QHBoxLayout(hero_card)

        hero_left = QVBoxLayout()

        h_tag = QLabel("RIVERPURE CONTROL CENTER")
        h_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        h_tag.setStyleSheet("""
            color: #83B8AB;
            letter-spacing: 1.2px;
        """)

        h_title = QLabel(
            "Water that moves forward, beautifully."
        )
        h_title.setFont(QFont("Georgia", 22, QFont.Weight.Bold))
        h_title.setStyleSheet("""
            color: #FFFFFF;
            margin-top: 6px;
            margin-bottom: 6px;
        """)

        h_desc = QLabel(
            "A clear view of every purification step—designed to keep your river\n"
            "system balanced, responsive, and ready."
        )
        h_desc.setFont(QFont("Segoe UI", 9))
        h_desc.setStyleSheet("""
            color: #B5D5CD;
            line-height: 1.4;
        """)

        hero_left.addWidget(h_tag)
        hero_left.addWidget(h_title)
        hero_left.addWidget(h_desc)

        mini_card = QFrame()
        mini_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 16px 20px;
        """)

        mini_layout = QVBoxLayout(mini_card)

        m_tag_box = QHBoxLayout()

        m_tag = QLabel("LIVE QUALITY")
        m_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        m_tag.setStyleSheet("color: #618278;")

        m_icon = QLabel("🛡️")

        m_tag_box.addWidget(m_tag)
        m_tag_box.addStretch()
        m_tag_box.addWidget(m_icon)

        m_title = QLabel("Water quality is stable")
        m_title.setFont(QFont("Georgia", 13, QFont.Weight.Bold))
        m_title.setStyleSheet("""
            color: #0C382E;
            margin-top: 4px;
        """)

        m_desc = QLabel(
            "All treatment stages are flowing within their preferred\n"
            "range"
        )
        m_desc.setFont(QFont("Segoe UI", 8))
        m_desc.setStyleSheet("color: #799A90;")

        m_wave = QLabel("----------------------------------------")
        m_wave.setStyleSheet("""
            color: #2DB89B;
            font-weight: bold;
        """)

        mini_layout.addLayout(m_tag_box)
        mini_layout.addWidget(m_title)
        mini_layout.addWidget(m_desc)
        mini_layout.addWidget(m_wave)

        hero_layout.addLayout(hero_left, stretch=3)
        hero_layout.addWidget(mini_card, stretch=2)

        main_layout.addWidget(hero_card)

        # --------------------------------------------------------
        # 3. METRICS
        # --------------------------------------------------------

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(14)

        self.c_turb = self.create_exact_metric(
            "Turbidity",
            "1.8",
            "NTU",
            "Clear water",
            "+ 4.2%",
            "#1B8272"
        )

        self.c_ph = self.create_exact_metric(
            "pH Balance",
            "7.2",
            "pH",
            "Perfectly balanced",
            "- Steady",
            "#618278"
        )

        self.c_flow = self.create_exact_metric(
            "Flow Rate",
            "142",
            "L/min",
            "Slightly elevated",
            "+ 8.0%",
            "#D06338"
        )

        self.c_temp = self.create_exact_metric(
            "Water Temperature",
            "18.6",
            "°C",
            "Optimal range",
            "+ 0.4°",
            "#1B8272"
        )

        metrics_layout.addWidget(self.c_turb)
        metrics_layout.addWidget(self.c_ph)
        metrics_layout.addWidget(self.c_flow)
        metrics_layout.addWidget(self.c_temp)

        main_layout.addLayout(metrics_layout)

        # --------------------------------------------------------
        # 4. CHART AND ALERTS
        # --------------------------------------------------------

        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(16)

        chart_card = QFrame()
        chart_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 18px;
            padding: 20px;
        """)

        chart_layout = QVBoxLayout(chart_card)

        c_top = QHBoxLayout()
        c_info = QVBoxLayout()

        c_tag = QLabel("WATER QUALITY TREND")
        c_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        c_tag.setStyleSheet("color: #799A90;")

        c_title = QLabel("Clarity in motion")
        c_title.setFont(QFont("Georgia", 16, QFont.Weight.Bold))
        c_title.setStyleSheet("color: #0C382E;")

        self.c_sub = QLabel(
            "24-hour quality pattern — consistently clear"
        )
        self.c_sub.setFont(QFont("Segoe UI", 8))
        self.c_sub.setStyleSheet("color: #799A90;")

        c_info.addWidget(c_tag)
        c_info.addWidget(c_title)
        c_info.addWidget(self.c_sub)

        c_top.addLayout(c_info)
        c_top.addStretch()

        self.range_buttons = []

        for index, text in enumerate(["24H", "7D", "30D"]):
            range_button = QPushButton(text)
            range_button.setProperty("class", "range-btn")
            range_button.setCheckable(True)
            range_button.setAutoExclusive(True)
            range_button.setChecked(index == 0)
            range_button.clicked.connect(
                lambda checked, value=text:
                self.select_time_range(value)
            )

            self.range_buttons.append(range_button)

        time_btn_box = QHBoxLayout()

        for button in self.range_buttons:
            time_btn_box.addWidget(button)

        c_top.addLayout(time_btn_box)
        chart_layout.addLayout(c_top)

        pg.setConfigOptions(antialias=True)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#FFFFFF")
        self.plot_widget.showGrid(
            x=False,
            y=False,
            alpha=0
        )
        self.plot_widget.hideAxis("left")
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseEnabled(
            x=False,
            y=False
        )

        self.curve = self.plot_widget.plot(
            self.sensor_history,
            pen=pg.mkPen(
                color="#21A08B",
                width=3
            )
        )

        chart_layout.addWidget(self.plot_widget)
        middle_layout.addWidget(chart_card, stretch=3)

        # Alerts card
        alerts_card = QFrame()
        alerts_card.setStyleSheet("""
            background-color: #0C382E;
            border-radius: 18px;
            padding: 20px;
        """)

        alerts_layout = QVBoxLayout(alerts_card)

        a_tag = QLabel("LIVE ALERTS")
        a_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        a_tag.setStyleSheet("color: #83B8AB;")

        a_title = QLabel("Flow signals")
        a_title.setFont(QFont("Georgia", 16, QFont.Weight.Bold))
        a_title.setStyleSheet("""
            color: #FFFFFF;
            margin-bottom: 12px;
        """)

        alert_one = self.create_alert(
            "⚠️  Intake flow slightly elevated",
            "Monitor — Inflow"
        )

        alert_two = self.create_alert(
            "💬  Carbon filter operating normally",
            "International — Green"
        )

        alerts_layout.addWidget(a_tag)
        alerts_layout.addWidget(a_title)
        alerts_layout.addWidget(alert_one)
        alerts_layout.addWidget(alert_two)
        alerts_layout.addStretch()

        middle_layout.addWidget(alerts_card, stretch=2)
        main_layout.addLayout(middle_layout)

        # --------------------------------------------------------
        # 5. PURIFICATION ROUTE
        # --------------------------------------------------------

        route_card = QFrame()
        route_card.setStyleSheet("background-color: transparent;")

        route_layout = QVBoxLayout(route_card)

        r_head = QHBoxLayout()
        r_tag_box = QVBoxLayout()

        r_tag = QLabel("PURIFICATION ROUTE")
        r_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        r_tag.setStyleSheet("color: #799A90;")

        r_title = QLabel("One river. Six gentle steps.")
        r_title.setFont(QFont("Georgia", 15, QFont.Weight.Bold))
        r_title.setStyleSheet("color: #0C382E;")

        r_tag_box.addWidget(r_tag)
        r_tag_box.addWidget(r_title)

        r_head.addLayout(r_tag_box)
        r_head.addStretch()

        r_sub_right = QLabel(
            "Each stage is flowing normally"
        )
        r_sub_right.setFont(QFont("Segoe UI", 8))
        r_sub_right.setStyleSheet("color: #799A90;")

        r_head.addWidget(r_sub_right)
        route_layout.addLayout(r_head)

        steps_box = QHBoxLayout()
        steps_box.setSpacing(10)

        steps_data = [
            ("🌊", "River Intake", "Normal 100%", "#175E54"),
            ("🌪️", "Debris Screen", "Clean 98%", "#21A08B"),
            ("🏺", "Sand Filter", "Active 94%", "#D06338"),
            ("⚙️", "Carbon Filter", "Healthy 99%", "#2D3E4E"),
            ("✨", "UV Purification", "Active 100%", "#6A4C93"),
            ("💧", "Clean Water Outlet", "Ready 100%", "#1B8272"),
        ]

        for icon, name, status, color in steps_data:

            step_item = QVBoxLayout()
            step_item.setAlignment(Qt.AlignmentFlag.AlignCenter)

            circle = QLabel(icon)
            circle.setFixedSize(42, 42)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 21px;
                font-size: 16px;
            """)

            s_name = QLabel(name)
            s_name.setFont(
                QFont("Segoe UI", 8, QFont.Weight.Bold)
            )
            s_name.setStyleSheet("""
                color: #0C382E;
                margin-top: 6px;
            """)

            s_stat = QLabel(status)
            s_stat.setFont(QFont("Segoe UI", 7))
            s_stat.setStyleSheet("color: #799A90;")

            step_item.addWidget(
                circle,
                alignment=Qt.AlignmentFlag.AlignCenter
            )
            step_item.addWidget(
                s_name,
                alignment=Qt.AlignmentFlag.AlignCenter
            )
            step_item.addWidget(
                s_stat,
                alignment=Qt.AlignmentFlag.AlignCenter
            )

            steps_box.addLayout(step_item)

        route_layout.addLayout(steps_box)
        main_layout.addWidget(route_card)

        # --------------------------------------------------------
        # 6. SYSTEM CONTROLS
        # --------------------------------------------------------

        bottom_controls_layout = QHBoxLayout()
        bottom_controls_layout.setSpacing(16)

        ctrl_card = QFrame()
        ctrl_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 18px;
            padding: 20px;
        """)

        ctrl_lay = QVBoxLayout(ctrl_card)

        ct_tag = QLabel("SYSTEM CONTROLS")
        ct_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        ct_tag.setStyleSheet("color: #799A90;")

        ct_title = QLabel("Guide the current")
        ct_title.setFont(QFont("Georgia", 15, QFont.Weight.Bold))
        ct_title.setStyleSheet("""
            color: #0C382E;
            margin-bottom: 10px;
        """)

        ctrl_lay.addWidget(ct_tag)
        ctrl_lay.addWidget(ct_title)

        controls_list = [
            ("Intake Pump", "Running", True),
            ("Sediment Filter", "72%", False),
            ("Carbon Filter", "Enabled", True),
            ("UV Sterilizer", "Enabled", True),
        ]

        for c_name, c_val, is_switch in controls_list:

            c_row = QHBoxLayout()

            lbl_cn = QLabel(c_name)
            lbl_cn.setFont(
                QFont("Segoe UI", 9, QFont.Weight.Bold)
            )
            lbl_cn.setStyleSheet("color: #0C382E;")

            c_row.addWidget(lbl_cn)
            c_row.addStretch()

            if is_switch:

                sw_lbl = QLabel("🟢 ON")
                sw_lbl.setStyleSheet("""
                    color: #1B8272;
                    font-weight: bold;
                    font-size: 10px;
                """)

                c_row.addWidget(sw_lbl)

            else:

                pbar = QProgressBar()
                pbar.setValue(72)
                pbar.setFixedWidth(120)
                pbar.setFixedHeight(8)
                pbar.setTextVisible(False)
                pbar.setStyleSheet("""
                    QProgressBar {
                        background-color: #E2EFEA;
                        border-radius: 4px;
                    }

                    QProgressBar::chunk {
                        background-color: #0C382E;
                        border-radius: 4px;
                    }
                """)

                lbl_v = QLabel("72%")
                lbl_v.setFont(
                    QFont("Segoe UI", 8, QFont.Weight.Bold)
                )
                lbl_v.setStyleSheet("color: #618278;")

                c_row.addWidget(pbar)
                c_row.addWidget(lbl_v)

            ctrl_lay.addLayout(c_row)

        v_row = QVBoxLayout()

        lbl_vn = QLabel("Outlet Valve")
        lbl_vn.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        lbl_vn.setStyleSheet("""
            color: #0C382E;
            margin-top: 6px;
        """)

        v_btns = QHBoxLayout()

        v_open = QLabel("Open")
        v_open.setStyleSheet("""
            background-color: #D3F3EE;
            color: #0C382E;
            font-weight: bold;
            padding: 6px;
            border-radius: 8px;
            font-size: 9px;
        """)

        v_res = QLabel("Restricted")
        v_res.setStyleSheet("""
            color: #799A90;
            padding: 6px;
            font-size: 9px;
        """)

        v_cls = QLabel("Closed")
        v_cls.setStyleSheet("""
            color: #799A90;
            padding: 6px;
            font-size: 9px;
        """)

        v_btns.addWidget(v_open)
        v_btns.addWidget(v_res)
        v_btns.addWidget(v_cls)

        v_row.addWidget(lbl_vn)
        v_row.addLayout(v_btns)
        ctrl_lay.addLayout(v_row)

        bottom_controls_layout.addWidget(
            ctrl_card,
            stretch=3
        )

        safe_card = QFrame()
        safe_card.setStyleSheet("""
            background-color: #FDF0E9;
            border-radius: 18px;
            padding: 20px;
        """)

        safe_lay = QVBoxLayout(safe_card)

        s_tag = QLabel("SAFETY FIRST")
        s_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        s_tag.setStyleSheet("color: #D06338;")

        s_title = QLabel("Safe stop, when needed.")
        s_title.setFont(QFont("Georgia", 15, QFont.Weight.Bold))
        s_title.setStyleSheet("""
            color: #6A2710;
            margin-top: 4px;
        """)

        s_desc = QLabel(
            "This carefully pauses every active treatment component "
            "and closes the outlet valve."
        )
        s_desc.setFont(QFont("Segoe UI", 9))
        s_desc.setWordWrap(True)
        s_desc.setStyleSheet("""
            color: #9C5237;
            margin-bottom: 15px;
        """)

        self.btn_stop = QPushButton(
            "🛑  EMERGENCY PAUSE"
        )
        self.btn_stop.setProperty(
            "class",
            "emergency-btn"
        )
        self.btn_stop.clicked.connect(
            self.emergency_pause
        )

        safe_lay.addWidget(s_tag)
        safe_lay.addWidget(s_title)
        safe_lay.addWidget(s_desc)
        safe_lay.addWidget(self.btn_stop)
        safe_lay.addStretch()

        bottom_controls_layout.addWidget(
            safe_card,
            stretch=2
        )

        main_layout.addLayout(bottom_controls_layout)

        # --------------------------------------------------------
        # 7. ACTIVITY AND IMPACT
        # --------------------------------------------------------

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(16)

        act_card = QFrame()
        act_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 18px;
            padding: 20px;
        """)

        act_lay = QVBoxLayout(act_card)

        rec_tag = QLabel("RECENT ACTIVITY")
        rec_tag.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        rec_tag.setStyleSheet("color: #799A90;")

        rec_title = QLabel("The river remembers")
        rec_title.setFont(QFont("Georgia", 15, QFont.Weight.Bold))
        rec_title.setStyleSheet("color: #0C382E;")

        rec_sub = QLabel(
            "No saved activity yet. Your next control change "
            "will appear here."
        )
        rec_sub.setFont(QFont("Segoe UI", 8))
        rec_sub.setWordWrap(True)
        rec_sub.setStyleSheet("""
            color: #90B0A7;
            margin-top: 10px;
        """)

        act_lay.addWidget(rec_tag)
        act_lay.addWidget(rec_title)
        act_lay.addWidget(rec_sub)

        imp_card = QFrame()
        imp_card.setStyleSheet("""
            background-color: #CDE8E1;
            border-radius: 18px;
            padding: 20px;
        """)

        imp_lay = QVBoxLayout(imp_card)

        i_icon = QLabel("🍃")

        i_title = QLabel(
            "A small act for every drop."
        )
        i_title.setFont(QFont("Georgia", 14, QFont.Weight.Bold))
        i_title.setStyleSheet("color: #0C382E;")

        i_desc = QLabel(
            "RiverPure helps operators make calm, traceable "
            "decisions that protect cleaner water downstream."
        )
        i_desc.setFont(QFont("Segoe UI", 8))
        i_desc.setWordWrap(True)
        i_desc.setStyleSheet("color: #386358;")

        i_bar = QLabel(
            "Dashboard data is up to date."
        )
        i_bar.setStyleSheet("""
            background-color: #FFFFFF;
            color: #618278;
            font-size: 8px;
            padding: 6px 12px;
            border-radius: 10px;
        """)

        imp_lay.addWidget(i_icon)
        imp_lay.addWidget(i_title)
        imp_lay.addWidget(i_desc)
        imp_lay.addWidget(i_bar)

        footer_layout.addWidget(act_card, stretch=3)
        footer_layout.addWidget(imp_card, stretch=2)

        main_layout.addLayout(footer_layout)

    # ------------------------------------------------------------
    # البطاقات
    # ------------------------------------------------------------

    def create_exact_metric(
        self,
        tag_str,
        val_str,
        unit_str,
        sub_str,
        badge_str,
        badge_color
    ):

        card = QFrame()
        card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 18px;
            padding: 16px;
        """)

        layout = QVBoxLayout(card)

        top_row = QHBoxLayout()

        lbl_tag = QLabel(tag_str.upper())
        lbl_tag.setFont(
            QFont("Segoe UI", 7, QFont.Weight.Bold)
        )
        lbl_tag.setStyleSheet("color: #799A90;")

        lbl_badge = QLabel(badge_str)
        lbl_badge.setFont(
            QFont("Segoe UI", 8, QFont.Weight.Bold)
        )
        lbl_badge.setStyleSheet(
            f"color: {badge_color};"
        )

        top_row.addWidget(lbl_tag)
        top_row.addStretch()
        top_row.addWidget(lbl_badge)

        val_row = QHBoxLayout()

        lbl_val = QLabel(val_str)
        lbl_val.setFont(
            QFont("Segoe UI", 22, QFont.Weight.Bold)
        )
        lbl_val.setStyleSheet("color: #0C382E;")

        lbl_unit = QLabel(unit_str)
        lbl_unit.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        lbl_unit.setStyleSheet("""
            color: #618278;
            margin-left: 2px;
        """)

        val_row.addWidget(lbl_val)
        val_row.addWidget(lbl_unit)
        val_row.addStretch()

        lbl_sub = QLabel(sub_str)
        lbl_sub.setFont(
            QFont("Segoe UI", 8)
        )
        lbl_sub.setStyleSheet("color: #90B0A7;")

        layout.addLayout(top_row)
        layout.addLayout(val_row)
        layout.addWidget(lbl_sub)

        card.lbl_val = lbl_val
        return card

    def create_alert(self, title, subtitle):

        alert_frame = QFrame()
        alert_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                padding: 12px;
            }
        """)

        alert_layout = QVBoxLayout(alert_frame)

        alert_text = QLabel(title)
        alert_text.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        alert_text.setStyleSheet("color: #FFFFFF;")
        alert_text.setWordWrap(True)

        alert_subtitle = QLabel(subtitle)
        alert_subtitle.setFont(
            QFont("Segoe UI", 8)
        )
        alert_subtitle.setStyleSheet("color: #83B8AB;")

        buttons_layout = QHBoxLayout()

        mark_button = QPushButton("Mark as read")
        mark_button.setProperty("class", "action-pill")

        dismiss_button = QPushButton("Dismiss")
        dismiss_button.setProperty("class", "action-pill")

        buttons_layout.addWidget(mark_button)
        buttons_layout.addWidget(dismiss_button)
        buttons_layout.addStretch()

        mark_button.clicked.connect(
            lambda: self.mark_alert_read(
                alert_subtitle,
                mark_button
            )
        )

        dismiss_button.clicked.connect(
            lambda: alert_frame.hide()
        )

        alert_layout.addWidget(alert_text)
        alert_layout.addWidget(alert_subtitle)
        alert_layout.addLayout(buttons_layout)

        self.alert_frames.append(alert_frame)

        return alert_frame

    # ------------------------------------------------------------
    # التحديث الحي
    # ------------------------------------------------------------

    def update_telemetry(self):

        p_ph = round(
            np.random.uniform(6.8, 7.6),
            1
        )

        p_turbidity = round(
            np.random.uniform(1.2, 2.4),
            1
        )

        p_flow = int(
            np.random.uniform(130, 155)
        )

        self.c_ph.lbl_val.setText(
            str(p_ph)
        )

        self.c_turb.lbl_val.setText(
            str(p_turbidity)
        )

        self.c_flow.lbl_val.setText(
            str(p_flow)
        )

        self.sensor_history.append(
            np.random.uniform(15, 25)
        )

        if len(self.sensor_history) > 20:
            self.sensor_history.pop(0)

        self.curve.setData(
            self.sensor_history
        )

    # ------------------------------------------------------------
    # أزرار المدة الزمنية
    # ------------------------------------------------------------

    def select_time_range(self, selected_range):

        self.current_range = selected_range

        descriptions = {
            "24H": "24-hour quality pattern — consistently clear",
            "7D": "7-day quality pattern — stable and balanced",
            "30D": "30-day quality pattern — reliably clear",
        }

        self.c_sub.setText(
            descriptions[selected_range]
        )

        data_sizes = {
            "24H": 20,
            "7D": 28,
            "30D": 36,
        }

        size = data_sizes[selected_range]

        self.sensor_history = list(
            np.random.uniform(15, 25, size)
        )

        self.curve.setData(
            self.sensor_history
        )

    # ------------------------------------------------------------
    # التنبيهات
    # ------------------------------------------------------------

    def mark_alert_read(self, subtitle_label, button):

        subtitle_label.setText("Read")
        subtitle_label.setStyleSheet("""
            color: #83B8AB;
            font-style: italic;
        """)

        button.setText("Read")

    # ------------------------------------------------------------
    # زر الطوارئ
    # ------------------------------------------------------------

    def emergency_pause(self):

        answer = QMessageBox.question(
            self,
            "Emergency Pause",
            "Pause every active treatment component and close the outlet valve?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.status_badge.setText(
            "● SYSTEM PAUSED"
        )

        self.status_badge.setStyleSheet("""
            background-color: #F8D7C7;
            color: #8A2D0D;
            padding: 6px 14px;
            border-radius: 14px;
        """)

        self.btn_stop.setText(
            "▶  RESUME SYSTEM"
        )

        try:
            self.btn_stop.clicked.disconnect()
        except RuntimeError:
            pass

        self.btn_stop.clicked.connect(
            self.resume_system
        )

    def resume_system(self):

        self.status_badge.setText(
            "● SYSTEM HEALTHY"
        )

        self.status_badge.setStyleSheet("""
            background-color: #CDE8E1;
            color: #0C382E;
            padding: 6px 14px;
            border-radius: 14px;
        """)

        self.btn_stop.setText(
            "🛑  EMERGENCY PAUSE"
        )

        try:
            self.btn_stop.clicked.disconnect()
        except RuntimeError:
            pass

        self.btn_stop.clicked.connect(
            self.emergency_pause
        )


# ------------------------------------------------------------
# تشغيل التطبيق
# ------------------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setApplicationName("RiverPure")
    app.setStyle("Fusion")

    window = RiverPureExactDashboard()
    window.show()

    sys.exit(app.exec())