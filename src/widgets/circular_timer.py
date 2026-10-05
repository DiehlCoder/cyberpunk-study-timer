import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QSizePolicy, QWidget


class CircularTimerWidget(QWidget):
    """Cyberpunk circular countdown timer with glowing neon gradients,

    high-contrast digital clock, and mode badges.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.remaining_seconds = 2400
        self.total_seconds = 2400
        self.progress_ratio = 0.0
        self.interval_name = "Deep Study 1"
        self.is_focus = True
        self.next_info = "Next: Rest Break (10m)"

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 250)

    def set_time(self, remaining_secs: int, total_secs: int, progress: float) -> None:
        self.remaining_seconds = remaining_secs
        self.total_seconds = total_secs
        self.progress_ratio = max(0.0, min(1.0, progress))
        self.update()

    def set_interval_info(self, name: str, is_focus: bool, next_label: str = "") -> None:
        self.interval_name = name
        self.is_focus = is_focus
        self.next_info = next_label
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height) - 24
        center_x = width / 2.0
        center_y = height / 2.0

        # Ring dimensions
        thickness = max(11.0, size * 0.058)
        radius = (size - thickness) / 2.0
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 1. Cyberpunk Ambient Glow (Double-pass neon aura)
        aura_color = QColor(0, 240, 255, 22) if self.is_focus else QColor(255, 0, 127, 22)
        glow_pen = QPen(aura_color, thickness * 1.8)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        # 2. Track Background (Deep Cyber Obsidian Void)
        track_pen = QPen(QColor(19, 20, 39, 220), thickness)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        # Inner subtle ring border
        inner_pen = QPen(QColor(35, 34, 71, 150), 1)
        painter.setPen(inner_pen)
        painter.drawEllipse(rect)

        # 3. Dynamic Cyberpunk Progress Arc
        if self.progress_ratio > 0.0:
            if self.is_focus:
                # Neon Cyan (#00f0ff) -> Cyber Violet (#8a2be2) -> Hot Magenta (#ff007f)
                grad_start = QColor("#00f0ff")
                grad_mid = QColor("#8a2be2")
                grad_end = QColor("#ff007f")
            else:
                # Cyber Amber (#ffe600) -> Sunset Pink (#ff007f)
                grad_start = QColor("#ffe600")
                grad_mid = QColor("#ff5252")
                grad_end = QColor("#ff007f")

            conical = QConicalGradient(center_x, center_y, -90.0)
            conical.setColorAt(0.0, grad_start)
            conical.setColorAt(min(0.99, max(0.01, self.progress_ratio * 0.5)), grad_mid)
            conical.setColorAt(max(0.01, self.progress_ratio), grad_end)
            conical.setColorAt(min(1.0, self.progress_ratio + 0.005), QColor(0, 0, 0, 0))

            arc_pen = QPen(QBrush(conical), thickness)
            arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(arc_pen)

            start_angle = 90 * 16
            span_angle = -int(self.progress_ratio * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

        # 4. Central Text Elements
        # A. Mode Pill Tag (FOCUS / BREAK)
        tag_text = "FOCUS" if self.is_focus else "BREAK"
        tag_bg = QColor(0, 240, 255, 30) if self.is_focus else QColor(255, 0, 127, 30)
        tag_border = QColor(0, 240, 255, 180) if self.is_focus else QColor(255, 0, 127, 180)
        tag_fg = QColor("#00f0ff") if self.is_focus else QColor("#ff007f")

        tag_w = size * 0.30
        tag_h = size * 0.082
        tag_rect = QRectF(center_x - tag_w / 2, center_y - size * 0.27, tag_w, tag_h)

        painter.setPen(QPen(tag_border, 1.2))
        painter.setBrush(QBrush(tag_bg))
        painter.drawRoundedRect(tag_rect, tag_h / 2, tag_h / 2)

        painter.setPen(QPen(tag_fg))
        tag_font = QFont("Segoe UI", int(max(9, size * 0.036)), QFont.Weight.Bold)
        tag_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.8)
        painter.setFont(tag_font)
        painter.drawText(tag_rect, Qt.AlignmentFlag.AlignCenter, tag_text)

        # B. Digital Time Display (MM:SS or HH:MM:SS)
        hours = self.remaining_seconds // 3600
        mins = (self.remaining_seconds % 3600) // 60
        secs = self.remaining_seconds % 60

        if hours > 0:
            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            time_font_size = int(max(22, size * 0.125))
        else:
            time_str = f"{mins:02d}:{secs:02d}"
            time_font_size = int(max(28, size * 0.165))

        time_font = QFont("Segoe UI", time_font_size, QFont.Weight.ExtraBold)
        painter.setFont(time_font)
        painter.setPen(QPen(QColor("#ffffff")))

        time_rect = QRectF(center_x - radius, center_y - size * 0.11, radius * 2, size * 0.23)
        painter.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, time_str)

        # C. Interval Name Subtitle
        sub_font = QFont("Segoe UI", int(max(10, size * 0.044)), QFont.Weight.Bold)
        painter.setFont(sub_font)
        sub_color = QColor("#70f3ff") if self.is_focus else QColor("#ff9f1c")
        painter.setPen(QPen(sub_color))
        sub_rect = QRectF(center_x - radius, center_y + size * 0.11, radius * 2, size * 0.10)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self.interval_name)

        # D. Next up footer
        if self.next_info:
            next_font = QFont("Segoe UI", int(max(9, size * 0.033)), QFont.Weight.Normal)
            painter.setFont(next_font)
            painter.setPen(QPen(QColor("#8b8aa8")))
            next_rect = QRectF(center_x - radius, center_y + size * 0.21, radius * 2, size * 0.08)
            painter.drawText(next_rect, Qt.AlignmentFlag.AlignCenter, self.next_info)

        painter.end()
