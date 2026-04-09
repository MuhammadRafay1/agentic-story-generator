"""
Scriptwriter Agent — Mode: auto
Queries MCP for the generate_script_segment tool and calls the HF LLM
to expand a user prompt into a structured multi-scene screenplay JSON.
"""

from mcp.tool_loader import loader


class ScriptWriter:
    def __init__(self):
        tools = loader.load_tools()
        self._available = [t["name"] for t in tools]
        assert "generate_script_segment" in self._available, (
            "[ScriptWriter] Required tool 'generate_script_segment' not found in MCP registry."
        )
        assert "commit_memory" in self._available, (
            "[ScriptWriter] Required tool 'commit_memory' not found in MCP registry."
        )

    def run(self, state: dict) -> dict:
        print("[ScriptWriter] Generating script from prompt...")
        prompt = state.get("input", "")
        try:
            script = loader.invoke("generate_script_segment", prompt=prompt, max_tokens=1500)
            loader.invoke(
                "commit_memory",
                text=f"Script generated from prompt: {prompt}",
                metadata={"type": "script_generation", "title": script.get("title", "")},
            )
            state["script"] = script
            state["error"] = ""
            print(f"[ScriptWriter] Generated '{script.get('title', 'Untitled')}' "
                  f"with {len(script.get('scenes', []))} scene(s).")
        except Exception as e:
            state["error"] = f"[ScriptWriter] Failed: {e}"
            print(state["error"])
        return state
