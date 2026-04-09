

from typing import TypedDict, List, Dict, Any


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


def get_initial_state(user_input: str, mode: str = "auto") -> AgentState:
    return {
        "input": user_input,
        "mode": mode,
        "script": {},
        "validated": False,
        "characters": {},
        "images": [],
        "memory_refs": [],
        "error": ""
    }