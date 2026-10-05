# FocusPulse — Learning & Focus Timer GUI

A sleek, responsive, and customizable learning interval timer built with **Python** and **PySide6 (Qt 6)**.

---

## ✨ Features

- **Custom Multi-Interval Sequences**: Build any routine you like (e.g. `40 min Study` → `10 min Break` → `60 min Study` → `5 min Break`).
- **Routine Presets**: Switch instantly between pre-configured routines (*Study & Break (40/10)*, *Deep Focus (60/5)*, *Pomodoro Classic (25/5)*) or save your own custom routines with `+ Save As`.
- **Customizable MP3 / WAV Alarm Sound**: Select any custom `.mp3` or `.wav` sound file from your disk via file picker, adjust volume, and test the alarm in real time.
- **Modern Responsive Dark Theme**: Clean glassmorphism slate design with vibrant neon cyan and violet accents that scales smoothly to any window size.
- **Animated Circular Progress Ring**: A smooth visual countdown ring that shows elapsed time, interval type badge (`FOCUS` vs `BREAK`), and upcoming interval info.
- **Custom App Icon**: Modern icon with Windows Taskbar pinning support (`SetCurrentProcessExplicitAppUserModelID`).
- **System Tray & Desktop Notifications**: Minimize the app to the Windows system tray and get desktop notification alerts when an interval completes.
- **Focus Time Statistics**: Tracks total daily minutes focused and completed rounds.

---

## 🚀 Quick Setup & Run

### 1. Create and Activate Virtual Environment (.venv)

Open PowerShell in this project folder:

```powershell
# Create .venv
python -m venv .venv

# Activate .venv
.\.venv\Scripts\Activate.ps1
```

*(If PowerShell script execution is restricted on your machine, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or activate via cmd: `.\.venv\Scripts\activate.bat`)*

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the Timer

```powershell
python main.py
```

---

## 📁 Project Architecture

```text
GUI/
├── .venv/                         # Python Virtual Environment
├── requirements.txt               # PySide6 dependency
├── main.py                        # Entry point with high-DPI and Windows taskbar icon integration
├── config.json                    # Saved presets, audio preferences, and daily stats
├── README.md
│
├── assets/
│   ├── icon.png                   # High-resolution glowing app icon
│   └── sounds/
│       ├── bell.wav               # Built-in gentle default chime
│       └── generate_sound.py      # Script that generated the synthetic bell
│
└── src/
    ├── styles.py                  # Polished dark-mode QSS stylesheet
    ├── config_manager.py          # JSON config & daily statistics manager
    ├── audio_manager.py           # Native QtMultimedia (QMediaPlayer) for MP3 playback
    ├── timer_engine.py            # Precision countdown engine & state machine
    ├── main_window.py             # Main layout, controls, and system tray integration
    └── widgets/
        ├── circular_timer.py      # QPainter-rendered circular progress ring
        ├── interval_editor.py     # Interval queue editor, add/edit/reorder & preset manager
        └── settings_dialog.py     # Audio picker (MP3), volume slider, and behavior toggles
```
