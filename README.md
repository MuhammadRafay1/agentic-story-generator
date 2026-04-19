# Writer's Room

Multi-agent system for structured story and image generation.

## Overview

The system follows a multi-agent architecture where specialized agents collaborate using shared memory and are orchestrated through LangGraph workflows.

Key features include:
- Autonomous script generation
- Script validation
- Character identity extraction
- AI-based image generation
- MCP-based dynamic tool discovery
- Human-in-the-loop validation

## Architecture

```
mode_selector → [validator | scriptwriter] → hitl → character_designer
             → image_synthesizer → memory_commit → END
```

**LLM:** Mistral-7B-Instruct via Hugging Face Inference API  
**Image:** Stable Diffusion 2.1 via Hugging Face Inference API  
**Memory:** FAISS + sentence-transformers (local)  
**Orchestration:** LangGraph StateGraph  
**Tools:** MCP dynamic registry (no hardcoded APIs)

## Project Structure

```
├── main.py              # CLI entry point
├── config.py            # Settings & env vars
├── requirements.txt     # Dependencies
│
├── agents/              # Specialized agents
│   ├── scriptwriter.py
│   ├── validator.py
│   ├── hitl.py
│   ├── character_designer.py
│   └── image_synthesizer.py
│
├── graph/               # LangGraph workflow
│   ├── workflow.py
│   └── state.py
│
├── mcp/                 # Tool registry & loader
│   ├── tool_registry.py
│   └── tool_loader.py
│
├── memory/              # FAISS vector store
│   └── vector_store.py
│
├── utils/               # JSON & helpers
│   ├── json_utils.py
│   └── helpers.py
│
└── outputs/             # Generated artifacts
    ├── scene_manifest.json
    ├── character_db.json
    └── images/
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
HF_API_TOKEN=your_token_here
HF_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.3
HF_IMAGE_MODEL=stabilityai/stable-diffusion-2-1
FAISS_INDEX_PATH=memory/faiss_index
OUTPUT_DIR=outputs
```

## Usage

```bash
# Auto mode — LLM generates from your prompt:
python main.py --mode auto --input "A story about criminal gang in Birmingham 1940"

# Manual mode — validate your own script JSON:
python main.py --mode manual --input path/to/script.json
```

## Outputs

| File | Description |
|---|---|
| `outputs/scene_manifest.json` | Structured multi-scene screenplay |
| `outputs/character_db.json` | Character identity store |
| `outputs/images/*.png` | AI-generated character visuals |