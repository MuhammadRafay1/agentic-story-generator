"""
MCP Tool Loader — agents call this to discover available tools at runtime.
"""

from mcp.tool_registry import registry


class ToolLoader:
    def load_tools(self) -> list[dict]:
        """Return all registered tool schemas (agents use this to know what's available)."""
        return registry.list_tools()

    def invoke(self, tool_name: str, **kwargs):
        """Invoke a tool by name through the registry."""
        return registry.invoke(tool_name, **kwargs)


# Singleton loader used by all agents
loader = ToolLoader()
