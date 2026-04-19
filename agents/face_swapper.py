"""
Face Swap Agent
Maps generated characters onto video frames.
"""
from mcp.tool_loader import loader

class FaceSwapper:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "face_swapper" in available, "[FaceSwapper] Tool 'face_swapper' not found."
        assert "identity_validator" in available, "[FaceSwapper] Tool 'identity_validator' not found."

    def run(self, task: dict) -> dict:
        scene = task.get("scene", {})
        task_id = task.get("task_id", "unknown_task")
        print(f"[FaceSwapper] Processing {task_id}...")
        
        swapped_video = ""
        try:
            # Get video ref (just using the first one or a mock string)
            video_ref = f"stock_video_{task_id}"
            characters = set([dlg.get("character", "UNKNOWN") for dlg in scene.get("dialogues", [])])
            
            for char in characters:
                is_valid = loader.invoke("identity_validator", character=char)
                if is_valid:
                    swapped_video = loader.invoke("face_swapper", character=char, video_ref=video_ref)
                    video_ref = swapped_video  # iteratively swap or just keep latest
                    
            print(f"[FaceSwapper] ✅ Completed face swapping for {task_id}.")
        except Exception as e:
            print(f"[FaceSwapper] ⚠️ Failed for {task_id}: {e}")
            
        return {"face_swap_results": [{task_id: swapped_video}]}
