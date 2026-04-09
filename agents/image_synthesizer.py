"""
Image Synthesizer Agent
Queries MCP for generate_character_image.
Calls HF Stable Diffusion per character, saves to outputs/images/.
"""

import os
from mcp.tool_loader import loader
from config import config


class ImageSynthesizer:
    def __init__(self):
        tools = loader.load_tools()
        available = [t["name"] for t in tools]
        assert "generate_character_image" in available, (
            "[ImageSynthesizer] Tool 'generate_character_image' not found in MCP registry."
        )

    def run(self, state: dict) -> dict:
        print("[ImageSynthesizer] Generating character images...")
        characters = state.get("characters", {})
        images_dir = os.path.join(config.output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        image_paths = []

        for name, meta in characters.items():
            safe_name = name.lower().replace(" ", "_")
            output_path = os.path.join(images_dir, f"{safe_name}.png")
            try:
                path = loader.invoke(
                    "generate_character_image",
                    character_name=name,
                    appearance=meta.get("appearance", "neutral appearance"),
                    output_path=output_path,
                )
                meta["image_ref"] = path
                image_paths.append(path)
                print(f"[ImageSynthesizer] ✅ Image saved: {path}")
            except Exception as e:
                print(f"[ImageSynthesizer] ⚠️  Failed for '{name}': {e}")
                meta["image_ref"] = ""

        state["images"] = image_paths
        state["characters"] = characters
        return state
