import unittest
import os
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import ConfigManager


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "test_config.json"
        ConfigManager._instance = None
        ConfigManager._initialized_paths = set()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        ConfigManager._instance = None
        ConfigManager._initialized_paths = set()

    def test_config_saving_and_loading(self):
        """Test loading default and saving custom configuration."""
        config_manager = ConfigManager(str(self.config_path))
        test_config = {
            "audio": {"sample_rate": 22050},
            "tts": {"voice": "female"}
        }

        config_manager.update_config(test_config)
        result = config_manager.save_config()
        self.assertTrue(result)
        self.assertTrue(self.config_path.exists())

        with open(self.config_path, 'r') as f:
            saved_config = json.load(f)

        self.assertEqual(saved_config['audio']['sample_rate'], 22050)
        self.assertEqual(saved_config['tts']['voice'], 'female')
        self.assertEqual(saved_config['audio']['channels'], 1)

    def test_dot_notation_get_and_set(self):
        """Test getting and setting nested values via dot notation."""
        config_manager = ConfigManager(str(self.config_path))

        self.assertEqual(config_manager.get('audio.sample_rate'), 16000)
        self.assertEqual(config_manager.get('non.existent.key', 'default_val'), 'default_val')

        config_manager.set('audio.sample_rate', 44100)
        self.assertEqual(config_manager.get('audio.sample_rate'), 44100)

        config_manager.set('new_section.sub_key', 'test_value')
        self.assertEqual(config_manager.get('new_section.sub_key'), 'test_value')

    def test_validation(self):
        """Test that invalid configuration values raise ValueError."""
        config_manager = ConfigManager(str(self.config_path))

        # Invalid sample rate
        config_manager.set('audio.sample_rate', -1)
        with self.assertRaises(ValueError):
            config_manager.validate_config()

        config_manager.reset_to_defaults()

        # Invalid TTS speed
        config_manager.set('tts.speed', 5.0)
        with self.assertRaises(ValueError):
            config_manager.validate_config()

    def test_reset_to_defaults(self):
        """Test resetting configuration to default values."""
        config_manager = ConfigManager(str(self.config_path))
        config_manager.set('audio.sample_rate', 48000)
        self.assertEqual(config_manager.get('audio.sample_rate'), 48000)

        config_manager.reset_to_defaults()
        self.assertEqual(config_manager.get('audio.sample_rate'), 16000)

    def test_singleton_pattern(self):
        """Test that ConfigManager enforces singleton pattern per config path."""
        cm1 = ConfigManager(str(self.config_path))
        cm2 = ConfigManager(str(self.config_path))
        self.assertIs(cm1, cm2)


if __name__ == '__main__':
    unittest.main()