import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tool_manager import ToolManager, BaseTool, ToolResult
from src.constants import PermissionLevel
from src.exceptions import ToolPermissionError


class MaliciousTool(BaseTool):
    @property
    def name(self) -> str:
        return "restricted_file_access"

    @property
    def description(self) -> str:
        return "Access system files"

    @property
    def parameters(self) -> dict:
        return {}

    def execute(self, parameters: dict) -> ToolResult:
        return ToolResult(success=True, result="accessed")

    def get_permission_level(self) -> PermissionLevel:
        return PermissionLevel.RESTRICTED


class TestSecurity(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()

    def test_restricted_tool_prevention(self):
        """Verify that tools with RESTRICTED permission level cannot be executed directly."""
        tool = MaliciousTool()
        self.tool_manager.register_tool(tool)

        with self.assertRaises(ToolPermissionError):
            self.tool_manager.execute_tool("restricted_file_access", {})


if __name__ == '__main__':
    unittest.main()
