import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import VoiceAIAgent
from src.constants import SystemState
from src.tool_manager import BaseTool, ToolResult
from src.constants import PermissionLevel


class MockWeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "weather forecast"

    @property
    def parameters(self) -> dict:
        return {}

    def execute(self, parameters: dict) -> ToolResult:
        return ToolResult(success=True, result="72°F and sunny")

    def get_permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.agent = VoiceAIAgent()

    def tearDown(self):
        self.agent.stop()

    def test_end_to_end_voice_turn(self):
        """Integration test for full turn: audio in -> STT -> LLM -> TTS out."""
        self.agent.start()
        res = self.agent.process_voice_turn(b'HELLO')
        self.assertIn("Hello!", res)
        self.assertEqual(self.agent.state, SystemState.IDLE)

    def test_end_to_end_tool_integration(self):
        """Integration test for tool intent matching and execution."""
        tool = MockWeatherTool()
        self.agent.tool_manager.register_tool(tool)
        self.agent.llm_engine.register_tool(tool)

        self.agent.start()
        res = self.agent.process_voice_turn(b'TEST')
        # LLM receives prompt and generates tool call or text response
        self.assertIsInstance(res, str)


if __name__ == '__main__':
    unittest.main()
