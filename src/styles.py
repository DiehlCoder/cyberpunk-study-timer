"""
Cyberpunk Theme Stylesheet for FocusPulse Learning Timer.
Based on the Cyberpunk Color Palette:
- Neon Cyan (#00f0ff)
- Electric Hot Pink / Magenta (#ff007f)
- Cyber Violet (#8a2be2, #a855f7)
- Electric Ice & Sky Blue (#70f3ff, #0084ff)
- Midnight Obsidian Void (#08090f, #111222, #181932)
"""

CYBERPUNK_THEME = """
/* Global Window & Font */
QMainWindow, QDialog, QWidget#CentralWidget {
    background-color: #08090f;
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Cyberpunk Card Panels */
QFrame#CardFrame {
    background-color: #111222;
    border: 1px solid #232247;
    border-radius: 16px;
}

QFrame#HeaderFrame {
    background-color: #0c0d18;
    border-bottom: 1px solid #1f1e38;
}

/* Typography */
QLabel {
    color: #cbd5e1;
}

QLabel#HeaderTitle {
    font-size: 20px;
    font-weight: 800;
    color: #00f0ff;
    letter-spacing: 1px;
}

QLabel#SectionHeader {
    font-size: 13px;
    font-weight: 700;
    color: #ff007f;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

QLabel#StatsChip {
    background-color: #16172e;
    border: 1px solid #3b3368;
    border-radius: 12px;
    padding: 6px 14px;
    color: #00f0ff;
    font-weight: 700;
    font-size: 12px;
}

/* Primary Action Button (Rounded Solid Hot Pink/Red matching Routine text #ff007f) */
QPushButton#PrimaryBtn {
    background-color: #ff007f;
    color: #ffffff;
    font-weight: 800;
    font-size: 15px;
    border-radius: 12px;
    min-height: 44px;
    max-height: 44px;
    padding: 0px 32px;
    border: none;
    letter-spacing: 0.5px;
}

QPushButton#PrimaryBtn:hover {
    background-color: #ff2a8d;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #cc0066;
}

/* Secondary Buttons */
QPushButton#SecondaryBtn {
    background-color: #16172e;
    color: #f1f5f9;
    font-weight: 600;
    font-size: 13px;
    border-radius: 12px;
    min-height: 36px;
    padding: 6px 16px;
    border: 1px solid #312c5e;
}

QPushButton#SecondaryBtn:hover {
    background-color: #212242;
    border-color: #00f0ff;
    color: #00f0ff;
}

QPushButton#SecondaryBtn:pressed {
    background-color: #0f1020;
    border-color: #ff007f;
}

/* Preset Combo Box */
QComboBox {
    background-color: #14152a;
    color: #00f0ff;
    border: 1px solid #312c5e;
    border-radius: 10px;
    padding: 7px 14px;
    font-weight: 700;
    min-width: 170px;
}

QComboBox:hover {
    border-color: #00f0ff;
    background-color: #191a34;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #121324;
    color: #f1f5f9;
    border: 1px solid #00f0ff;
    border-radius: 8px;
    selection-background-color: #281e4a;
    selection-color: #00f0ff;
    padding: 6px;
}

/* Scroll Area for Interval Cards */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Interval Card (Custom Cyberpunk Deck Cards) */
QFrame#IntervalCard {
    background-color: #131427;
    border: 1px solid #232247;
    border-radius: 10px;
    padding: 6px;
}

QFrame#IntervalCard:hover {
    background-color: #1a1b35;
    border-color: #7928ca;
}

QFrame#IntervalCard[active="true"] {
    background-color: #1c183b;
    border: 1.5px solid #00f0ff;
}

/* Scrollbar */
QScrollBar:vertical {
    border: none;
    background: #0b0c16;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2d2654;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sliders */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #232247;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #ff007f);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #00f0ff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #ff007f;
    border-color: #ffffff;
}

/* Inputs */
QSpinBox, QLineEdit {
    background-color: #14152a;
    color: #f1f5f9;
    border: 1px solid #312c5e;
    border-radius: 8px;
    padding: 7px 10px;
    font-size: 13px;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #00f0ff;
}

/* Checkboxes */
QCheckBox {
    spacing: 10px;
    color: #cbd5e1;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #3b3368;
    background: #14152a;
}

QCheckBox::indicator:checked {
    background-color: #ff007f;
    border-color: #ff007f;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #232247;
    border-radius: 12px;
    background-color: #0e0f1e;
    padding: 10px;
}

QTabBar::tab {
    background: #131427;
    color: #8b8aa8;
    padding: 9px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    font-weight: 700;
}

QTabBar::tab:selected {
    background: #1c183b;
    color: #00f0ff;
    border-bottom: 2px solid #00f0ff;
}
"""

DARK_THEME = CYBERPUNK_THEME
