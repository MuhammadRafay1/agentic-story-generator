"""
Phase 2 LangGraph Workflow
Implements Map-Reduce parallel execution for multimodal scene generation.
"""

from langgraph.graph import StateGraph, END
try:
    from langgraph.types import Send
except ImportError:
    from langgraph.constants import Send

from graph.state import AgentState, SceneTask

from agents.scene_parser import SceneParser
from agents.voice_synthesizer import VoiceSynthesizer
from agents.video_generator import VideoGenerator
from agents.face_swapper import FaceSwapper
from agents.lip_syncer import LipSyncer

# Instantiate agents
_scene_parser = SceneParser()
_voice_synth = VoiceSynthesizer()
_video_gen = VideoGenerator()
_face_swap = FaceSwapper()
_lip_sync = LipSyncer()

def scene_parser_node(state: AgentState):
    return _scene_parser.run(state)

def map_tasks(state: AgentState):
    """
    Distribute each scene task to parallel Voice and Video branches using Send()
    """
    tasks = state.get("scene_tasks", [])
    sends = []
    for task in tasks:
        # We send the individual task dictionary to both voice and video nodes
        sends.append(Send("voice_synth_node", task))
        sends.append(Send("video_gen_node", task))
    return sends

def voice_synth_node(task: SceneTask):
    return _voice_synth.run(task)

def video_gen_node(task: SceneTask):
    return _video_gen.run(task)

def map_face_swap(state: AgentState):
    tasks = state.get("scene_tasks", [])
    return [Send("face_swap_node", task) for task in tasks]

def face_swap_node(task: SceneTask):
    return _face_swap.run(task)

def map_lip_sync(state: AgentState):
    tasks = state.get("scene_tasks", [])
    return [Send("lip_sync_node", task) for task in tasks]

def lip_sync_node(task: SceneTask):
    return _lip_sync.run(task)

def build_phase2_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("scene_parser_node", scene_parser_node)
    builder.add_node("voice_synth_node", voice_synth_node)
    builder.add_node("video_gen_node", video_gen_node)
    builder.add_node("face_swap_node", face_swap_node)
    builder.add_node("lip_sync_node", lip_sync_node)
    
    # 1. Parse scene
    builder.set_entry_point("scene_parser_node")

    # 2. Map to Voice and Video
    builder.add_conditional_edges("scene_parser_node", map_tasks, ["voice_synth_node", "video_gen_node"])
    
    def aggregator1(state: AgentState):
        return {}
    builder.add_node("aggregator1", aggregator1)
    builder.add_edge("voice_synth_node", "aggregator1")
    builder.add_edge("video_gen_node", "aggregator1")
    
    # 3. Map to Face Swap
    builder.add_conditional_edges("aggregator1", map_face_swap, ["face_swap_node"])
    
    def aggregator2(state: AgentState):
        return {}
    builder.add_node("aggregator2", aggregator2)
    builder.add_edge("face_swap_node", "aggregator2")
    
    # 4. Map to Lip Sync
    builder.add_conditional_edges("aggregator2", map_lip_sync, ["lip_sync_node"])
    
    def aggregator_final(state: AgentState):
        print("\n[Phase 2 Workflow] ✅ All scenes generated successfully.")
        return {}
        
    builder.add_node("aggregator_final", aggregator_final)
    builder.add_edge("lip_sync_node", "aggregator_final")
    builder.add_edge("aggregator_final", END)

    return builder.compile()

phase2_workflow = build_phase2_workflow()
