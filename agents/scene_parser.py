"""
Scene Parser Agent
Transforms scene_manifest.json into executable tasks.
"""
from mcp.tool_loader import loader

class SceneParser:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "get_task_graph" in available, "[SceneParser] Tool 'get_task_graph' not found."
        assert "commit_memory" in available, "[SceneParser] Tool 'commit_memory' not found."

    def run(self, state: dict) -> dict:
        print("[SceneParser] Parsing scene manifest into executable tasks...")
        script = state.get("script", {})
        try:
            tasks = loader.invoke("get_task_graph", script=script)
            state["scene_tasks"] = tasks
            
            # Commit to memory
            loader.invoke(
                "commit_memory",
                text=f"Generated {len(tasks)} scene tasks for Phase 2 execution.",
                metadata={"type": "task_graph", "num_tasks": len(tasks)}
            )
            print(f"[SceneParser] ✅ Generated {len(tasks)} independent scene tasks.")
        except Exception as e:
            state["error"] = f"[SceneParser] Failed: {e}"
            print(state["error"])
        return state
