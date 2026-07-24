"""
Reusable UI Components for Voice AI Agent.
"""

from typing import Dict, Any, Optional
from src.constants import SystemState


class StatusIndicatorWidget:
    """Widget model representing system status visual indicators."""

    STATE_LABELS = {
        SystemState.IDLE: "Voice Agent Ready",
        SystemState.LISTENING: "Listening...",
        SystemState.PROCESSING: "Thinking...",
        SystemState.SPEAKING: "Speaking...",
        SystemState.ERROR: "System Error"
    }

    def __init__(self, initial_state: SystemState = SystemState.IDLE):
        self.state = initial_state
        self.label = self.STATE_LABELS[initial_state]

    def update_state(self, new_state: SystemState) -> None:
        """Update active status indicator state.

        Args:
            new_state: SystemState enum value
        """
        self.state = new_state
        self.label = self.STATE_LABELS.get(new_state, "Unknown State")


class LevelMeterWidget:
    """Widget model representing input/output volume levels."""

    def __init__(self, initial_level: float = 0.0):
        self.level = max(0.0, min(1.0, initial_level))

    def set_level(self, level: float) -> None:
        """Update volume level meter value (0.0-1.0).

        Args:
            level: Float value between 0.0 and 1.0
        """
        self.level = max(0.0, min(1.0, level))
