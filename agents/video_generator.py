"""
Video Generation Agent
Generates scene visuals from scene descriptions.
"""
from mcp.tool_loader import loader

class VideoGenerator:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "query_stock_footage" in available, "[VideoGenerator] Tool 'query_stock_footage' not found."

    def run(self, task: dict) -> dict:
        scene = task.get("scene", {})
        task_id = task.get("task_id", "unknown_task")
        print(f"[VideoGenerator] Processing {task_id}...")
        
        video_refs = []
        try:
            heading = scene.get("heading", "")
            action = scene.get("action", "")
            refs = loader.invoke("query_stock_footage", query=f"{heading} {action}")
            video_refs = refs
            print(f"[VideoGenerator] ✅ Retrieved {len(video_refs)} video refs for {task_id}.")
        except Exception as e:
            print(f"[VideoGenerator] ⚠️ Failed for {task_id}: {e}")
            
        return {"video_results": [{task_id: video_refs}]}
