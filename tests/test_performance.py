import unittest
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import VoiceAIAgent


class TestPerformance(unittest.TestCase):

    def setUp(self):
        self.agent = VoiceAIAgent()

    def tearDown(self):
        self.agent.stop()

    def test_end_to_end_latency_benchmark(self):
        """Test processing latency threshold (< 500ms for simulated pipeline)."""
        self.agent.start()
        start_t = time.time()
        self.agent.process_voice_turn(b'HELLO')
        elapsed_ms = (time.time() - start_t) * 1000.0

        # Verify pipeline completes rapidly
        self.assertLess(elapsed_ms, 500.0)


if __name__ == '__main__':
    unittest.main()
