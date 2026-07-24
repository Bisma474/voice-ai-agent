import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tts_engine import TTSEngine


class TestTTSEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TTSEngine(model_path="dummy_tts.onnx", use_fallback=True)

    def test_synthesize(self):
        """Test text synthesis to audio PCM bytes."""
        audio = self.engine.synthesize("Hello world testing speech synthesis.")
        self.assertIsInstance(audio, bytes)
        self.assertGreater(len(audio), 0)

        # Empty string yields empty bytes
        self.assertEqual(self.engine.synthesize(""), b"")

    def test_voices(self):
        """Test voice selection and metadata."""
        voices = self.engine.get_available_voices()
        self.assertIn("female", voices)

        self.engine.set_voice("female")
        info = self.engine.get_voice_info("female")
        self.assertEqual(info["gender"], "female")

    def test_rate_validation(self):
        """Test rate setting validation."""
        self.engine.set_rate(1.5)
        with self.assertRaises(ValueError):
            self.engine.set_rate(3.0)


if __name__ == '__main__':
    unittest.main()
