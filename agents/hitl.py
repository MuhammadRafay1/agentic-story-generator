"""
Human-in-the-Loop (HITL) Agent
Provides a checkpoint: user can Approve, Reject, or Edit the generated script.
"""

import json


class HITLHandler:
    def run(self, state: dict) -> dict:
        script = state.get("script", {})
        title = script.get("title", "Untitled")
        scenes = script.get("scenes", [])

        print("\n" + "=" * 60)
        print("  🎬 HUMAN-IN-THE-LOOP CHECKPOINT")
        print("=" * 60)
        print(f"  Title     : {title}")
        print(f"  Scenes    : {len(scenes)}")
        for s in scenes:
            print(f"\n  Scene {s.get('scene_id', '?')}: {s.get('heading', '')}")
            print(f"    Action  : {s.get('action', '')[:80]}...")
            for dlg in s.get("dialogues", [])[:2]:
                print(f"    [{dlg.get('character', '?')}]: {dlg.get('line', '')[:60]}")
        print("\n" + "=" * 60)
        print("  [A] Approve   [R] Reject   [E] Edit JSON")
        print("=" * 60)

        choice = input("  Your choice: ").strip().upper()

        if choice == "A":
            state["validated"] = True
            print("[HITL] ✅ Script approved.")
        elif choice == "R":
            state["validated"] = False
            state["error"] = "[HITL] Script rejected by user."
            print("[HITL] ❌ Script rejected. Workflow will stop.")
        elif choice == "E":
            print("[HITL] Paste your edited JSON (end with a blank line):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            try:
                edited = json.loads("\n".join(lines))
                state["script"] = edited
                state["validated"] = True
                print("[HITL] ✅ Edited script accepted.")
            except json.JSONDecodeError as e:
                state["error"] = f"[HITL] Invalid JSON: {e}"
                print(state["error"])
        else:
            print("[HITL] Unrecognised choice — defaulting to Approve.")
            state["validated"] = True

        return state
