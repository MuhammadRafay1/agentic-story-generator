"""
LangGraph Workflow — PROJECT MONTAGE Phase 1
7-node StateGraph with conditional routing on mode.

Flow:
  mode_selector → [validator | scriptwriter] → hitl → character_designer
                → image_synthesizer → memory_commit → END
"""

import json
import os
from langgraph.graph import StateGraph, END

from graph.state import AgentState
from agents.scriptwriter import ScriptWriter
from agents.validator import Validator
from agents.hitl import HITLHandler
from agents.character_designer import CharacterDesigner
from agents.image_synthesizer import ImageSynthesizer
from mcp.tool_loader import loader
from config import config

# ------------------------------------------------------------------ #
#  Instantiate agents once                                             #
# ------------------------------------------------------------------ #
_scriptwriter = ScriptWriter()
_validator = Validator()
_hitl = HITLHandler()
_character_designer = CharacterDesigner()
_image_synthesizer = ImageSynthesizer()


# ------------------------------------------------------------------ #
#  Node functions                                                      #
# ------------------------------------------------------------------ #
def mode_selector_node(state: AgentState) -> AgentState:
    """Determine routing based on mode. No-op — routing handled by edge."""
    print(f"\n[Workflow] Mode: {state.get('mode', 'auto').upper()}")
    return state


def validator_node(state: AgentState) -> AgentState:
    return _validator.run(state)


def scriptwriter_node(state: AgentState) -> AgentState:
    return _scriptwriter.run(state)


def hitl_node(state: AgentState) -> AgentState:
    if state.get("error"):
        print(f"[Workflow] Skipping HITL — error present: {state['error']}")
        return state
    return _hitl.run(state)


def character_node(state: AgentState) -> AgentState:
    if not state.get("validated"):
        print("[Workflow] Skipping CharacterDesigner — script not validated.")
        return state
    return _character_designer.run(state)


def image_node(state: AgentState) -> AgentState:
    if not state.get("validated"):
        print("[Workflow] Skipping ImageSynthesizer — script not validated.")
        return state
    return _image_synthesizer.run(state)


def memory_commit_node(state: AgentState) -> AgentState:
    """Final node — commit scene manifest to memory and write JSON file."""
    script = state.get("script", {})
    if script:
        try:
            loader.invoke(
                "commit_memory",
                text=json.dumps(script, indent=2),
                metadata={"type": "scene_manifest", "title": script.get("title", "")},
            )
            # Write scene_manifest.json
            out_path = os.path.join(config.output_dir, "scene_manifest.json")
            os.makedirs(config.output_dir, exist_ok=True)
            with open(out_path, "w") as f:
                json.dump(script, f, indent=4)
            print(f"[Workflow] ✅ scene_manifest.json saved to {out_path}")
            state["memory_refs"].append(out_path)
        except Exception as e:
            print(f"[Workflow] ⚠️  Memory commit failed: {e}")
    return state


# ------------------------------------------------------------------ #
#  Conditional routing                                                 #
# ------------------------------------------------------------------ #
def route_by_mode(state: AgentState) -> str:
    return "validate" if state.get("mode") == "manual" else "generate"


def route_after_hitl(state: AgentState) -> str:
    if state.get("error") or not state.get("validated"):
        return "stop"
    return "continue"


# ------------------------------------------------------------------ #
#  Graph construction                                                  #
# ------------------------------------------------------------------ #
def build_workflow():
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("mode_selector", mode_selector_node)
    graph.add_node("validator", validator_node)
    graph.add_node("scriptwriter", scriptwriter_node)
    graph.add_node("hitl", hitl_node)
    graph.add_node("character_designer", character_node)
    graph.add_node("image_synthesizer", image_node)
    graph.add_node("memory_commit", memory_commit_node)

    # Entry point
    graph.set_entry_point("mode_selector")

    # Conditional routing: mode_selector → validator OR scriptwriter
    graph.add_conditional_edges(
        "mode_selector",
        route_by_mode,
        {"validate": "validator", "generate": "scriptwriter"},
    )

    # Both paths converge at HITL
    graph.add_edge("validator", "hitl")
    graph.add_edge("scriptwriter", "hitl")

    # Conditional routing: hitl → continue OR stop
    graph.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {"continue": "character_designer", "stop": END},
    )

    # Linear tail
    graph.add_edge("character_designer", "image_synthesizer")
    graph.add_edge("image_synthesizer", "memory_commit")
    graph.add_edge("memory_commit", END)

    return graph.compile()


workflow = build_workflow()
