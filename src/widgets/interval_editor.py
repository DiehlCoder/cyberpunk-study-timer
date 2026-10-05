from typing import Any, Dict, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class IntervalCard(QFrame):
    """An interactive Cyberpunk card representing an interval in the routine.

    Clicking selects and activates this interval in the timer.
    """

    clicked = Signal(int)
    double_clicked = Signal(int)

    def __init__(self, index: int, name: str, itype: str, mins: float, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.index = index
        self.setObjectName("IntervalCard")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._is_active = is_active
        self._itype = itype.lower()

        self._build_ui(index, name, self._itype, mins, is_active)
        self.set_active(is_active)

    def _build_ui(self, index: int, name: str, itype: str, mins: float, is_active: bool) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # 1. Step Number Badge (#1, #2...)
        self.step_label = QLabel(f"#{index + 1}")
        self.step_label.setStyleSheet("""
            color: #8b8aa8;
            font-size: 11px;
            font-weight: 800;
            background-color: #1a1b32;
            padding: 3px 6px;
            border-radius: 4px;
        """)
        layout.addWidget(self.step_label)

        # 2. Type Badge (FOCUS / BREAK)
        is_focus = (itype == "focus")
        badge_text = "FOCUS" if is_focus else "BREAK"
        badge_color = "#00f0ff" if is_focus else "#ff007f"
        badge_bg = "rgba(0, 240, 255, 0.16)" if is_focus else "rgba(255, 0, 127, 0.16)"
        badge_border = "rgba(0, 240, 255, 0.4)" if is_focus else "rgba(255, 0, 127, 0.4)"

        self.type_badge = QLabel(badge_text)
        self.type_badge.setStyleSheet(f"""
            color: {badge_color};
            background-color: {badge_bg};
            border: 1px solid {badge_border};
            border-radius: 6px;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.type_badge)

        # 3. Interval Name
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("""
            color: #ffffff;
            font-weight: 700;
            font-size: 13px;
        """)
        layout.addWidget(self.name_label, stretch=1)

        # 4. Status Indicator (▶ ACTIVE / READY)
        self.status_label = QLabel("▶ ACTIVE" if is_active else "CLICK TO JUMP")
        self.status_label.setStyleSheet(
            "color: #00f0ff; font-weight: 800; font-size: 10px; letter-spacing: 0.5px;"
            if is_active
            else "color: #555476; font-size: 10px; font-weight: 600;"
        )
        layout.addWidget(self.status_label)

        # 5. Duration Pill
        dur_str = f"{int(mins)}m" if mins.is_integer() else f"{mins:.1f}m"
        self.dur_label = QLabel(dur_str)
        self.dur_label.setStyleSheet("""
            color: #70f3ff;
            background-color: #161830;
            border: 1px solid #312c5e;
            border-radius: 6px;
            font-weight: 800;
            font-size: 12px;
            padding: 3px 8px;
        """)
        layout.addWidget(self.dur_label)

    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active
        if is_active:
            glow_color = "#00f0ff" if self._itype == "focus" else "#ff007f"
            self.setStyleSheet(f"""
                QFrame#IntervalCard {{
                    background-color: #1a1938;
                    border: 2px solid {glow_color};
                    border-radius: 10px;
                }}
            """)
            self.status_label.setText("▶ CURRENT")
            self.status_label.setStyleSheet(f"color: {glow_color}; font-weight: 800; font-size: 10px; letter-spacing: 0.5px;")
        else:
            self.setStyleSheet("""
                QFrame#IntervalCard {{
                    background-color: #121324;
                    border: 1px solid #232247;
                    border-radius: 10px;
                }}
                QFrame#IntervalCard:hover {{
                    background-color: #181935;
                    border: 1px solid #5a388a;
                }}
            """)
            self.status_label.setText("SELECT")
            self.status_label.setStyleSheet("color: #555476; font-size: 10px; font-weight: 600;")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.index)
        super().mouseDoubleClickEvent(event)


class EditIntervalDialog(QDialog):
    """Dialog to create or edit an individual interval."""

    def __init__(self, parent=None, name="Focus Session", itype="focus", minutes=40):
        super().__init__(parent)
        self.setWindowTitle("Edit Interval")
        self.setFixedWidth(360)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f101f;
                color: #f1f5f9;
            }
            QLabel {
                font-weight: 600;
                color: #cbd5e1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(18, 18, 18, 18)

        form = QFormLayout()
        form.setSpacing(14)

        self.name_input = QLineEdit(name)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Focus", "Break"])
        self.type_combo.setCurrentText("Focus" if itype.lower() == "focus" else "Break")

        self.min_spin = QSpinBox()
        self.min_spin.setRange(1, 480)
        self.min_spin.setValue(int(minutes))
        self.min_spin.setSuffix(" min")

        form.addRow("Interval Name:", self.name_input)
        form.addRow("Mode Type:", self.type_combo)
        form.addRow("Duration:", self.min_spin)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_data(self) -> Dict[str, Any]:
        return {
            "name": self.name_input.text().strip() or "Interval",
            "type": self.type_combo.currentText().lower(),
            "duration_minutes": self.min_spin.value(),
        }


class IntervalEditorWidget(QWidget):
    """Panel allowing users to configure, reorder, add/remove intervals,

    click any interval to jump/select, and switch presets.
    """

    intervals_updated = Signal(list)  # List[Dict[str, Any]]
    preset_switched = Signal(str)     # Preset name
    interval_selected = Signal(int)   # Index of interval clicked to jump to

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.active_index = 0
        self.selected_row = 0
        self.card_widgets: List[IntervalCard] = []

        self._init_ui()
        self.refresh_presets_dropdown()
        self.load_active_preset()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # --- Preset Selector Bar ---
        preset_bar = QHBoxLayout()
        preset_bar.setSpacing(8)

        preset_label = QLabel("Routine:")
        preset_label.setStyleSheet("color: #ff007f; font-weight: 700; font-size: 13px;")
        preset_bar.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        preset_bar.addWidget(self.preset_combo, stretch=1)

        self.save_preset_btn = QPushButton("+ Save As")
        self.save_preset_btn.setObjectName("SecondaryBtn")
        self.save_preset_btn.setToolTip("Save current interval list as a new custom preset")
        self.save_preset_btn.clicked.connect(self._on_save_as_preset)
        preset_bar.addWidget(self.save_preset_btn)

        self.del_preset_btn = QPushButton("Delete")
        self.del_preset_btn.setObjectName("SecondaryBtn")
        self.del_preset_btn.setToolTip("Delete current routine preset")
        self.del_preset_btn.clicked.connect(self._on_delete_preset)
        preset_bar.addWidget(self.del_preset_btn)

        main_layout.addLayout(preset_bar)

        # --- Scrollable Interval Cards List ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("IntervalScrollArea")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # --- Action Buttons (Add, Edit, Remove, Move Up/Down) ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.add_btn = QPushButton("+ Add Interval")
        self.add_btn.setObjectName("SecondaryBtn")
        self.add_btn.clicked.connect(self._on_add_item)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setObjectName("SecondaryBtn")
        self.edit_btn.clicked.connect(self._on_edit_selected)
        btn_layout.addWidget(self.edit_btn)

        self.del_btn = QPushButton("Remove")
        self.del_btn.setObjectName("SecondaryBtn")
        self.del_btn.clicked.connect(self._on_remove_selected)
        btn_layout.addWidget(self.del_btn)

        self.up_btn = QPushButton("▲ Up")
        self.up_btn.setObjectName("SecondaryBtn")
        self.up_btn.setToolTip("Move selected interval up")
        self.up_btn.clicked.connect(self._on_move_up)
        btn_layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("▼ Down")
        self.down_btn.setObjectName("SecondaryBtn")
        self.down_btn.setToolTip("Move selected interval down")
        self.down_btn.clicked.connect(self._on_move_down)
        btn_layout.addWidget(self.down_btn)

        main_layout.addLayout(btn_layout)

    def refresh_presets_dropdown(self) -> None:
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        presets = self.config.get_presets()
        for name in presets.keys():
            self.preset_combo.addItem(name)
        active_name = self.config.get_active_preset_name()
        if active_name in presets:
            self.preset_combo.setCurrentText(active_name)
        self.preset_combo.blockSignals(False)

    def load_active_preset(self) -> None:
        intervals = self.config.get_active_intervals()
        self.populate_list(intervals)

    def populate_list(self, intervals: List[Dict[str, Any]]) -> None:
        # Clear existing cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.card_widgets.clear()

        # Build cards
        for i, item in enumerate(intervals):
            card = IntervalCard(
                index=i,
                name=item.get("name", "Interval"),
                itype=item.get("type", "focus"),
                mins=float(item.get("duration_minutes", 25)),
                is_active=(i == self.active_index),
            )
            card.clicked.connect(self._on_card_clicked)
            card.double_clicked.connect(self._on_card_double_clicked)
            self.cards_layout.addWidget(card)
            self.card_widgets.append(card)

    def highlight_active(self, index: int) -> None:
        """Updates which card has the glowing active indicator."""
        self.active_index = index
        self.selected_row = index
        for i, card in enumerate(self.card_widgets):
            card.set_active(i == index)

    def _on_card_clicked(self, index: int) -> None:
        """When user clicks any card, select it and jump to it in the timer!"""
        self.selected_row = index
        self.highlight_active(index)
        self.interval_selected.emit(index)

    def _on_card_double_clicked(self, index: int) -> None:
        self.selected_row = index
        self._on_edit_row(index)

    def get_current_list_data(self) -> List[Dict[str, Any]]:
        name = self.preset_combo.currentText()
        presets = self.config.get_presets()
        return presets.get(name, self.config.get_active_intervals())

    def _emit_change(self, intervals: List[Dict[str, Any]]) -> None:
        active_preset = self.preset_combo.currentText()
        self.config.save_preset(active_preset, intervals)
        self.populate_list(intervals)
        self.intervals_updated.emit(intervals)

    def _on_preset_selected(self, preset_name: str) -> None:
        if not preset_name:
            return
        self.config.set_active_preset_name(preset_name)
        self.load_active_preset()
        self.preset_switched.emit(preset_name)

    def _on_save_as_preset(self) -> None:
        name, ok = QInputDialog.getText(self, "Save Preset", "Enter a name for this custom routine:")
        if ok and name.strip():
            preset_name = name.strip()
            data = self.get_current_list_data()
            self.config.save_preset(preset_name, data)
            self.refresh_presets_dropdown()
            self.preset_combo.setCurrentText(preset_name)

    def _on_delete_preset(self) -> None:
        preset_name = self.preset_combo.currentText()
        if len(self.config.get_presets()) <= 1:
            QMessageBox.warning(self, "Warning", "You must keep at least one routine preset.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete preset '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.delete_preset(preset_name)
            self.refresh_presets_dropdown()
            self.load_active_preset()

    def _on_add_item(self) -> None:
        dlg = EditIntervalDialog(self, name="Focus Session", itype="focus", minutes=40)
        if dlg.exec():
            new_item = dlg.get_data()
            intervals = list(self.get_current_list_data())
            intervals.append(new_item)
            self._emit_change(intervals)

    def _on_edit_selected(self) -> None:
        if 0 <= self.selected_row < len(self.card_widgets):
            self._on_edit_row(self.selected_row)

    def _on_edit_row(self, row: int) -> None:
        intervals = list(self.get_current_list_data())
        if not (0 <= row < len(intervals)):
            return
        data = intervals[row]
        dlg = EditIntervalDialog(
            self,
            name=data["name"],
            itype=data["type"],
            minutes=int(data["duration_minutes"]),
        )
        if dlg.exec():
            updated = dlg.get_data()
            intervals[row] = updated
            self._emit_change(intervals)

    def _on_remove_selected(self) -> None:
        intervals = list(self.get_current_list_data())
        if len(intervals) <= 1:
            QMessageBox.warning(self, "Warning", "Routine must have at least one interval.")
            return
        if 0 <= self.selected_row < len(intervals):
            intervals.pop(self.selected_row)
            self.selected_row = max(0, min(self.selected_row, len(intervals) - 1))
            self._emit_change(intervals)

    def _on_move_up(self) -> None:
        intervals = list(self.get_current_list_data())
        row = self.selected_row
        if row > 0:
            intervals[row - 1], intervals[row] = intervals[row], intervals[row - 1]
            self.selected_row = row - 1
            self._emit_change(intervals)
            self.highlight_active(self.selected_row)

    def _on_move_down(self) -> None:
        intervals = list(self.get_current_list_data())
        row = self.selected_row
        if 0 <= row < len(intervals) - 1:
            intervals[row + 1], intervals[row] = intervals[row], intervals[row + 1]
            self.selected_row = row + 1
            self._emit_change(intervals)
            self.highlight_active(self.selected_row)
