import unittest
import os
import sys
import tempfile
import logging
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.constants import SystemState, PermissionLevel
from src.exceptions import VoiceAIAgentError, ConfigError, AudioPipelineError, ToolPermissionError
from src.logging_config import setup_logging
from src.utils import normalize_text, chunk_text, convert_pcm_format


class TestCoreUtilities(unittest.TestCase):

    def test_constants(self):
        """Test application constants and enums."""
        self.assertEqual(SystemState.IDLE.value, "idle")
        self.assertEqual(SystemState.LISTENING.value, "listening")
        self.assertEqual(PermissionLevel.SAFE.value, "safe")

    def test_custom_exceptions(self):
        """Test custom exception hierarchy and error codes."""
        err = VoiceAIAgentError("Generic error")
        self.assertEqual(err.error_code, "UNKNOWN_ERROR")

        cfg_err = ConfigError("Config issue")
        self.assertEqual(cfg_err.error_code, "CONFIG_ERROR")
        self.assertIsInstance(cfg_err, VoiceAIAgentError)

        perm_err = ToolPermissionError("Permission denied")
        self.assertEqual(perm_err.error_code, "TOOL_PERMISSION_ERROR")

    def test_logging_setup(self):
        """Test logging configuration utility."""
        test_dir = tempfile.mkdtemp()
        try:
            logger = setup_logging(log_dir=test_dir, level="DEBUG")
            self.assertEqual(logger.name, "voice_ai_agent")
            self.assertTrue(Path(test_dir, "voice_ai_agent.log").exists())
        finally:
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_text_utilities(self):
        """Test text normalization and chunking."""
        raw = "  Hello   world!   This is a   test sentence.  "
        normalized = normalize_text(raw)
        self.assertEqual(normalized, "Hello world! This is a test sentence.")

        chunks = chunk_text("Sentence one. Sentence two. Sentence three.", max_chars=25)
        self.assertTrue(len(chunks) >= 2)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 25)

    def test_pcm_resampling(self):
        """Test PCM sample rate conversion helper."""
        dummy_pcm = b'\x00\x00\x10\x00\x20\x00'
        resampled = convert_pcm_format(dummy_pcm, 16000, 16000)
        self.assertEqual(resampled, dummy_pcm)

        resampled_2x = convert_pcm_format(dummy_pcm, 16000, 32000)
        self.assertEqual(len(resampled_2x), len(dummy_pcm) * 2)


if __name__ == '__main__':
    unittest.main()
