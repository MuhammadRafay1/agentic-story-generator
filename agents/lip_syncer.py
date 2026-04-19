"""
Lip Sync Agent
Synchronizes audio waveform and facial movements.
"""
import os
from mcp.tool_loader import loader
from config import config

class LipSyncer:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "lip_sync_aligner" in available, "[LipSyncer] Tool 'lip_sync_aligner' not found."

    def run(self, task: dict) -> dict:
        task_id = task.get("task_id", "unknown_task")
        scene = task.get("scene", {})
        print(f"[LipSyncer] Processing {task_id}...")
        
        final_video_path = ""
        try:
            output_dir = os.path.join(config.output_dir, "raw_scenes")
            out_path = os.path.join(output_dir, f"{task_id}.mp4")
            
            dialogues = scene.get("dialogues", [])
            if not dialogues:
                raise ValueError("No dialogues found for this scene.")
            first_char = dialogues[0].get("character", "UNKNOWN")
            
            audio_path = os.path.join(config.output_dir, "audio", task_id, f"{first_char}_voice.mp3")
            video_path = os.path.join(config.output_dir, "images", f"{first_char}_portrait.png")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio not found at {audio_path}")
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Image not found at {video_path}")
            
            final_video_path = loader.invoke(
                "lip_sync_aligner", 
                audio_path=audio_path, 
                video_path=video_path, 
                output_path=out_path
            )
            print(f"[LipSyncer] ✅ Generated final synced scene for {task_id} at {final_video_path}")
            loader.invoke("commit_memory", text=f"Generated final synced scene: {final_video_path}", metadata={"task_id": task_id})
        except Exception as e:
            print(f"[LipSyncer] ⚠️ Failed for {task_id}: {e}")
            try:
                loader.invoke("commit_memory", text=f"LipSync failed for {task_id}: {e}", metadata={"task_id": task_id, "error": str(e)})
            except Exception:
                pass
            
        return {"final_scenes": [final_video_path]}
