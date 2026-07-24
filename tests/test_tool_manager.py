import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tool_manager import ToolManager, BaseTool, ToolResult
from src.constants import PermissionLevel
from src.exceptions import ToolPermissionError


class MockSafeTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Simple calculator tool"

    @property
    def parameters(self) -> dict:
        return {"type": "object", "properties": {"expression": {"type": "string"}}}

    def execute(self, parameters: dict) -> ToolResult:
        expr = parameters.get("expression", "0")
        return ToolResult(success=True, result=eval(expr))

    def get_permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE


class MockRestrictedTool(BaseTool):
    @property
    def name(self) -> str:
        return "system_cmd"

    @property
    def description(self) -> str:
        return "Restricted system command execution"

    @property
    def parameters(self) -> dict:
        return {"type": "object"}

    def execute(self, parameters: dict) -> ToolResult:
        return ToolResult(success=True, result="executed")

    def get_permission_level(self) -> PermissionLevel:
        return PermissionLevel.RESTRICTED


class TestToolManager(unittest.TestCase):

    def setUp(self):
        self.manager = ToolManager()
        self.safe_tool = MockSafeTool()
        self.restricted_tool = MockRestrictedTool()

    def test_register_and_list_tools(self):
        """Test tool registration and discovery."""
        self.manager.register_tool(self.safe_tool)
        self.assertIn("calculator", self.manager.list_available_tools())
        info = self.manager.get_tool_info("calculator")
        self.assertEqual(info["description"], "Simple calculator tool")

    def test_execute_safe_tool(self):
        """Test safe tool execution."""
        self.manager.register_tool(self.safe_tool)
        res = self.manager.execute_tool("calculator", {"expression": "2 + 3"})
        self.assertTrue(res.success)
        self.assertEqual(res.result, 5)

    def test_restricted_tool_permission(self):
        """Test that restricted tools raise ToolPermissionError."""
        self.manager.register_tool(self.restricted_tool)
        with self.assertRaises(ToolPermissionError):
            self.manager.execute_tool("system_cmd", {})

    def test_enable_disable_tool(self):
        """Test enabling and disabling tools."""
        self.manager.register_tool(self.safe_tool)
        self.manager.disable_tool("calculator")
        res = self.manager.execute_tool("calculator", {"expression": "1 + 1"})
        self.assertFalse(res.success)
        self.assertIn("disabled", res.error)

        self.manager.enable_tool("calculator")
        res2 = self.manager.execute_tool("calculator", {"expression": "1 + 1"})
        self.assertTrue(res2.success)


if __name__ == '__main__':
    unittest.main()
