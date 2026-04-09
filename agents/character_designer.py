"""
Character Designer Agent
Queries MCP for extract_characters + commit_memory.
Writes character_db.json.
"""

import json
import os
from mcp.tool_loader import loader
from config import config


class CharacterDesigner:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "extract_characters" in available, (
            "[CharacterDesigner] Tool 'extract_characters' not found in MCP registry."
        )
        assert "query_stock_footage" in available, (
            "[CharacterDesigner] Tool 'query_stock_footage' not found in MCP registry."
        )
        assert "commit_memory" in available, (
            "[CharacterDesigner] Tool 'commit_memory' not found in MCP registry."
        )

    def run(self, state: dict) -> dict:
        print("[CharacterDesigner] Extracting characters from script...")
        script = state.get("script", {})
        try:
            characters = loader.invoke("extract_characters", script=script)

            # Enrich each character with stock footage refs
            for name, meta in characters.items():
                refs = loader.invoke("query_stock_footage", query=name)
                meta["stock_refs"] = refs
                loader.invoke(
                    "commit_memory",
                    text=f"Character: {name}. Appearance: {meta.get('appearance')}. Personality: {meta.get('personality')}.",
                    metadata={"type": "character", "name": name},
                )

            state["characters"] = characters

            # Write character_db.json
            db_path = os.path.join(config.output_dir, "character_db.json")
            os.makedirs(config.output_dir, exist_ok=True)
            with open(db_path, "w") as f:
                json.dump({"characters": characters}, f, indent=4)

            print(f"[CharacterDesigner] ✅ {len(characters)} character(s) saved to {db_path}")
        except Exception as e:
            state["error"] = f"[CharacterDesigner] Failed: {e}"
            print(state["error"])
        return state
