import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.stt_engine import STTEngine
from src.exceptions import STTEngineError


class TestSTTEngine(unittest.TestCase):

    def setUp(self):
        self.engine = STTEngine(model_path="dummy_model.bin", language="en", model_size="base")

    def test_transcribe(self):
        """Test audio transcription."""
        text = self.engine.transcribe(b'HELLO', sample_rate=16000)
        self.assertEqual(text, "Hello world")

        # Test empty audio
        self.assertEqual(self.engine.transcribe(b''), "")

    def test_language_management(self):
        """Test getting and setting language codes."""
        self.assertIn("en", self.engine.get_supported_languages())
        self.engine.set_language("es")
        self.assertEqual(self.engine.get_model_info()["language"], "es")

        with self.assertRaises(ValueError):
            self.engine.set_language("invalid_code")

    def test_load_unload(self):
        """Test model load and unload."""
        self.engine.unload_model()
        self.assertFalse(self.engine.get_model_info()["is_loaded"])

        with self.assertRaises(STTEngineError):
            self.engine.transcribe(b'HELLO')

        self.engine.load_model("new_model.bin")
        self.assertTrue(self.engine.get_model_info()["is_loaded"])


if __name__ == '__main__':
    unittest.main()
