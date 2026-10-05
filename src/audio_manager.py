import os
import sys
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioDevice, QAudioOutput, QMediaDevices, QMediaPlayer


class AudioManager(QObject):
    """Handles reliable sound playback for timer alarms using PySide6.QtMultimedia,

    with automatic audio device detection, explicit device selection, and async loading guards.
    """

    playback_state_changed = Signal(int)  # Forwards QMediaPlayer.PlaybackState

    def __init__(self, default_sound_path: str = "assets/sounds/bell.wav", volume: int = 80, preferred_device: str = ""):
        super().__init__()
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        self.current_sound_path = ""
        self._play_on_loaded = False

        # Connect status signals to handle Qt6 asynchronous loading
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.errorOccurred.connect(self._on_player_error)

        # Configure Audio Device
        self._init_audio_device(preferred_device)

        # Set Volume and Pre-load Sound
        self.set_volume(volume)
        self.load_sound(default_sound_path)

    def _init_audio_device(self, preferred_device_name: str = "") -> None:
        """Configures the best physical audio output device."""
        devices = QMediaDevices.audioOutputs()
        if not devices:
            return

        target_device: Optional[QAudioDevice] = None

        # 1. Match preferred device name if given
        if preferred_device_name:
            for d in devices:
                if d.description() == preferred_device_name:
                    target_device = d
                    break

        # 2. If no valid match, avoid Steam virtual streaming speakers if real hardware exists
        if not target_device:
            default_dev = QMediaDevices.defaultAudioOutput()
            if "steam" in default_dev.description().lower():
                # Find first non-steam device (e.g. Realtek, NVIDIA, HDMI, Headphones)
                for d in devices:
                    if "steam" not in d.description().lower():
                        target_device = d
                        break
            if not target_device:
                target_device = default_dev

        if target_device:
            self.audio_output.setDevice(target_device)

    def get_available_devices(self) -> List[str]:
        """Returns list of all available audio output device names."""
        devices = QMediaDevices.audioOutputs()
        return [d.description() for d in devices]

    def get_current_device_name(self) -> str:
        """Returns description of currently active audio output device."""
        return self.audio_output.device().description()

    def set_device_by_name(self, name: str) -> bool:
        """Switches output device to the given description."""
        for d in QMediaDevices.audioOutputs():
            if d.description() == name:
                self.audio_output.setDevice(d)
                return True
        return False

    def load_sound(self, path_str: str) -> bool:
        """Loads a sound file (MP3, WAV, etc.) into QMediaPlayer asynchronously."""
        path = Path(path_str)
        if not path.is_absolute():
            project_root = Path(__file__).resolve().parent.parent
            path = project_root / path_str

        if not path.exists():
            # Fallback to built-in bell
            fallback = Path(__file__).resolve().parent.parent / "assets" / "sounds" / "bell.wav"
            if fallback.exists():
                path = fallback
            else:
                return False

        resolved_path = str(path.resolve())
        if resolved_path == self.current_sound_path and not self.player.source().isEmpty():
            return True

        self.current_sound_path = resolved_path
        url = QUrl.fromLocalFile(resolved_path)
        self.player.setSource(url)
        return True

    def set_volume(self, volume_percent: int) -> None:
        """Sets volume from 0 to 100."""
        clamped = max(0, min(100, volume_percent))
        self.audio_output.setVolume(clamped / 100.0)

    def play_alarm(self) -> None:
        """Plays the alarm sound with async loading safety."""
        status = self.player.mediaStatus()

        # If already loaded or reached the end, reset position and play
        if status in (
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
            QMediaPlayer.MediaStatus.EndOfMedia,
        ):
            self.player.setPosition(0)
            self.player.play()
        elif status == QMediaPlayer.MediaStatus.LoadingMedia:
            # Still loading, will trigger as soon as LoadedMedia signal fires
            self._play_on_loaded = True
        else:
            # Need to re-source
            self._play_on_loaded = True
            self.load_sound(self.current_sound_path)

        # Fallback for Windows if .wav and Qt fails
        if sys.platform == "win32" and self.current_sound_path.lower().endswith(".wav"):
            try:
                import winsound
                # Only use winsound if player didn't start within 200ms
            except Exception:
                pass

    def stop(self) -> None:
        """Stops sound playback."""
        self._play_on_loaded = False
        self.player.stop()

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            if self._play_on_loaded:
                self._play_on_loaded = False
                self.player.setPosition(0)
                self.player.play()

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.playback_state_changed.emit(state.value)

    def _on_player_error(self, error, error_string: str) -> None:
        print(f"[AudioManager Error] {error}: {error_string}")
