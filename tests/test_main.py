import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import VoiceAIAgent
from src.constants import SystemState


class TestMainOrchestrator(unittest.TestCase):

    def setUp(self):
        self.agent = VoiceAIAgent()

    def tearDown(self):
        self.agent.stop()

    def test_lifecycle_and_state_transitions(self):
        """Test starting and stopping agent orchestrator."""
        self.agent.start()
        self.assertTrue(self.agent.audio_pipeline.is_active)
        self.assertEqual(self.agent.state, SystemState.IDLE)

        self.agent.stop()
        self.assertFalse(self.agent.audio_pipeline.is_active)

    def test_process_voice_turn(self):
        """Test processing voice pipeline turn."""
        self.agent.start()
        response = self.agent.process_voice_turn(b'HELLO')
        self.assertEqual(response, "Hello! How can I assist you today?")
        self.assertEqual(self.agent.state, SystemState.IDLE)


if __name__ == '__main__':
    unittest.main()
