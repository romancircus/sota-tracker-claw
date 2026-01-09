#!/usr/bin/env python3
"""
Initialize the SOTA Tracker database with schema and seed data.

Run this once to set up the database:
    python init_db.py
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "sota.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


def create_schema(db: sqlite3.Connection):
    """Create database schema."""
    db.executescript("""
        -- Models table (updated with is_open_source)
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            release_date DATE,
            source TEXT DEFAULT 'manual',
            source_url TEXT,
            is_sota BOOLEAN DEFAULT FALSE,
            is_open_source BOOLEAN DEFAULT TRUE,
            sota_rank INTEGER,
            sota_rank_open INTEGER,      -- Rank among open-source only
            metrics JSON,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Forbidden models
        CREATE TABLE IF NOT EXISTS forbidden (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            reason TEXT NOT NULL,
            replacement TEXT,
            category TEXT,
            deprecated_date DATE,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Categories
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            default_open_source BOOLEAN DEFAULT TRUE
        );

        -- Cache tracking (per-category freshness)
        CREATE TABLE IF NOT EXISTS cache_status (
            category TEXT PRIMARY KEY,
            last_fetched TIMESTAMP,
            fetch_source TEXT,           -- 'huggingface', 'lmarena', 'artificial_analysis', 'manual'
            fetch_success BOOLEAN DEFAULT TRUE,
            error_message TEXT
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_models_category ON models(category);
        CREATE INDEX IF NOT EXISTS idx_models_sota ON models(is_sota);
        CREATE INDEX IF NOT EXISTS idx_models_open ON models(is_open_source);
        CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);
    """)


def seed_categories(db: sqlite3.Connection):
    """Seed model categories."""
    categories = [
        ("image_gen", "Image Generation", "Text/image to image generation", True),
        ("image_edit", "Image Editing", "Image editing, inpainting, style transfer", True),
        ("video", "Video Generation", "Text/image to video", True),
        ("llm_local", "Local LLMs", "LLMs for local inference (GGUF, llama.cpp)", True),
        ("llm_api", "API LLMs", "Cloud-based LLM APIs", False),
        ("llm_coding", "Coding LLMs", "LLMs optimized for code generation", True),
        ("tts", "Text-to-Speech", "Voice synthesis and cloning", True),
        ("stt", "Speech-to-Text", "Audio transcription", True),
        ("music", "Music Generation", "AI music creation", True),
        ("3d", "3D Generation", "3D model and scene generation", True),
        ("embeddings", "Embeddings", "Vector embedding models", True),
    ]

    db.executemany(
        "INSERT OR REPLACE INTO categories (id, name, description, default_open_source) VALUES (?, ?, ?, ?)",
        categories
    )


def seed_sota_models(db: sqlite3.Connection):
    """Seed current SOTA models (January 2026) - VERIFIED."""

    models = [
        # =====================================================================
        # IMAGE GENERATION (verified Jan 2026)
        # =====================================================================
        # Closed source
        {
            "id": "gpt-image-1.5",
            "name": "GPT Image 1.5",
            "category": "image_gen",
            "release_date": "2025-12-16",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 1,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 overall (1264 Elo), 4x faster than GPT-4o image, native text rendering",
                "why_sota": "Highest benchmark scores, best prompt adherence, superior text-in-image",
                "strengths": ["Text rendering", "Prompt accuracy", "Speed", "Photorealism"],
                "use_cases": ["Marketing assets", "UI mockups", "Any task needing text in images"],
                "elo": 1264
            }
        },
        {
            "id": "gemini-3-pro-image",
            "name": "Gemini 3 Pro Image",
            "category": "image_gen",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 2,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#2 overall (1235 Elo), strong across all categories, great diversity",
                "why_sota": "Excellent balance of quality, diversity, and consistency",
                "strengths": ["Diverse styles", "Consistency", "Creative interpretation"],
                "use_cases": ["Creative projects", "Varied style needs", "Exploration"],
                "elo": 1235
            }
        },
        # Open source
        {
            "id": "z-image-turbo",
            "name": "Z-Image-Turbo",
            "category": "image_gen",
            "release_date": "2025-11-26",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 3,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 open-source (1150 Elo), 6B params, runs on 16GB VRAM, ~$5/1k images self-hosted",
                "why_sota": "Best quality/efficiency ratio for open-source, production-ready speed",
                "strengths": ["Fast inference", "Low VRAM", "Cost-effective", "RTX 4090 compatible"],
                "use_cases": ["High-volume production", "Real-time apps", "Budget-conscious deployments"],
                "vram": "16GB",
                "elo": 1150
            }
        },
        {
            "id": "flux2-dev",
            "name": "FLUX.2-dev",
            "category": "image_gen",
            "release_date": "2025-11-25",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 4,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 open-source, 32B params, multi-image consistency, needs 96GB VRAM (A100/H100)",
                "why_sota": "Best for consistent character/style across multiple images",
                "strengths": ["Character consistency", "Style consistency", "High detail", "Professional quality"],
                "use_cases": ["Comic/story generation", "Brand assets", "Character design", "Multi-shot campaigns"],
                "vram": "96GB"
            }
        },
        {
            "id": "qwen-image-2512",
            "name": "Qwen-Image-2512",
            "category": "image_gen",
            "release_date": "2025-12-31",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 5,
            "sota_rank_open": 3,
            "metrics": {
                "notes": "#3 open-source, best human realism/skin detail, 40GB+ VRAM, slow but highest quality portraits",
                "why_sota": "Unmatched photorealistic humans, skin texture, and facial detail",
                "strengths": ["Portrait quality", "Skin realism", "Human anatomy", "Natural lighting"],
                "use_cases": ["Portrait photography", "Fashion", "Character art", "Realistic humans"],
                "vram": "40GB+"
            }
        },

        # =====================================================================
        # IMAGE EDITING
        # =====================================================================
        {
            "id": "qwen-image-edit-2511",
            "name": "Qwen-Image-Edit-2511",
            "category": "image_edit",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 image editing, natural language instructions, preserves unedited regions perfectly",
                "why_sota": "Best understanding of natural language edit requests, surgical precision",
                "strengths": ["Instruction following", "Region preservation", "Natural edits", "Multi-step editing"],
                "use_cases": ["Photo retouching", "Object removal/addition", "Background changes", "Style transfer"]
            }
        },
        {
            "id": "flux1-kontext",
            "name": "FLUX.1-Kontext",
            "category": "image_edit",
            "release_date": "2025-06-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 2,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 image editing, specialized in color/style transfer, maintains structure",
                "why_sota": "Best for recoloring and style changes while preserving composition",
                "strengths": ["Color transfer", "Style transfer", "Structure preservation", "Lighting changes"],
                "use_cases": ["Recoloring products", "Season changes", "Time-of-day changes", "Style variations"]
            }
        },

        # =====================================================================
        # VIDEO GENERATION (verified Jan 2026)
        # =====================================================================
        # Closed source
        {
            "id": "veo-3.1",
            "name": "Google Veo 3.1",
            "category": "video",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 1,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 overall, 4K photorealism, native audio, trained on YouTube dataset",
                "why_sota": "Unmatched photorealism from massive YouTube training data, native audio generation",
                "strengths": ["Photorealism", "Physics accuracy", "Native audio", "Long coherence"],
                "use_cases": ["Professional video production", "Commercials", "Film VFX", "High-end content"]
            }
        },
        {
            "id": "runway-gen-4.5",
            "name": "Runway Gen-4.5",
            "category": "video",
            "release_date": "2025-12-11",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 2,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#2 overall, native audio, 1-min multi-shot videos, character consistency across shots",
                "why_sota": "Best for professional workflows with multi-shot coherence and character tracking",
                "strengths": ["Multi-shot consistency", "Character tracking", "Native audio", "Professional UI"],
                "use_cases": ["Short films", "Music videos", "Ads with recurring characters", "Storyboarding"]
            }
        },
        {
            "id": "sora-2",
            "name": "OpenAI Sora 2",
            "category": "video",
            "release_date": "2025-11-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 3,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#3 overall, native audio, 20s high-quality videos, cinematic camera control",
                "why_sota": "Best understanding of cinematic language, camera movements, and scene composition",
                "strengths": ["Cinematic quality", "Camera control", "Scene composition", "Native audio"],
                "use_cases": ["Cinematic shorts", "Concept visualization", "Creative exploration"]
            }
        },
        {
            "id": "kling-2.6",
            "name": "Kling 2.6",
            "category": "video",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 4,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#4 overall, best human motion/expressions, 1080p, up to 3-min with extend feature",
                "why_sota": "Most realistic human movements, facial expressions, and lip sync",
                "strengths": ["Human motion", "Facial expressions", "Lip sync", "Length extension"],
                "use_cases": ["Talking head videos", "Human-centric content", "Virtual avatars", "Long-form content"]
            }
        },
        # Open source
        {
            "id": "ltx-2",
            "name": "LTX-2",
            "category": "video",
            "release_date": "2026-01-06",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 5,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 open-source, native audio, 4K 50fps, runs on 12GB VRAM (RTX 4090), fastest inference",
                "why_sota": "Best open-source with native audio, runs on consumer hardware, real-time capable",
                "strengths": ["Speed", "Native audio", "4K output", "Low VRAM", "RTX 4090 compatible"],
                "use_cases": ["Real-time generation", "High-volume production", "Consumer GPU workflows", "Prototyping"],
                "vram": "12GB"
            }
        },
        {
            "id": "wan-2.2",
            "name": "Wan 2.2",
            "category": "video",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 6,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 open-source, MoE architecture, best human motion quality, 720p output",
                "why_sota": "Highest quality human motion in open-source, sophisticated MoE architecture",
                "strengths": ["Human motion quality", "Natural movement", "Gesture accuracy", "Emotional expression"],
                "use_cases": ["Human-centric videos", "Dance/movement", "Character animation", "Realistic humans"]
            }
        },
        {
            "id": "hunyuan-video-1.5",
            "name": "HunyuanVideo 1.5",
            "category": "video",
            "release_date": "2025-11-21",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 7,
            "sota_rank_open": 3,
            "metrics": {
                "notes": "#3 open-source, 13B params, cinematic quality, excels at complex multi-object scenes",
                "why_sota": "Best at complex scenes with multiple interacting objects and characters",
                "strengths": ["Complex scenes", "Multi-object tracking", "Cinematic look", "Scene coherence"],
                "use_cases": ["Complex narratives", "Multi-character scenes", "Action sequences", "Detailed environments"]
            }
        },
        {
            "id": "wan2.1-i2v",
            "name": "Wan2.1-I2V",
            "category": "video",
            "release_date": "2025-06-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 8,
            "sota_rank_open": 4,
            "metrics": {
                "notes": "#4 open-source, image-to-video specialist, best creature/animal realism, silky smooth motion",
                "why_sota": "Unmatched creature animation and texture detail from static images",
                "strengths": ["Image-to-video", "Creature realism", "Texture detail", "Smooth motion"],
                "use_cases": ["Animating photos", "Creature/animal content", "Nature scenes", "Texture-heavy subjects"]
            }
        },

        # =====================================================================
        # LOCAL LLMs (verified Jan 2026)
        # =====================================================================
        {
            "id": "qwen3",
            "name": "Qwen3",
            "category": "llm_local",
            "release_date": "2026-01-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 local LLM, beats DeepSeek-V3 and Llama 4 on MMLU/BBH, hybrid thinking mode",
                "why_sota": "New benchmark leader with innovative hybrid reasoning that adapts to task complexity",
                "strengths": ["Benchmark scores", "Hybrid reasoning", "Efficiency", "Multilingual"],
                "use_cases": ["General assistant", "Complex reasoning", "Multilingual tasks", "Research"]
            }
        },
        {
            "id": "llama3.3-70b",
            "name": "Llama 3.3-70B",
            "category": "llm_local",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 2,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 local LLM, GPT-4 class performance, 40GB GGUF, runs on 64GB MacBook or dual RTX 4090",
                "why_sota": "Best balance of capability and deployment flexibility, Meta's most capable open model",
                "strengths": ["GPT-4 class", "Instruction following", "Safety", "Wide deployment support"],
                "use_cases": ["Enterprise deployments", "Safe assistant", "General purpose", "MacBook Pro M3 Max"],
                "vram": "40GB"
            }
        },
        {
            "id": "deepseek-v3",
            "name": "DeepSeek-V3",
            "category": "llm_local",
            "release_date": "2025-12-25",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 3,
            "sota_rank_open": 3,
            "metrics": {
                "notes": "#3 local LLM, 671B MoE (37B active), 78% MMLU-Pro, cheapest API at $0.07/M tokens",
                "why_sota": "Most efficient MoE architecture, GPT-4 quality at 1/10th the cost",
                "strengths": ["Cost efficiency", "MoE architecture", "Code generation", "Math/reasoning"],
                "use_cases": ["Cost-sensitive deployments", "Code generation", "Math problems", "API fallback"],
                "vram": "37GB active"
            }
        },
        {
            "id": "qwen2.5-72b",
            "name": "Qwen2.5-72B",
            "category": "llm_local",
            "release_date": "2025-09-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 4,
            "sota_rank_open": 4,
            "metrics": {
                "notes": "#4 local LLM, excellent math/reasoning, 41GB GGUF Q4, strong Chinese support",
                "why_sota": "Best for mathematical reasoning and Chinese language tasks",
                "strengths": ["Math reasoning", "Chinese language", "Long context", "Instruction following"],
                "use_cases": ["Math tutoring", "Chinese content", "Academic research", "Data analysis"],
                "vram": "41GB"
            }
        },
        {
            "id": "qwen2.5-32b",
            "name": "Qwen2.5-32B",
            "category": "llm_local",
            "release_date": "2025-09-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 5,
            "sota_rank_open": 5,
            "metrics": {
                "notes": "#5 local LLM, best quality/speed balance, 19GB GGUF Q4, fits RTX 4090/3090",
                "why_sota": "Sweet spot for single high-end consumer GPU with excellent quality",
                "strengths": ["Single GPU", "Good quality", "Fast inference", "RTX 4090 optimal"],
                "use_cases": ["Personal assistant", "RTX 4090 builds", "Interactive use", "Balanced workloads"],
                "vram": "19GB"
            }
        },
        {
            "id": "qwen2.5-7b",
            "name": "Qwen2.5-7B",
            "category": "llm_local",
            "release_date": "2025-09-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 6,
            "sota_rank_open": 6,
            "metrics": {
                "notes": "#6 local LLM, best small model, 4.4GB GGUF Q4, runs on laptops and mobile",
                "why_sota": "Best quality in the 7B class, optimal for resource-constrained deployments",
                "strengths": ["Small footprint", "Fast", "Low VRAM", "Edge deployment"],
                "use_cases": ["Laptops", "Edge devices", "Quick tasks", "Prototyping", "RTX 3060/4060"],
                "vram": "4.4GB"
            }
        },

        # =====================================================================
        # API LLMs (closed source)
        # =====================================================================
        {
            "id": "claude-opus-4.5",
            "name": "Claude Opus 4.5",
            "category": "llm_api",
            "release_date": "2025-11-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 1,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 API LLM for complex reasoning, agentic tasks, and nuanced writing (Anthropic)",
                "why_sota": "Best at multi-step reasoning, code understanding, and maintaining context in long conversations",
                "strengths": ["Complex reasoning", "Code generation", "Long context retention", "Agentic workflows"],
                "use_cases": ["Software engineering", "Research assistance", "Complex analysis", "Agentic coding"]
            }
        },
        {
            "id": "gpt-4.5",
            "name": "GPT-4.5",
            "category": "llm_api",
            "release_date": "2025-10-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 2,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#2 API LLM, strongest multimodal (vision, audio, image gen), OpenAI ecosystem",
                "why_sota": "Best integrated multimodal experience with vision, audio, and generation in one model",
                "strengths": ["Multimodal", "Vision", "Audio", "Image generation", "Ecosystem"],
                "use_cases": ["Multimodal apps", "Vision analysis", "Content creation", "ChatGPT plugins"]
            }
        },
        {
            "id": "gemini-2.0-pro",
            "name": "Gemini 2.0 Pro",
            "category": "llm_api",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 3,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#3 API LLM, 1M+ token context, best for document analysis and research (Google)",
                "why_sota": "Largest context window, best for processing entire codebases or document collections",
                "strengths": ["1M+ context", "Document analysis", "Research", "Google integration"],
                "use_cases": ["Large document analysis", "Codebase review", "Research synthesis", "Book analysis"]
            }
        },
        {
            "id": "grok-4.1",
            "name": "Grok 4.1",
            "category": "llm_api",
            "release_date": "2025-11-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 4,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#4 API LLM, #1 LMArena Elo (1483), real-time X/Twitter data, uncensored (xAI)",
                "why_sota": "Highest human preference scores, real-time information access, fewer content restrictions",
                "strengths": ["Human preference", "Real-time data", "Uncensored", "X integration"],
                "use_cases": ["Current events", "Social analysis", "Less filtered responses", "Real-time research"]
            }
        },

        # =====================================================================
        # CODING LLMs (NEW CATEGORY)
        # =====================================================================
        {
            "id": "qwen3-coder",
            "name": "Qwen3-Coder",
            "category": "llm_coding",
            "release_date": "2026-01-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 open-source coder, 262K native context (1M with YaRN), beats GPT-4 on HumanEval",
                "why_sota": "Largest code context window in open-source, excellent at multi-file understanding",
                "strengths": ["262K context", "Multi-file projects", "Codebase understanding", "HumanEval leader"],
                "use_cases": ["Large codebase work", "Refactoring", "Code review", "IDE integration"]
            }
        },
        {
            "id": "deepseek-v3-coder",
            "name": "DeepSeek-V3",
            "category": "llm_coding",
            "release_date": "2025-12-25",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 2,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 open-source coder, 78% MMLU-Pro CS, cheapest capable coding model at $0.07/M tokens",
                "why_sota": "Best cost/performance for code generation, strong at algorithmic problems",
                "strengths": ["Cost efficiency", "Algorithms", "Math/CS", "API availability"],
                "use_cases": ["Budget coding assistant", "LeetCode-style problems", "Algorithm design", "API coding"]
            }
        },
        {
            "id": "claude-opus-4.5-coding",
            "name": "Claude Opus 4.5",
            "category": "llm_coding",
            "release_date": "2025-11-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 3,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 closed-source coder, best at complex multi-step code reasoning and agentic coding",
                "why_sota": "Unmatched at understanding complex codebases and making coordinated multi-file changes",
                "strengths": ["Complex reasoning", "Multi-file edits", "Agentic coding", "Code explanation"],
                "use_cases": ["Claude Code CLI", "Complex refactoring", "Architecture decisions", "Code review"]
            }
        },
        {
            "id": "cursor-claude",
            "name": "Cursor (Claude-based)",
            "category": "llm_coding",
            "release_date": "2025-12-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 4,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#2 closed-source coder, IDE-integrated with Claude, best autocomplete and inline editing",
                "why_sota": "Best IDE integration with context-aware autocomplete and inline code editing",
                "strengths": ["IDE integration", "Autocomplete", "Inline editing", "Context awareness"],
                "use_cases": ["VS Code replacement", "Real-time coding assistance", "Autocomplete", "Quick edits"]
            }
        },

        # =====================================================================
        # TTS
        # =====================================================================
        {
            "id": "chatterbox-tts",
            "name": "ChatterboxTTS",
            "category": "tts",
            "release_date": "2025-06-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 open-source TTS, most natural prosody and emotion, runs locally",
                "why_sota": "Best naturalness in open-source, handles emotion and emphasis well",
                "strengths": ["Natural prosody", "Emotion", "Local deployment", "Fast inference"],
                "use_cases": ["Audiobooks", "Voice assistants", "Content creation", "Accessibility"]
            }
        },
        {
            "id": "f5-tts",
            "name": "F5-TTS",
            "category": "tts",
            "release_date": "2025-08-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 2,
            "sota_rank_open": 2,
            "metrics": {
                "notes": "#2 open-source TTS, best voice cloning from short samples (3-10s reference audio)",
                "why_sota": "Highest quality voice cloning with minimal reference audio needed",
                "strengths": ["Voice cloning", "Short reference audio", "Quality", "Multilingual"],
                "use_cases": ["Voice cloning", "Personalized TTS", "Character voices", "Dubbing"]
            }
        },
        {
            "id": "elevenlabs",
            "name": "ElevenLabs",
            "category": "tts",
            "release_date": "2025-01-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 3,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 commercial TTS, best overall quality, instant voice cloning, many languages",
                "why_sota": "Highest quality output, best voice cloning, widest language support",
                "strengths": ["Quality", "Voice cloning", "Languages", "API ease"],
                "use_cases": ["Professional production", "Multilingual content", "Voice cloning", "Enterprise"]
            }
        },

        # =====================================================================
        # STT
        # =====================================================================
        {
            "id": "whisper-large-v3",
            "name": "Whisper Large v3",
            "category": "stt",
            "release_date": "2024-11-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 STT, best accuracy across languages, OpenAI open-weights, runs locally",
                "why_sota": "Lowest word error rate, handles accents/noise well, 99 languages",
                "strengths": ["Accuracy", "99 languages", "Noise robustness", "Local deployment"],
                "use_cases": ["Transcription", "Meeting notes", "Subtitle generation", "Voice commands"]
            }
        },

        # =====================================================================
        # MUSIC
        # =====================================================================
        {
            "id": "suno-v4",
            "name": "Suno v4",
            "category": "music",
            "release_date": "2025-09-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 1,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#1 music generation, best vocal quality and song structure, full songs with lyrics",
                "why_sota": "Most realistic vocals, best at maintaining song structure and coherence",
                "strengths": ["Vocal quality", "Song structure", "Lyrics", "Genre variety"],
                "use_cases": ["Full song creation", "Background music", "Content creators", "Prototyping"]
            }
        },
        {
            "id": "udio",
            "name": "Udio",
            "category": "music",
            "release_date": "2025-06-01",
            "is_sota": True,
            "is_open_source": False,
            "sota_rank": 2,
            "sota_rank_open": None,
            "metrics": {
                "notes": "#2 music generation, best for instrumentals and electronic music, high fidelity audio",
                "why_sota": "Superior instrumental quality, better for electronic/EDM genres",
                "strengths": ["Instrumentals", "Electronic music", "Audio fidelity", "Production quality"],
                "use_cases": ["Instrumentals", "EDM", "Background tracks", "Sound design"]
            }
        },

        # =====================================================================
        # EMBEDDINGS
        # =====================================================================
        {
            "id": "bge-m3",
            "name": "BGE-M3",
            "category": "embeddings",
            "release_date": "2024-06-01",
            "is_sota": True,
            "is_open_source": True,
            "sota_rank": 1,
            "sota_rank_open": 1,
            "metrics": {
                "notes": "#1 embeddings, multilingual (100+ langs), hybrid dense+sparse+ColBERT retrieval",
                "why_sota": "Best retrieval quality with hybrid approach, works across languages",
                "strengths": ["Multilingual", "Hybrid retrieval", "Dense+Sparse", "ColBERT support"],
                "use_cases": ["RAG systems", "Semantic search", "Multilingual search", "Document retrieval"]
            }
        },
    ]

    for model in models:
        db.execute("""
            INSERT OR REPLACE INTO models
            (id, name, category, release_date, is_sota, is_open_source, sota_rank, sota_rank_open, metrics, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual')
        """, (
            model["id"],
            model["name"],
            model["category"],
            model["release_date"],
            model["is_sota"],
            model.get("is_open_source", True),
            model["sota_rank"],
            model.get("sota_rank_open"),
            json.dumps(model.get("metrics", {}))
        ))


def main():
    """Initialize the database."""
    print(f"Initializing database at {DB_PATH}")

    # Remove existing database for fresh start
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Removed existing database")

    db = sqlite3.connect(str(DB_PATH))

    print("Creating schema...")
    create_schema(db)

    print("Seeding categories...")
    seed_categories(db)

    print("Seeding SOTA models...")
    seed_sota_models(db)

    db.commit()

    # Print stats
    model_count = db.execute("SELECT COUNT(*) FROM models").fetchone()[0]
    open_count = db.execute("SELECT COUNT(*) FROM models WHERE is_open_source = 1").fetchone()[0]
    closed_count = db.execute("SELECT COUNT(*) FROM models WHERE is_open_source = 0").fetchone()[0]

    db.close()

    print(f"\nDatabase initialized successfully!")
    print(f"  Total models: {model_count}")
    print(f"  Open-source: {open_count}")
    print(f"  Closed-source: {closed_count}")
    print(f"  Size: {DB_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
