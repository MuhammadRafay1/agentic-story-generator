"""
Voice Synthesis Agent
Generates speech aligned with character identity.
"""
import os
from mcp.tool_loader import loader
from config import config

class VoiceSynthesizer:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "voice_cloning_synthesizer" in available, "[VoiceSynthesizer] Tool 'voice_cloning_synthesizer' not found."

    def run(self, task: dict) -> dict:
        scene = task.get("scene", {})
        task_id = task.get("task_id", "unknown_task")
        print(f"[VoiceSynthesizer] Processing {task_id}...")
        
        audio_outputs = []
        try:
            output_dir = os.path.join(config.output_dir, "audio", task_id)
            dialogues = scene.get("dialogues", [])
            for i, dlg in enumerate(dialogues):
                char_name = dlg.get("character", "UNKNOWN")
                line = dlg.get("line", "")
                out_path = loader.invoke(
                    "voice_cloning_synthesizer",
                    character=char_name,
                    dialogues=[line],
                    output_dir=output_dir
                )
                audio_outputs.append({
                    "character": char_name,
                    "audio_path": out_path
                })
            
            print(f"[VoiceSynthesizer] ✅ Synthesized {len(audio_outputs)} voice clips for {task_id}.")
        except Exception as e:
            print(f"[VoiceSynthesizer] ⚠️ Failed for {task_id}: {e}")
        
        return {"audio_results": [{task_id: audio_outputs}]}
