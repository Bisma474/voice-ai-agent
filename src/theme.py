"""
Theme Manager component for Voice AI Agent UI.
Handles dark/light mode switching and color palettes.
"""

from typing import Dict, Any


class ThemeManager:
    """Manages application visual themes (light/dark/system)."""

    LIGHT_THEME = {
        "bg": "#FFFFFF",
        "fg": "#1F2937",
        "accent": "#3B82F6",
        "panel_bg": "#F3F4F6",
        "border": "#E5E7EB",
        "state_idle": "#6B7280",
        "state_listening": "#10B981",
        "state_processing": "#3B82F6",
        "state_speaking": "#8B5CF6",
        "state_error": "#EF4444",
        "text_secondary": "#4B5563"
    }

    DARK_THEME = {
        "bg": "#111827",
        "fg": "#F9FAFB",
        "accent": "#60A5FA",
        "panel_bg": "#1F2937",
        "border": "#374151",
        "state_idle": "#9CA3AF",
        "state_listening": "#34D399",
        "state_processing": "#60A5FA",
        "state_speaking": "#A78BFA",
        "state_error": "#F87171",
        "text_secondary": "#D1D5DB"
    }

    def __init__(self, mode: str = "system"):
        """Initialize theme manager.

        Args:
            mode: 'light', 'dark', or 'system'
        """
        self.mode = mode if mode in ["light", "dark", "system"] else "system"

    def get_colors(self) -> Dict[str, str]:
        """Get color palette for active theme.

        Returns:
            Dictionary mapping color keys to hex values
        """
        if self.mode == "dark":
            return self.DARK_THEME.copy()
        # Default or light theme
        return self.LIGHT_THEME.copy()

    def set_mode(self, mode: str) -> None:
        """Set theme mode.

        Args:
            mode: 'light', 'dark', or 'system'
        """
        if mode in ["light", "dark", "system"]:
            self.mode = mode
