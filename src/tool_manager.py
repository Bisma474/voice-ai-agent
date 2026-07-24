"""
Tool Manager component for Voice AI Agent.
Manages registration, discovery, permission checking, and execution of external tools.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.constants import PermissionLevel
from src.exceptions import ToolError, ToolPermissionError


class ToolResult:
    """Encapsulates the output of a tool execution."""

    def __init__(self, success: bool, result: Any = None, error: Optional[str] = None):
        self.success = success
        self.result = result
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error
        }


class BaseTool(ABC):
    """Abstract Base Class for all voice assistant tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human readable description of the tool."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema dictionary defining input parameters."""
        pass

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute tool logic with given parameter values."""
        pass

    def get_permission_level(self) -> PermissionLevel:
        """Get permission level required to run this tool."""
        return PermissionLevel.SAFE

    def requires_confirmation(self) -> bool:
        """Check if user confirmation is required before execution."""
        return self.get_permission_level() in (PermissionLevel.CONFIRM, PermissionLevel.RESTRICTED)


class ToolManager:
    """Manages discovery, registration, security permissions, and invocation of tools."""

    def __init__(self, tools_directory: Optional[str] = None):
        """Initialize ToolManager.

        Args:
            tools_directory: Directory path for dynamic plugin loading
        """
        self.tools_directory = tools_directory or os.path.expanduser("~/.voice_ai/tools")
        self._tools: Dict[str, BaseTool] = {}
        self._enabled_tools: Dict[str, bool] = {}
        self._execution_logs: List[Dict[str, Any]] = []

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool object.

        Args:
            tool: Instance of BaseTool subclass
        """
        if not isinstance(tool, BaseTool):
            raise TypeError("Tool must be an instance of BaseTool")
        name = tool.name
        if not name:
            raise ValueError("Tool name cannot be empty")
        self._tools[name] = tool
        self._enabled_tools[name] = True

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool by name.

        Args:
            tool_name: String name of tool

        Returns:
            True if removed, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            self._enabled_tools.pop(tool_name, None)
            return True
        return False

    def enable_tool(self, tool_name: str) -> None:
        """Enable execution for registered tool.

        Args:
            tool_name: Name of tool
        """
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' is not registered.")
        self._enabled_tools[tool_name] = True

    def disable_tool(self, tool_name: str) -> None:
        """Disable execution for registered tool.

        Args:
            tool_name: Name of tool
        """
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' is not registered.")
        self._enabled_tools[tool_name] = False

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if tool is registered and enabled."""
        return self._enabled_tools.get(tool_name, False)

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with parameters after checking status and permissions.

        Args:
            tool_name: Name of target tool
            parameters: Input parameters dict

        Returns:
            ToolResult object
        """
        if tool_name not in self._tools:
            err_msg = f"Tool '{tool_name}' not found."
            return ToolResult(success=False, error=err_msg)

        if not self.is_tool_enabled(tool_name):
            err_msg = f"Tool '{tool_name}' is disabled."
            return ToolResult(success=False, error=err_msg)

        tool = self._tools[tool_name]

        # Check permissions
        if tool.get_permission_level() == PermissionLevel.RESTRICTED:
            raise ToolPermissionError(f"Execution of restricted tool '{tool_name}' requires elevated authorization.")

        try:
            result = tool.execute(parameters)
            self._log_execution(tool_name, parameters, result)
            return result
        except Exception as e:
            res = ToolResult(success=False, error=str(e))
            self._log_execution(tool_name, parameters, res)
            return res

    def list_available_tools(self) -> List[str]:
        """Get names of all registered tools."""
        return list(self._tools.keys())

    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get details about a registered tool.

        Args:
            tool_name: Name of tool

        Returns:
            Dictionary containing metadata
        """
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' not found.")

        tool = self._tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "permission_level": tool.get_permission_level().value,
            "requires_confirmation": tool.requires_confirmation(),
            "is_enabled": self.is_tool_enabled(tool_name)
        }

    def _log_execution(self, tool_name: str, params: Dict[str, Any], result: ToolResult) -> None:
        """Internal execution audit logging."""
        import time
        self._execution_logs.append({
            "timestamp": time.time(),
            "tool_name": tool_name,
            "parameters": params,
            "success": result.success,
            "error": result.error
        })

    def get_execution_logs(self) -> List[Dict[str, Any]]:
        """Return execution logs."""
        return self._execution_logs.copy()
