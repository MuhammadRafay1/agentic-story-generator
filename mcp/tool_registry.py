"""
MCP Tool Registry — all tools are registered here with their schemas.
Agents MUST query this registry at runtime; no hardcoded API calls allowed.
"""

from huggingface_hub import InferenceClient
from config import config


class ToolRegistry:
    def __init__(self):
        self._tools: dict = {}
        self._register_all()

    # ------------------------------------------------------------------ #
    #  Internal registration                                               #
    # ------------------------------------------------------------------ #
    def _register_all(self):
        self.register_tool(
            name="generate_script_segment",
            description="Call the Hugging Face LLM to expand a user prompt into a structured multi-scene screenplay JSON.",
            parameters={"prompt": "str", "max_tokens": "int"},
            handler=self._generate_script_segment,
        )
        self.register_tool(
            name="validate_script_structure",
            description="Check that a script JSON has required fields: scene_id, heading, action, dialogues, visual_cues.",
            parameters={"script": "dict"},
            handler=self._validate_script_structure,
        )
        self.register_tool(
            name="extract_characters",
            description="Parse all unique characters from a script JSON and return their metadata.",
            parameters={"script": "dict"},
            handler=self._extract_characters,
        )
        self.register_tool(
            name="generate_character_image",
            description="Call the HF Stable Diffusion API to generate a character reference image.",
            parameters={"character_name": "str", "appearance": "str", "output_path": "str"},
            handler=self._generate_character_image,
        )
        self.register_tool(
            name="commit_memory",
            description="Embed and store a document string in the FAISS vector store.",
            parameters={"text": "str", "metadata": "dict"},
            handler=self._commit_memory,
        )
        self.register_tool(
            name="query_memory",
            description="Perform a semantic search over the FAISS vector store.",
            parameters={"query": "str", "k": "int"},
            handler=self._query_memory,
        )
        self.register_tool(
            name="query_stock_footage",
            description="Return placeholder stock footage references for a given character or scene.",
            parameters={"query": "str"},
            handler=self._query_stock_footage,
        )
        self.register_tool(
            name="get_task_graph",
            description="Decomposes a scene_manifest.json into independent scene tasks for Phase 2.",
            parameters={"script": "dict"},
            handler=self._get_task_graph,
        )
        self.register_tool(
            name="voice_cloning_synthesizer",
            description="Mocks generation of character speech using voice cloning.",
            parameters={"character": "str", "dialogues": "list", "output_dir": "str"},
            handler=self._voice_cloning_synthesizer,
        )
        self.register_tool(
            name="face_swapper",
            description="Mocks mapping a character identity onto video frames.",
            parameters={"character": "str", "video_ref": "str"},
            handler=self._face_swapper,
        )
        self.register_tool(
            name="identity_validator",
            description="Validates that a character identity matches the expected criteria.",
            parameters={"character": "str"},
            handler=self._identity_validator,
        )
        self.register_tool(
            name="lip_sync_aligner",
            description="Mocks synchronizing audio and facial movements into a final MP4.",
            parameters={"audio_path": "str", "video_path": "str", "output_path": "str"},
            handler=self._lip_sync_aligner,
        )

    def register_tool(self, name: str, description: str, parameters: dict, handler):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    def get_tool(self, name: str):
        if name not in self._tools:
            raise KeyError(f"[MCP] Tool '{name}' not found in registry.")
        return self._tools[name]

    def list_tools(self) -> list[dict]:
        """Return tool schemas (without handlers) for agent inspection."""
        return [
            {k: v for k, v in tool.items() if k != "handler"}
            for tool in self._tools.values()
        ]

    def invoke(self, name: str, **kwargs):
        tool = self.get_tool(name)
        return tool["handler"](**kwargs)

    # ------------------------------------------------------------------ #
    #  Tool implementations                                                #
    # ------------------------------------------------------------------ #
    def _generate_script_segment(self, prompt: str, max_tokens: int = 1024) -> dict:
        """Call HF Serverless Inference API to generate screenplay JSON from a user prompt."""
        system = (
            "You are a professional screenplay writer tasked to write screenplays."
            "Given a user prompt, generate a structured multi-scene screenplay as valid JSON only. "
            "Return ONLY valid JSON with this exact schema, no extra text:\n"
            '{"title": "...", "scenes": [{"scene_id": 1, "heading": "INT. LOCATION - DAY", '
            '"action": "...", "dialogues": [{"character": "...", "line": "..."}], '
            '"visual_cues": ["..."]}]}'
        )
        client = InferenceClient(api_key=config.hf_api_token)
        response = client.chat.completions.create(
            model=config.hf_model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        raw_text = response.choices[0].message.content
        from utils.json_utils import extract_json_from_llm_response
        return extract_json_from_llm_response(raw_text)

    def _validate_script_structure(self, script: dict) -> dict:
        """Validate that the script JSON has the required fields."""
        errors = []
        if "scenes" not in script or not script["scenes"]:
            errors.append("Missing 'scenes' list.")
        else:
            for i, scene in enumerate(script["scenes"]):
                for field in ("scene_id", "heading", "action", "dialogues", "visual_cues"):
                    if field not in scene:
                        errors.append(f"Scene {i + 1} missing '{field}'.")
        return {"valid": len(errors) == 0, "errors": errors}

    def _extract_characters(self, script: dict) -> dict:
        """Extract unique characters from script dialogues."""
        characters = {}
        for scene in script.get("scenes", []):
            for dlg in scene.get("dialogues", []):
                name = dlg.get("character", "").strip().upper()
                if name and name not in characters:
                    characters[name] = {
                        "personality": "To be defined",
                        "appearance": "To be defined",
                        "style": "Cinematic",
                        "image_ref": "",
                    }
        return characters

    def _generate_character_image(self, character_name: str, appearance: str, output_path: str) -> str:
        """Call HF Serverless Inference API to generate a character image, save it as PNG."""
        import os

        prompt = (
            f"Portrait of {character_name}, {appearance}, "
            "cinematic lighting, high detail, film still, 8k"
        )
        client = InferenceClient(api_key=config.hf_api_token)
        image = client.text_to_image(
            prompt,
            model=config.hf_image_model,
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        return output_path

    def _commit_memory(self, text: str, metadata: dict = None) -> str:
        """Embed and store text in the FAISS vector store."""
        from memory.vector_store import VectorStore
        store = VectorStore()
        store.load()
        store.add_document(text, metadata or {})
        store.persist()
        return f"[MEMORY] Committed: {text[:60]}..."

    def _query_memory(self, query: str, k: int = 3) -> list:
        """Semantic search over FAISS store."""
        from memory.vector_store import VectorStore
        store = VectorStore()
        store.load()
        return store.search(query, k=k)

    def _query_stock_footage(self, query: str) -> list:
        """Stub — returns placeholder stock footage references."""
        return [f"stock://footage/{query.replace(' ', '_')}_ref_{i}" for i in range(3)]

    def _get_task_graph(self, script: dict) -> list:
        """Decompose a scene manifest into a list of independent scene tasks."""
        scenes = script.get("scenes", [])
        tasks = []
        for i, scene in enumerate(scenes):
            tasks.append({
                "task_id": f"scene_{scene.get('scene_id', i+1)}",
                "scene": scene
            })
        return tasks

    def _voice_cloning_synthesizer(self, character: str, dialogues: list, output_dir: str) -> str:
        """Actual natural speech synthesis using edge-tts."""
        import os
        import sys
        import subprocess
        
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"{character}_voice.mp3")
        
        voices = ["en-US-GuyNeural", "en-US-AriaNeural", "en-US-ChristopherNeural", "en-US-JennyNeural"]
        voice = voices[len(character) % len(voices)]
        
        text = " ".join(dialogues)
        if not text.strip():
            text = "..."
            
        print(f"[ToolRegistry] Synthesizing speech for {character} using {voice}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", out_path],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[ToolRegistry] edge-tts error: {e.stderr.decode('utf-8', errors='ignore')}")
            raise RuntimeError(f"Voice synthesis failed for {character}")
            
        return out_path

    def _face_swapper(self, character: str, video_ref: str) -> str:
        """Provide a static visual coherence image for the character."""
        import os
        from config import config
        from PIL import Image, ImageDraw
        
        image_path = os.path.join(config.output_dir, "images", f"{character}_portrait.png")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        if not os.path.exists(image_path):
            try:
                img = Image.new('RGB', (1024, 1024), color = (73, 109, 137))
                d = ImageDraw.Draw(img)
                d.text((400,500), f"Character:\n{character}", fill=(255,255,0))
                img.save(image_path)
            except Exception as e:
                print(f"[ToolRegistry] Error creating portrait: {e}")
                
        return image_path

    def _identity_validator(self, character: str) -> bool:
        """Mock identity validation."""
        return True

    def _lip_sync_aligner(self, audio_path: str, video_path: str, output_path: str) -> str:
        """Actual temporal alignment: merge static visual with generated audio."""
        import os
        from moviepy import ImageClip, AudioFileClip
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"[ToolRegistry] Aligning {audio_path} with {video_path}...")
        
        try:
            audio_clip = AudioFileClip(audio_path)
            video_clip = ImageClip(video_path).with_duration(audio_clip.duration)
            video_clip = video_clip.with_audio(audio_clip)
            
            video_clip.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=None
            )
            audio_clip.close()
            video_clip.close()
        except Exception as e:
            print(f"[ToolRegistry] Lip sync alignment failed: {e}")
            raise
            
        return output_path

# Singleton
registry = ToolRegistry()
