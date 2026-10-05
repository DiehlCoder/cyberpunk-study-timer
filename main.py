import ctypes
import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow
from src.styles import DARK_THEME


def main():
    # 1. Windows Taskbar Icon Fix
    if sys.platform == "win32":
        try:
            app_id = "kirad.focuspulse.learningtimer.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception as e:
            print(f"Could not set AppUserModelID: {e}")

    # 2. Enable High-DPI Scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 3. Create Application
    app = QApplication(sys.argv)
    app.setApplicationName("FocusPulse")
    app.setOrganizationName("LearningTimer")

    # 4. Set Application Icon (Using timer_icon.png)
    assets_dir = Path(__file__).resolve().parent / "assets"
    candidate_icons = [
        assets_dir / "timer_icon.png",
        assets_dir / "timer_icon.jpeg",
        assets_dir / "icon.png",
    ]
    for icon_path in candidate_icons:
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            break

    # 5. Apply Cyberpunk Theme Stylesheet
    app.setStyleSheet(DARK_THEME)

    # 6. Launch Main Window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
