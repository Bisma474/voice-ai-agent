import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.initialization import check_system_dependencies, initialize_components


class TestInitialization(unittest.TestCase):

    def test_check_system_dependencies(self):
        """Test checking system runtime requirements."""
        deps = check_system_dependencies()
        self.assertTrue(deps["python_version"])
        self.assertTrue(deps["disk_space"])

    def test_initialize_components(self):
        """Test full component initialization sequence."""
        components, config_mgr = initialize_components()
        self.assertIn("audio_pipeline", components)
        self.assertIn("stt_engine", components)
        self.assertIn("llm_engine", components)
        self.assertIn("tts_engine", components)
        self.assertIn("wake_detector", components)
        self.assertIn("tool_manager", components)


if __name__ == '__main__':
    unittest.main()
