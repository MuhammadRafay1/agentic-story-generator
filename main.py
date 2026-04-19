"""
Main entry point for PROJECT MONTAGE — Phase 1: Writer's Room.

Usage:
 

  # Manual mode (provide script JSON file):
  python main.py --mode manual --input path/to/script.json
"""

import argparse
import json
import sys
from dotenv import load_dotenv

load_dotenv()

from graph.state import get_initial_state
from graph.workflow import workflow
from graph.phase2_workflow import phase2_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Writer's Room — Autonomous Story & Image Generation (PROJECT MONTAGE Phase 1)"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "manual"],
        default="auto",
        help="'auto' = LLM generates from prompt, 'manual' = provide existing script JSON",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Prompt text (auto mode) or path to script JSON file (manual mode)",
    )
    parser.add_argument(
        "--phase",
        choices=["1", "2"],
        default="1",
        help="Phase to execute: '1' for Writer's Room, '2' for Multimodal Generation",
    )
    args = parser.parse_args()

    # Build initial state
    if args.mode == "manual":
        try:
            with open(args.input, "r") as f:
                script = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load script from '{args.input}': {e}")
            sys.exit(1)
        state = get_initial_state(user_input=args.input, mode="manual")
        state["script"] = script
    else:
        state = get_initial_state(user_input=args.input, mode="auto")

    if args.phase == "1":
        print("\n" + "=" * 60)
        print("  🎬 PROJECT MONTAGE — Writer's Room (Phase 1)")
        print("=" * 60)
        print(f"  Mode  : {args.mode.upper()}")
        print(f"  Input : {args.input[:80]}")
        print("=" * 60 + "\n")

        # Execute the workflow
        final_state = workflow.invoke(state)

        # Summary
        print("\n" + "=" * 60)
        print("  ✅ PHASE 1 WORKFLOW COMPLETE")
        print("=" * 60)
        script = final_state.get("script", {})
        print(f"  Title      : {script.get('title', 'N/A')}")
        print(f"  Scenes     : {len(script.get('scenes', []))}")
        print(f"  Characters : {len(final_state.get('characters', {}))}")
        print(f"  Images     : {len(final_state.get('images', []))}")
        if final_state.get("error"):
            print(f"\n  ⚠️  Error : {final_state['error']}")
        print("=" * 60)

    elif args.phase == "2":
        print("\n" + "=" * 60)
        print("  🎥 PROJECT MONTAGE — Multimodal Generation (Phase 2)")
        print("=" * 60)
        if args.mode != "manual":
            print("[ERROR] Phase 2 requires --mode manual and --input path/to/scene_manifest.json")
            sys.exit(1)
            
        print(f"  Input : {args.input[:80]}")
        print("=" * 60 + "\n")

        # Execute the phase 2 workflow
        final_state = phase2_workflow.invoke(state)
        
        # Summary
        print("\n" + "=" * 60)
        print("  ✅ PHASE 2 WORKFLOW COMPLETE")
        print("=" * 60)
        print(f"  Processed Scenes : {len(final_state.get('scene_tasks', []))}")
        print(f"  Final Videos     : {len(final_state.get('final_scenes', []))}")
        if final_state.get("error"):
            print(f"\n  ⚠️  Error : {final_state['error']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
