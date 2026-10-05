import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "alarm_sound_path": "assets/sounds/bell.wav",
    "alarm_volume": 80,
    "auto_start_next": True,
    "desktop_notifications": True,
    "minimize_to_tray": True,
    "active_preset": "Study & Break (40 / 10)",
    "presets": {
        "Study & Break (40 / 10)": [
            {"name": "Deep Study 1", "type": "focus", "duration_minutes": 40},
            {"name": "Rest Break", "type": "break", "duration_minutes": 10},
            {"name": "Deep Study 2", "type": "focus", "duration_minutes": 40},
            {"name": "Long Rest", "type": "break", "duration_minutes": 20},
        ],
        "Deep Focus (60 / 5)": [
            {"name": "Deep Work 1", "type": "focus", "duration_minutes": 60},
            {"name": "Quick Pause", "type": "break", "duration_minutes": 5},
            {"name": "Deep Work 2", "type": "focus", "duration_minutes": 60},
            {"name": "Recovery Break", "type": "break", "duration_minutes": 15},
        ],
        "Pomodoro Classic (25 / 5)": [
            {"name": "Focus Session 1", "type": "focus", "duration_minutes": 25},
            {"name": "Short Break 1", "type": "break", "duration_minutes": 5},
            {"name": "Focus Session 2", "type": "focus", "duration_minutes": 25},
            {"name": "Short Break 2", "type": "break", "duration_minutes": 5},
            {"name": "Focus Session 3", "type": "focus", "duration_minutes": 25},
            {"name": "Short Break 3", "type": "break", "duration_minutes": 5},
            {"name": "Focus Session 4", "type": "focus", "duration_minutes": 25},
            {"name": "Long Break", "type": "break", "duration_minutes": 20},
        ],
    },
    "stats": {
        "last_date": str(date.today()),
        "today_focus_seconds": 0,
        "today_completed_sessions": 0,
        "total_focus_seconds": 0,
    },
}


class ConfigManager:
    """Manages application state persistence in config.json."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config_path = config_path
        self.data: Dict[str, Any] = self._load()
        self._check_date_reset()

    def _load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            self._save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge with defaults for any missing keys
                for key, val in DEFAULT_CONFIG.items():
                    if key not in loaded:
                        loaded[key] = val
                return loaded
        except Exception as e:
            print(f"Error loading config, resetting to default: {e}")
            return DEFAULT_CONFIG.copy()

    def _save(self, data: Dict[str, Any] | None = None) -> None:
        save_data = data if data is not None else self.data
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

    def _check_date_reset(self) -> None:
        today_str = str(date.today())
        stats = self.data.setdefault("stats", {})
        if stats.get("last_date") != today_str:
            stats["last_date"] = today_str
            stats["today_focus_seconds"] = 0
            stats["today_completed_sessions"] = 0
            self._save()

    # Preset Getters & Setters
    def get_presets(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.data.get("presets", {})

    def get_active_preset_name(self) -> str:
        return self.data.get("active_preset", "Study & Break (40 / 10)")

    def set_active_preset_name(self, name: str) -> None:
        self.data["active_preset"] = name
        self._save()

    def get_active_intervals(self) -> List[Dict[str, Any]]:
        name = self.get_active_preset_name()
        presets = self.get_presets()
        return presets.get(name, list(presets.values())[0] if presets else [])

    def save_preset(self, name: str, intervals: List[Dict[str, Any]]) -> None:
        self.data.setdefault("presets", {})[name] = intervals
        self.data["active_preset"] = name
        self._save()

    def delete_preset(self, name: str) -> bool:
        presets = self.data.get("presets", {})
        if name in presets and len(presets) > 1:
            del presets[name]
            self.data["active_preset"] = next(iter(presets.keys()))
            self._save()
            return True
        return False

    # Audio & Preference Settings
    def get_alarm_sound_path(self) -> str:
        return self.data.get("alarm_sound_path", "assets/sounds/bell.wav")

    def set_alarm_sound_path(self, path: str) -> None:
        self.data["alarm_sound_path"] = path
        self._save()

    def get_alarm_volume(self) -> int:
        return int(self.data.get("alarm_volume", 80))

    def set_alarm_volume(self, volume: int) -> None:
        self.data["alarm_volume"] = max(0, min(100, volume))
        self._save()

    def get_audio_device(self) -> str:
        return self.data.get("audio_device", "")

    def set_audio_device(self, name: str) -> None:
        self.data["audio_device"] = name
        self._save()

    def get_auto_start_next(self) -> bool:
        return bool(self.data.get("auto_start_next", True))

    def set_auto_start_next(self, val: bool) -> None:
        self.data["auto_start_next"] = val
        self._save()

    def get_desktop_notifications(self) -> bool:
        return bool(self.data.get("desktop_notifications", True))

    def set_desktop_notifications(self, val: bool) -> None:
        self.data["desktop_notifications"] = val
        self._save()

    def get_minimize_to_tray(self) -> bool:
        return bool(self.data.get("minimize_to_tray", True))

    def set_minimize_to_tray(self, val: bool) -> None:
        self.data["minimize_to_tray"] = val
        self._save()

    # Statistics Tracking
    def add_focus_time(self, seconds: int) -> None:
        stats = self.data.setdefault("stats", {})
        stats["today_focus_seconds"] = stats.get("today_focus_seconds", 0) + seconds
        stats["total_focus_seconds"] = stats.get("total_focus_seconds", 0) + seconds
        self._save()

    def increment_completed_sessions(self) -> None:
        stats = self.data.setdefault("stats", {})
        stats["today_completed_sessions"] = stats.get("today_completed_sessions", 0) + 1
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        return self.data.get("stats", {})
