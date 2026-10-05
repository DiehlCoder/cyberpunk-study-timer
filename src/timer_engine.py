from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from PySide6.QtCore import QObject, QTimer, Signal


class TimerState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"


@dataclass
class Interval:
    name: str
    interval_type: str  # "focus" or "break"
    duration_seconds: int

    @property
    def is_focus(self) -> bool:
        return self.interval_type.lower() == "focus"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.interval_type,
            "duration_minutes": round(self.duration_seconds / 60, 2),
        }


class TimerEngine(QObject):
    """Core state machine and precision ticker for multi-interval learning timer."""

    # Signals
    tick = Signal(int, int, float)  # remaining_seconds, total_seconds, progress_ratio (0.0 to 1.0)
    state_changed = Signal(str)  # TimerState
    interval_started = Signal(int, dict)  # index, interval_dict
    interval_finished = Signal(int, dict)  # index, interval_dict
    all_completed = Signal()  # when the whole routine finishes

    def __init__(self, intervals_data: Optional[List[Dict[str, Any]]] = None, auto_advance: bool = True):
        super().__init__()
        self.auto_advance = auto_advance
        self.state = TimerState.STOPPED
        self.intervals: List[Interval] = []
        self.current_index = 0
        self.remaining_seconds = 0
        self.total_seconds = 0

        # High precision QTimer (1000ms tick)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        if intervals_data:
            self.load_intervals(intervals_data)

    def load_intervals(self, intervals_data: List[Dict[str, Any]]) -> None:
        """Loads a list of interval definitions."""
        self.stop()
        self.intervals.clear()
        for item in intervals_data:
            name = item.get("name", "Interval")
            itype = item.get("type", "focus")
            mins = float(item.get("duration_minutes", 25))
            secs = max(1, int(mins * 60))
            self.intervals.append(Interval(name=name, interval_type=itype, duration_seconds=secs))

        if not self.intervals:
            # Fallback default
            self.intervals.append(Interval("Study", "focus", 40 * 60))
            self.intervals.append(Interval("Break", "break", 10 * 60))

        self.current_index = 0
        self._setup_current_interval()

    def _setup_current_interval(self) -> None:
        if 0 <= self.current_index < len(self.intervals):
            curr = self.intervals[self.current_index]
            self.total_seconds = curr.duration_seconds
            self.remaining_seconds = curr.duration_seconds
            self._emit_tick()

    def start(self) -> None:
        if not self.intervals:
            return
        if self.state == TimerState.STOPPED:
            self.state = TimerState.RUNNING
            self._timer.start()
            self.state_changed.emit(self.state.value)
            self.interval_started.emit(self.current_index, self.current_interval.to_dict())
        elif self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._timer.start()
            self.state_changed.emit(self.state.value)

    def pause(self) -> None:
        if self.state == TimerState.RUNNING:
            self._timer.stop()
            self.state = TimerState.PAUSED
            self.state_changed.emit(self.state.value)

    def toggle(self) -> None:
        if self.state == TimerState.RUNNING:
            self.pause()
        else:
            self.start()

    def stop(self) -> None:
        self._timer.stop()
        self.state = TimerState.STOPPED
        self._setup_current_interval()
        self.state_changed.emit(self.state.value)

    def reset_current(self) -> None:
        was_running = (self.state == TimerState.RUNNING)
        self._timer.stop()
        self.state = TimerState.STOPPED
        self._setup_current_interval()
        self.state_changed.emit(self.state.value)
        if was_running:
            self.start()

    def skip_next(self) -> None:
        was_running = (self.state == TimerState.RUNNING)
        self._timer.stop()
        if self.current_index + 1 < len(self.intervals):
            self.current_index += 1
            self.state = TimerState.STOPPED
            self._setup_current_interval()
            self.state_changed.emit(self.state.value)
            if was_running or self.auto_advance:
                self.start()
        else:
            # End of queue
            self.state = TimerState.STOPPED
            self.current_index = 0
            self._setup_current_interval()
            self.state_changed.emit(self.state.value)
            self.all_completed.emit()

    def skip_prev(self) -> None:
        was_running = (self.state == TimerState.RUNNING)
        self._timer.stop()
        if self.current_index > 0:
            self.current_index -= 1
        self.state = TimerState.STOPPED
        self._setup_current_interval()
        self.state_changed.emit(self.state.value)
        if was_running:
            self.start()

    def jump_to_index(self, index: int) -> None:
        if 0 <= index < len(self.intervals):
            was_running = (self.state == TimerState.RUNNING)
            self._timer.stop()
            self.current_index = index
            self.state = TimerState.STOPPED
            self._setup_current_interval()
            self.state_changed.emit(self.state.value)
            if was_running:
                self.start()

    def _on_tick(self) -> None:
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._emit_tick()

        if self.remaining_seconds <= 0:
            self._on_interval_finished()

    def _on_interval_finished(self) -> None:
        self._timer.stop()
        finished_idx = self.current_index
        finished_interval = self.intervals[finished_idx].to_dict()

        # Emit completion signal for alarm & notifications
        self.interval_finished.emit(finished_idx, finished_interval)

        # Check if more intervals exist
        if self.current_index + 1 < len(self.intervals):
            self.current_index += 1
            self._setup_current_interval()
            if self.auto_advance:
                self.state = TimerState.RUNNING
                self._timer.start()
                self.state_changed.emit(self.state.value)
                self.interval_started.emit(self.current_index, self.current_interval.to_dict())
            else:
                self.state = TimerState.STOPPED
                self.state_changed.emit(self.state.value)
        else:
            # Entire routine finished
            self.state = TimerState.STOPPED
            self.state_changed.emit(self.state.value)
            self.all_completed.emit()
            self.current_index = 0
            self._setup_current_interval()

    def _emit_tick(self) -> None:
        if self.total_seconds > 0:
            progress = (self.total_seconds - self.remaining_seconds) / float(self.total_seconds)
        else:
            progress = 0.0
        self.tick.emit(self.remaining_seconds, self.total_seconds, progress)

    @property
    def current_interval(self) -> Interval:
        return self.intervals[self.current_index]

    @property
    def next_interval(self) -> Optional[Interval]:
        if self.current_index + 1 < len(self.intervals):
            return self.intervals[self.current_index + 1]
        return None
