"""
UI Styles and Typography Definitions for Voice AI Agent.
"""

from typing import Dict, Any
from src.theme import ThemeManager


class UIStyles:
    """Provides style definitions for UI components."""

    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def get_button_style(self) -> Dict[str, Any]:

        """Get button styling attributes."""
        colors = self.theme_manager.get_colors()
        return {
            "background": colors["accent"],
            "foreground": "#FFFFFF",
            "activebackground": colors["accent"],
            "font": ("Helvetica", 10, "bold"),
            "border": 0,
            "padx": 10,
            "pady": 5
        }

    def get_status_indicator_colors(self) -> Dict[str, str]:
        """Get state indicator colors."""
        colors = self.theme_manager.get_colors()
        return {
            "idle": colors["state_idle"],
            "listening": colors["state_listening"],
            "processing": colors["state_processing"],
            "speaking": colors["state_speaking"],
            "error": colors["state_error"]
        }
