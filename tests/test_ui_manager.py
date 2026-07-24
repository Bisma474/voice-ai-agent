import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ui_manager import UIManager
from src.constants import SystemState
from src.theme import ThemeManager


class TestUIManager(unittest.TestCase):

    def setUp(self):
        self.ui = UIManager(theme_mode="dark")

    def test_state_visualization(self):
        """Test system state visual indicator updates."""
        self.assertEqual(self.ui.current_state, SystemState.IDLE)
        self.assertEqual(self.ui.status_widget.label, "Voice Agent Ready")

        self.ui.show_state(SystemState.LISTENING)
        self.assertEqual(self.ui.current_state, SystemState.LISTENING)
        self.assertEqual(self.ui.status_widget.label, "Listening...")

    def test_hotkey_registration(self):
        """Test global hotkey registration and invocation."""
        triggered = []

        def callback():
            triggered.append(True)

        self.ui.register_hotkey(callback, "Ctrl+Space")
        self.assertTrue(self.ui.trigger_hotkey("Ctrl+Space"))
        self.assertEqual(len(triggered), 1)

    def test_menu_and_notifications(self):
        """Test tray menu items and desktop notifications."""
        self.ui.add_menu_item("Settings", lambda: None)
        self.assertEqual(len(self.ui.get_menu_items()), 1)

        self.ui.notify("Error Alert", "Failed to connect audio device")
        self.assertEqual(len(self.ui.get_notifications()), 1)

    def test_theme_management(self):
        """Test dark/light theme switching."""
        theme = ThemeManager("dark")
        colors = theme.get_colors()
        self.assertEqual(colors["bg"], "#111827")

        theme.set_mode("light")
        light_colors = theme.get_colors()
        self.assertEqual(light_colors["bg"], "#FFFFFF")


if __name__ == '__main__':
    unittest.main()
