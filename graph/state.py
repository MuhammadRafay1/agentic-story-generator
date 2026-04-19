

from typing import TypedDict, List, Dict, Any, Annotated
import operator

class SceneTask(TypedDict):
    task_id: str
    scene: Dict[str, Any]


class AgentState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph workflow.
    """

    # 🔹 Input Layer
    input: str                  # User prompt OR raw script
    mode: str                   # "manual" or "auto"

    # 🔹 Script Layer
    script: Dict[str, Any]      # Structured screenplay JSON
    validated: bool             # Whether script passed validation

    # 🔹 Character Layer
    characters: Dict[str, Dict[str, Any]]  # Character database

    # 🔹 Image Layer
    images: List[str]           # Paths to generated images

    # 🔹 Memory Layer
    memory_refs: List[str]      # References stored in vector DB

    # 🔹 Control / Debugging
    error: str                  # Error message (if any)

    # 🔹 Phase 2 Layer
    scene_tasks: List[SceneTask]
    audio_results: Annotated[List[Dict[str, Any]], operator.add]
    video_results: Annotated[List[Dict[str, Any]], operator.add]
    face_swap_results: Annotated[List[Dict[str, Any]], operator.add]
    final_scenes: Annotated[List[str], operator.add]


def get_initial_state(user_input: str, mode: str = "auto") -> AgentState:
    return {
        "input": user_input,
        "mode": mode,
        "script": {},
        "validated": False,
        "characters": {},
        "images": [],
        "memory_refs": [],
        "error": "",
        "scene_tasks": [],
        "audio_results": [],
        "video_results": [],
        "face_swap_results": [],
        "final_scenes": []
    }