import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    """Cyberpunk settings dialog for custom MP3 alarm sounds, audio device selection,

    volume testing, and behavior preferences.
    """

    def __init__(self, config_manager, audio_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.audio = audio_manager

        self.setWindowTitle("Preferences & Audio Settings")
        self.setMinimumWidth(520)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0b14;
                color: #f1f5f9;
            }
            QGroupBox {
                border: 1px solid #28244f;
                border-radius: 12px;
                margin-top: 14px;
                padding-top: 18px;
                font-weight: 800;
                color: #00f0ff;
                font-size: 13px;
                letter-spacing: 0.5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: #0a0b14;
            }
        """)

        self._init_ui()
        self.audio.playback_state_changed.connect(self._on_playback_state_changed)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ================= 1. Alarm Sound Section =================
        sound_group = QGroupBox("Alarm Sound (Custom MP3 / WAV)")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(14)

        # Sound File Path Row
        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.path_edit = QLineEdit(self.config.get_alarm_sound_path())
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("""
            background-color: #14152a;
            color: #cbd5e1;
            border: 1px solid #312c5e;
            border-radius: 8px;
            padding: 8px;
        """)
        file_row.addWidget(self.path_edit, stretch=1)

        self.browse_btn = QPushButton("Browse MP3...")
        self.browse_btn.setObjectName("SecondaryBtn")
        self.browse_btn.clicked.connect(self._on_browse_sound)
        file_row.addWidget(self.browse_btn)

        self.default_sound_btn = QPushButton("Default Bell")
        self.default_sound_btn.setObjectName("SecondaryBtn")
        self.default_sound_btn.clicked.connect(self._on_reset_default_sound)
        file_row.addWidget(self.default_sound_btn)

        sound_layout.addLayout(file_row)

        # Audio Output Device Dropdown Row
        device_row = QHBoxLayout()
        device_row.setSpacing(10)

        dev_label = QLabel("Audio Output Device:")
        dev_label.setStyleSheet("color: #cbd5e1; font-weight: 600;")
        device_row.addWidget(dev_label)

        self.device_combo = QComboBox()
        available_devices = self.audio.get_available_devices()
        current_dev = self.audio.get_current_device_name()

        for d_name in available_devices:
            self.device_combo.addItem(d_name)

        if current_dev in available_devices:
            self.device_combo.setCurrentText(current_dev)

        self.device_combo.currentTextChanged.connect(self._on_device_changed)
        device_row.addWidget(self.device_combo, stretch=1)

        sound_layout.addLayout(device_row)

        # Volume Slider Row
        vol_row = QHBoxLayout()
        vol_row.setSpacing(12)

        vol_label = QLabel("Alarm Volume:")
        vol_label.setStyleSheet("color: #cbd5e1; font-weight: 600;")
        vol_row.addWidget(vol_label)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        current_vol = self.config.get_alarm_volume()
        self.vol_slider.setValue(current_vol)

        self.vol_val_label = QLabel(f"{current_vol}%")
        self.vol_val_label.setStyleSheet("color: #00f0ff; font-weight: 800; min-width: 44px;")
        self.vol_slider.valueChanged.connect(self._on_volume_changed)

        vol_row.addWidget(self.vol_slider, stretch=1)
        vol_row.addWidget(self.vol_val_label)

        self.test_sound_btn = QPushButton("▶ Test Sound")
        self.test_sound_btn.setObjectName("SecondaryBtn")
        self.test_sound_btn.clicked.connect(self._on_test_sound)
        vol_row.addWidget(self.test_sound_btn)

        sound_layout.addLayout(vol_row)
        main_layout.addWidget(sound_group)

        # ================= 2. Behavior & Notifications =================
        behavior_group = QGroupBox("Behavior & Notifications")
        beh_layout = QVBoxLayout(behavior_group)
        beh_layout.setSpacing(12)

        self.auto_advance_cb = QCheckBox("Auto-start next interval immediately when time is up")
        self.auto_advance_cb.setChecked(self.config.get_auto_start_next())
        beh_layout.addWidget(self.auto_advance_cb)

        self.notifications_cb = QCheckBox("Show Windows desktop notification banner when interval finishes")
        self.notifications_cb.setChecked(self.config.get_desktop_notifications())
        beh_layout.addWidget(self.notifications_cb)

        self.tray_cb = QCheckBox("Keep running in System Tray when window is closed")
        self.tray_cb.setChecked(self.config.get_minimize_to_tray())
        beh_layout.addWidget(self.tray_cb)

        main_layout.addWidget(behavior_group)

        # ================= Dialog Buttons =================
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self._on_save)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box)

    def _on_browse_sound(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Alarm Sound File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.m4a *.wma);;All Files (*.*)",
        )
        if file_path:
            self.path_edit.setText(file_path)
            self.audio.load_sound(file_path)

    def _on_reset_default_sound(self) -> None:
        self.path_edit.setText("assets/sounds/bell.wav")
        self.audio.load_sound("assets/sounds/bell.wav")

    def _on_device_changed(self, device_name: str) -> None:
        if device_name:
            self.audio.set_device_by_name(device_name)

    def _on_volume_changed(self, val: int) -> None:
        self.vol_val_label.setText(f"{val}%")
        self.audio.set_volume(val)

    def _on_test_sound(self) -> None:
        if self.audio.is_playing():
            self.audio.stop()
            self.test_sound_btn.setText("▶ Test Sound")
        else:
            self.audio.load_sound(self.path_edit.text())
            self.audio.set_volume(self.vol_slider.value())
            self.audio.play_alarm()
            self.test_sound_btn.setText("⏹ Stop")

    def _on_playback_state_changed(self, state_val: int) -> None:
        if state_val != QMediaPlayer.PlaybackState.PlayingState.value:
            self.test_sound_btn.setText("▶ Test Sound")

    def _on_save(self) -> None:
        self.audio.stop()
        self.config.set_alarm_sound_path(self.path_edit.text())
        self.config.set_alarm_volume(self.vol_slider.value())
        self.config.set_audio_device(self.device_combo.currentText())
        self.config.set_auto_start_next(self.auto_advance_cb.isChecked())
        self.config.set_desktop_notifications(self.notifications_cb.isChecked())
        self.config.set_minimize_to_tray(self.tray_cb.isChecked())
        self.accept()

    def closeEvent(self, event) -> None:
        self.audio.stop()
        super().closeEvent(event)
