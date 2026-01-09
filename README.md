# SOTA Tracker

**The definitive open-source database of State-of-the-Art AI models.**

Auto-updated daily from [LMArena](https://lmarena.ai), [Artificial Analysis](https://artificialanalysis.ai), and [HuggingFace](https://huggingface.co).

## Why This Exists

AI models are released weekly. Keeping track is impossible. This project:

1. **Scrapes authoritative sources** - LMArena Elo rankings, Artificial Analysis benchmarks
2. **Updates daily** via GitHub Actions
3. **Exports to JSON/CSV** - Use in your own projects
4. **Provides an MCP server** - Claude/AI assistants can query directly

## Quick Start: Use the Data

### Option 1: Download JSON/CSV

```bash
# Latest data (updated daily)
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/sota-tracker-mcp/main/data/sota_export.json
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/sota-tracker-mcp/main/data/sota_export.csv
```

### Option 2: Clone and Query Locally

```bash
git clone https://github.com/YOUR_USERNAME/sota-tracker-mcp.git
cd sota-tracker-mcp

# Query with sqlite3
sqlite3 data/sota.db "SELECT name, sota_rank FROM models WHERE category='llm_api' ORDER BY sota_rank LIMIT 10"
```

### Option 3: Use with Claude (MCP)

```bash
# Install as MCP server
claude mcp add --transport stdio --scope user sota-tracker \
  -- python ~/sota-tracker-mcp/server.py

# Now Claude can query SOTA data directly!
```

## Data Sources

| Source | Data | Update Frequency |
|--------|------|------------------|
| [LMArena](https://lmarena.ai/leaderboard) | LLM Elo rankings (6M+ human votes) | Daily |
| [Artificial Analysis](https://artificialanalysis.ai) | LLM benchmarks, pricing, speed | Daily |
| [HuggingFace](https://huggingface.co) | Model downloads, trending | Daily |
| Manual curation | Video, Image, Audio models | As needed |

## Categories

| Category | Description | Top Models (Jan 2026) |
|----------|-------------|----------------------|
| `llm_api` | Cloud LLM APIs | Gemini 3 Pro, Grok 4.1, Claude Opus 4.5 |
| `llm_local` | Local LLMs (GGUF) | Qwen3, Llama 3.3, DeepSeek-V3 |
| `llm_coding` | Code-focused LLMs | Qwen3-Coder, DeepSeek-V3 |
| `image_gen` | Image generation | GPT Image 1.5, Z-Image-Turbo |
| `video` | Video generation | Veo 3.1, LTX-2 |
| `tts` | Text-to-speech | ChatterboxTTS, ElevenLabs |
| `stt` | Speech-to-text | Whisper Large v3 |
| `embeddings` | Vector embeddings | BGE-M3 |

## MCP Tools

When installed as an MCP server, Claude can use these tools:

| Tool | Description |
|------|-------------|
| `query_sota(category)` | Get current SOTA for a category |
| `check_freshness(model)` | Check if a model is current or outdated |
| `get_forbidden()` | List outdated models to avoid |
| `compare_models(a, b)` | Compare two models side-by-side |
| `recent_releases(days)` | Models released in past N days |
| `refresh_data()` | Force refresh from sources |
| `cache_status()` | Check data freshness |

## Run Your Own Scraper

```bash
# Install dependencies
pip install -r requirements.txt
pip install playwright
playwright install chromium

# Run all scrapers
python scrapers/run_all.py --export

# Output:
# data/sota_export.json
# data/sota_export.csv
# data/lmarena_latest.json
```

## GitHub Actions (Auto-Update)

This repo uses GitHub Actions to:
- **Daily**: Scrape all sources, update database, commit changes
- **Weekly**: Create a tagged release with JSON/CSV exports

To enable on your fork:
1. Fork this repo
2. Go to Settings → Actions → Enable workflows
3. Data will auto-update daily at 6 AM UTC

## File Structure

```
sota-tracker-mcp/
├── server.py                    # MCP server
├── init_db.py                   # Database initialization
├── requirements.txt             # Dependencies
├── data/
│   ├── sota.db                  # SQLite database
│   ├── sota_export.json         # Full JSON export
│   ├── sota_export.csv          # CSV export
│   ├── lmarena_latest.json      # Raw LMArena data
│   └── forbidden.json           # Outdated models list
├── scrapers/
│   ├── lmarena.py               # LMArena scraper (Playwright)
│   ├── artificial_analysis.py   # AA scraper (Playwright)
│   └── run_all.py               # Unified runner
├── fetchers/
│   ├── huggingface.py           # HuggingFace API
│   └── cache_manager.py         # Smart caching
└── .github/workflows/
    └── daily-scrape.yml         # GitHub Actions workflow
```

## Contributing

Found a model that's missing or incorrectly ranked?

1. **For manual additions**: Edit `init_db.py` and submit a PR
2. **For scraper improvements**: Edit files in `scrapers/`
3. **For new data sources**: Add a new scraper and update `run_all.py`

## API Endpoints (Coming Soon)

Planning to add a simple REST API:
- `GET /api/v1/models?category=llm_api`
- `GET /api/v1/models/:id`
- `GET /api/v1/rankings?source=lmarena`

## Data Attribution & Legal

This project aggregates **publicly available benchmark data** from third-party sources. We do not claim ownership of rankings, Elo scores, or benchmark results.

### Data Sources (Used With Permission)

| Source | Data | Permission |
|--------|------|------------|
| [LMArena](https://lmarena.ai) | Chatbot Arena Elo rankings | `robots.txt: Allow: /` |
| [Artificial Analysis](https://artificialanalysis.ai) | LLM quality benchmarks | `robots.txt: Allow: /` (explicitly allows AI crawlers) |
| [HuggingFace](https://huggingface.co) | Model metadata, downloads | Public API |
| [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) | Open-source LLM benchmarks | CC-BY license |

### Disclaimer

- All benchmark scores and rankings are the intellectual work of their respective sources
- This project provides aggregation and tooling, not original benchmark data
- Data is scraped once daily to minimize server load
- If you are a data source and wish to be excluded, please open an issue

### Fair Use

This project:
- Aggregates factual data (not copyrightable)
- Adds value through tooling (MCP server, unified format)
- Attributes all sources with links
- Does not compete commercially with sources
- Respects robots.txt permissions

## License

MIT - See [LICENSE](LICENSE) for details.

The **code** in this repository is MIT licensed. The **data** belongs to its respective sources (see attribution above).
