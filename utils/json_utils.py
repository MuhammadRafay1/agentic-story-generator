"""
JSON utilities — robust extraction of JSON from LLM responses.
"""

import json
import re


def extract_json_from_llm_response(text: str) -> dict:
    """
    Strip markdown code fences and extract valid JSON from an LLM response.
    Falls back to a minimal valid structure if parsing fails.
    """
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the first {...} or [...] block
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Return a minimal structure so the workflow can continue
    print("[json_utils] ⚠️  Could not parse JSON from LLM response. Returning minimal structure.")
    return {
        "title": "Untitled",
        "scenes": [
            {
                "scene_id": 1,
                "heading": "INT. UNKNOWN - DAY",
                "action": text[:300],
                "dialogues": [],
                "visual_cues": [],
            }
        ],
    }


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
