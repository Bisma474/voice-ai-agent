import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.llm_engine import LLMEngine
from src.exceptions import LLMEngineError


class TestLLMEngine(unittest.TestCase):

    def setUp(self):
        self.engine = LLMEngine(model_path="dummy_llm.gguf", context_length=2048)

    def test_generate(self):
        """Test text response generation."""
        response = self.engine.generate("Hello assistant")
        self.assertIn("Hello!", response)

    def test_parameters(self):
        """Test parameter tuning."""
        self.engine.set_parameters(temperature=0.2, max_tokens=256)
        self.assertEqual(self.engine.temperature, 0.2)
        self.assertEqual(self.engine.max_tokens, 256)

    def test_token_count(self):
        """Test token counting estimation."""
        self.assertEqual(self.engine.get_token_count("Hello world test"), 4)

    def test_load_unload(self):
        """Test model loading and unloading."""
        self.engine.unload_model()
        with self.assertRaises(LLMEngineError):
            self.engine.generate("Hi")

        self.engine.load_model("valid_model.gguf")
        response = self.engine.generate("Hi")
        self.assertTrue(len(response) > 0)


if __name__ == '__main__':
    unittest.main()
