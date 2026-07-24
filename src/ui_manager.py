"""
User Interface Manager component for Voice AI Agent.
Handles visual state indicators, notifications, system tray menu, hotkeys, and history viewing.
"""

from typing import Callable, Optional, Dict, List, Any
from src.constants import SystemState
from src.theme import ThemeManager
from src.ui_components import StatusIndicatorWidget, LevelMeterWidget


class UIManager:
    """Manages application user interface state and interactions."""

    def __init__(self, theme_mode: str = "system"):
        """Initialize user interface manager."""
        self.theme_manager = ThemeManager(mode=theme_mode)
        self.status_widget = StatusIndicatorWidget(SystemState.IDLE)
        self.mic_level_widget = LevelMeterWidget(0.0)
        self.volume_level_widget = LevelMeterWidget(0.8)

        self.current_state = SystemState.IDLE
        self.current_message = ""
        self.is_message_temporary = False
        self.icon_path: Optional[str] = None

        self._hotkeys: Dict[str, Callable] = {}
        self._menu_items: List[Dict[str, Any]] = []
        self._notifications: List[Dict[str, str]] = []
        self._history: List[Dict[str, Any]] = []

    def show_state(self, state: SystemState) -> None:
        """Update visual indicator for system state.

        Args:
            state: SystemState enum value
        """
        self.current_state = state
        self.status_widget.update_state(state)

    def set_message(self, text: str, is_temporary: bool = False) -> None:
        """Display temporary or persistent message on UI.

        Args:
            text: Message string
            is_temporary: Whether message automatically clears
        """
        self.current_message = text
        self.is_message_temporary = is_temporary

    def get_user_input(self, prompt: str) -> Optional[str]:
        """Get text input from user via prompt dialog or mock interface.

        Args:
            prompt: Question or prompt label

        Returns:
            Entered string response or None if cancelled
        """
        # Return input if provided or empty
        return f"Response to {prompt}"

    def register_hotkey(self, callback: Callable, key_combo: str = "Ctrl+Space") -> None:
        """Register global hotkey for activation (e.g. Ctrl+Space for Push-To-Talk).

        Args:
            callback: Function to invoke on hotkey trigger
            key_combo: Hotkey key combination string
        """
        self._hotkeys[key_combo] = callback

    def trigger_hotkey(self, key_combo: str) -> bool:
        """Trigger a registered hotkey callback manually or programmatically.

        Args:
            key_combo: Registered key combination string

        Returns:
            True if hotkey was found and invoked
        """
        if key_combo in self._hotkeys:
            self._hotkeys[key_combo]()
            return True
        return False

    def add_menu_item(self, label: str, callback: Callable) -> None:
        """Add item to system tray context menu.

        Args:
            label: Text label for menu item
            callback: Function to execute when clicked
        """
        self._menu_items.append({"label": label, "callback": callback})

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Get registered tray menu items.

        Returns:
            List of menu item dicts
        """
        return self._menu_items.copy()

    def set_icon(self, icon_path: str) -> None:
        """Set system tray icon path.

        Args:
            icon_path: Path to icon image file
        """
        self.icon_path = icon_path

    def notify(self, title: str, message: str) -> None:
        """Show desktop notification.

        Args:
            title: Notification header string
            message: Notification body text
        """
        self._notifications.append({"title": title, "message": message})

    def get_notifications(self) -> List[Dict[str, str]]:
        """Get list of active desktop notifications."""
        return self._notifications.copy()

    def update_volume(self, volume: float) -> None:
        """Update audio output volume display (0.0-1.0).

        Args:
            volume: Float level between 0.0 and 1.0
        """
        self.volume_level_widget.set_level(volume)

    def update_microphone_level(self, level: float) -> None:
        """Show microphone input level (0.0-1.0).

        Args:
            level: Float level between 0.0 and 1.0
        """
        self.mic_level_widget.set_level(level)

    def add_history_entry(self, role: str, content: str) -> None:
        """Add transcript entry to conversation history viewer.

        Args:
            role: 'user' or 'assistant'
            content: Text message content
        """
        import time
        self._history.append({
            "timestamp": time.time(),
            "role": role,
            "content": content
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history records."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear local conversation history viewer."""
        self._history.clear()
