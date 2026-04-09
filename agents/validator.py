"""
Validator Agent — Mode: manual
Queries MCP for validate_script_structure and checks the provided script JSON.
"""

from mcp.tool_loader import loader


class Validator:
    def __init__(self):
        tools = loader.load_tools()
        self._available = [t["name"] for t in tools]
        assert "validate_script_structure" in self._available, (
            "[Validator] Required tool 'validate_script_structure' not found in MCP registry."
        )

    def run(self, state: dict) -> dict:
        print("[Validator] Validating script structure...")
        script = state.get("script", {})
        try:
            result = loader.invoke("validate_script_structure", script=script)
            state["validated"] = result["valid"]
            if result["valid"]:
                print("[Validator] ✅ Script is valid.")
            else:
                print("[Validator] ❌ Validation failed:")
                for err in result["errors"]:
                    print(f"   • {err}")
                state["error"] = "Validation failed: " + "; ".join(result["errors"])
        except Exception as e:
            state["validated"] = False
            state["error"] = f"[Validator] Exception: {e}"
            print(state["error"])
        return state
