import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.audio_manager import AudioManager
from src.config_manager import ConfigManager
from src.timer_engine import TimerEngine, TimerState
from src.widgets.circular_timer import CircularTimerWidget
from src.widgets.interval_editor import IntervalEditorWidget
from src.widgets.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Cyberpunk Main Window for FocusPulse Learning Timer."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusPulse — Cyberpunk Learning Timer")
        self.setMinimumSize(480, 680)
        self.resize(540, 780)

        # 1. Initialize State & Managers
        self.config = ConfigManager()
        self.audio = AudioManager(
            default_sound_path=self.config.get_alarm_sound_path(),
            volume=self.config.get_alarm_volume(),
            preferred_device=self.config.get_audio_device(),
        )
        self.engine = TimerEngine(
            intervals_data=self.config.get_active_intervals(),
            auto_advance=self.config.get_auto_start_next(),
        )

        # 2. Setup Icon & Window Assets (Using timer_icon.png)
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        candidate_icons = [
            assets_dir / "timer_icon.png",
            assets_dir / "timer_icon.jpeg",
            assets_dir / "icon.png",
        ]
        self.app_icon = QIcon()
        for p in candidate_icons:
            if p.exists():
                self.app_icon = QIcon(str(p))
                self.setWindowIcon(self.app_icon)
                break

        # 3. Build UI
        self._init_ui()

        # 4. Setup System Tray
        self._init_tray()

        # 5. Connect Engine Signals
        self._connect_signals()

        # 6. Initial UI state sync
        self._update_display_for_current_interval()
        self._update_stats_label()

    def _init_ui(self) -> None:
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(14)

        # ================= Header Bar =================
        header = QFrame()
        header.setObjectName("HeaderFrame")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 4)

        title_label = QLabel("⚡ FocusPulse")
        title_label.setObjectName("HeaderTitle")
        h_layout.addWidget(title_label)

        h_layout.addStretch()

        self.stats_chip = QLabel("⚡ 0m Focus • 0 rounds")
        self.stats_chip.setObjectName("StatsChip")
        self.stats_chip.setToolTip("Total productive focus time recorded today")
        h_layout.addWidget(self.stats_chip)

        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setObjectName("SecondaryBtn")
        self.settings_btn.setToolTip("Customize MP3 alarm sound, volume, and preferences")
        self.settings_btn.clicked.connect(self._open_settings)
        h_layout.addWidget(self.settings_btn)

        main_layout.addWidget(header)

        # ================= Central Circular Timer =================
        timer_card = QFrame()
        timer_card.setObjectName("CardFrame")
        tc_layout = QVBoxLayout(timer_card)
        tc_layout.setContentsMargins(14, 18, 14, 16)
        tc_layout.setSpacing(14)

        self.circular_timer = CircularTimerWidget()
        tc_layout.addWidget(self.circular_timer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls Row (Prev, Reset, Play/Pause, Skip)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("◀ Prev")
        self.prev_btn.setObjectName("SecondaryBtn")
        self.prev_btn.setToolTip("Go to previous interval")
        self.prev_btn.clicked.connect(self.engine.skip_prev)
        ctrl_layout.addWidget(self.prev_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("SecondaryBtn")
        self.reset_btn.setToolTip("Reset the current countdown")
        self.reset_btn.clicked.connect(self.engine.reset_current)
        ctrl_layout.addWidget(self.reset_btn)

        self.play_btn = QPushButton("Start Focus")
        self.play_btn.setObjectName("PrimaryBtn")
        self.play_btn.setMinimumWidth(180)
        self.play_btn.clicked.connect(self._on_play_clicked)
        ctrl_layout.addWidget(self.play_btn)

        self.skip_btn = QPushButton("Skip ▶")
        self.skip_btn.setObjectName("SecondaryBtn")
        self.skip_btn.setToolTip("Skip to the next interval")
        self.skip_btn.clicked.connect(self.engine.skip_next)
        ctrl_layout.addWidget(self.skip_btn)

        tc_layout.addLayout(ctrl_layout)
        main_layout.addWidget(timer_card, stretch=2)

        # ================= Bottom Tabs (Intervals Routine) =================
        self.tabs = QTabWidget()
        
        # Tab: Intervals Routine (No emoji, clean text)
        self.editor_widget = IntervalEditorWidget(self.config)
        self.editor_widget.intervals_updated.connect(self._on_intervals_edited)
        self.editor_widget.preset_switched.connect(self._on_preset_switched)
        self.editor_widget.interval_selected.connect(self._on_interval_selected_from_card)
        self.tabs.addTab(self.editor_widget, "Intervals Routine")

        main_layout.addWidget(self.tabs, stretch=2)

    def _init_tray(self) -> None:
        """Initializes the Windows system tray icon and background notification menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        self.tray_icon = QSystemTrayIcon(self.app_icon if not self.app_icon.isNull() else self.windowIcon(), self)
        
        tray_menu = QMenu()
        show_action = QAction("Show / Hide FocusPulse", self)
        show_action.triggered.connect(self._toggle_visibility)
        tray_menu.addAction(show_action)

        self.tray_toggle_action = QAction("Start / Pause", self)
        self.tray_toggle_action.triggered.connect(self.engine.toggle)
        tray_menu.addAction(self.tray_toggle_action)

        skip_action = QAction("Skip Interval", self)
        skip_action.triggered.connect(self.engine.skip_next)
        tray_menu.addAction(skip_action)

        tray_menu.addSeparator()

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _connect_signals(self) -> None:
        self.engine.tick.connect(self._on_tick)
        self.engine.state_changed.connect(self._on_state_changed)
        self.engine.interval_started.connect(self._on_interval_started)
        self.engine.interval_finished.connect(self._on_interval_finished)
        self.engine.all_completed.connect(self._on_all_completed)

    def _on_play_clicked(self) -> None:
        self.engine.toggle()

    def _on_tick(self, remaining: int, total: int, progress: float) -> None:
        self.circular_timer.set_time(remaining, total, progress)

    def _on_state_changed(self, state_str: str) -> None:
        curr = self.engine.current_interval
        action_name = "Focus" if curr.is_focus else "Break"
        if state_str == TimerState.RUNNING.value:
            self.play_btn.setText(f"Pause {action_name}")
        elif state_str == TimerState.PAUSED.value:
            self.play_btn.setText(f"Resume {action_name}")
        else:
            self.play_btn.setText(f"Start {action_name}")

    def _on_interval_started(self, index: int, interval_dict: dict) -> None:
        self._update_display_for_current_interval()
        self.editor_widget.highlight_active(index)

    def _on_interval_finished(self, index: int, interval_dict: dict) -> None:
        name = interval_dict.get("name", "Interval")
        itype = interval_dict.get("type", "focus")
        duration_mins = interval_dict.get("duration_minutes", 25)

        # 1. Update daily statistics if it was a focus session
        if itype.lower() == "focus":
            self.config.add_focus_time(int(duration_mins * 60))
            self.config.increment_completed_sessions()
            self._update_stats_label()

        # 2. Trigger Custom Alarm Sound
        self.audio.play_alarm()

        # 3. Trigger Desktop Notification
        if self.config.get_desktop_notifications() and self.tray_icon:
            if itype.lower() == "focus":
                title = "⚡ Cyberpunk Focus Finished!"
                msg = f"Routine step '{name}' completed! Jack out for a break."
            else:
                title = "⚡ Break Finished!"
                msg = f"Break is over. Jack back in for the next focus run!"

            self.tray_icon.showMessage(
                title,
                msg,
                QSystemTrayIcon.MessageIcon.Information,
                5000,
            )

    def _on_all_completed(self) -> None:
        self.audio.play_alarm()
        if self.config.get_desktop_notifications() and self.tray_icon:
            self.tray_icon.showMessage(
                "🏆 Cyber Routine Completed!",
                "All intervals in this routine are done. Clean run!",
                QSystemTrayIcon.MessageIcon.Information,
                6000,
            )
        self._update_display_for_current_interval()

    def _on_interval_selected_from_card(self, index: int) -> None:
        """User clicked directly on an interval card: switch timer to this interval!"""
        self.engine.jump_to_index(index)
        self._update_display_for_current_interval()

    def _update_display_for_current_interval(self) -> None:
        curr = self.engine.current_interval
        next_item = self.engine.next_interval
        next_label = f"Next: {next_item.name} ({int(next_item.duration_seconds/60)}m)" if next_item else "Next: Routine End"

        self.circular_timer.set_interval_info(
            name=curr.name,
            is_focus=curr.is_focus,
            next_label=next_label,
        )

        progress = 0.0
        if self.engine.total_seconds > 0:
            progress = (self.engine.total_seconds - self.engine.remaining_seconds) / float(self.engine.total_seconds)

        self._on_tick(self.engine.remaining_seconds, self.engine.total_seconds, progress)
        self.editor_widget.highlight_active(self.engine.current_index)
        self._on_state_changed(self.engine.state.value)

    def _update_stats_label(self) -> None:
        stats = self.config.get_stats()
        secs = stats.get("today_focus_seconds", 0)
        sessions = stats.get("today_completed_sessions", 0)
        mins = secs // 60
        hours = mins // 60
        rem_m = mins % 60
        if hours > 0:
            time_txt = f"{hours}h {rem_m}m"
        else:
            time_txt = f"{mins}m"
        self.stats_chip.setText(f"⚡ {time_txt} Focus • {sessions} {'round' if sessions == 1 else 'rounds'}")

    def _on_intervals_edited(self, new_intervals: list) -> None:
        self.engine.load_intervals(new_intervals)
        self._update_display_for_current_interval()

    def _on_preset_switched(self, preset_name: str) -> None:
        intervals = self.config.get_active_intervals()
        self.engine.load_intervals(intervals)
        self._update_display_for_current_interval()

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.config, self.audio, self)
        if dlg.exec():
            self.engine.auto_advance = self.config.get_auto_start_next()

    def _toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_visibility()

    def _quit_application(self) -> None:
        self.audio.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.config.get_minimize_to_tray() and self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "FocusPulse is still running",
                "Timer continues in the system tray. Click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            self._quit_application()
            event.accept()
