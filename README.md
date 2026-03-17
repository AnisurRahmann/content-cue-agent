# ContentCued Marketing Agent

A production multi-agent LangGraph system for cross-platform marketing campaign generation with **tiered LLM routing for cost optimization**.

## 🎯 Overview

ContentCued generates complete marketing campaigns from a single brief using 6 specialized AI agents. The system intelligently routes LLM calls across 3 tiers to minimize costs while maintaining quality.

**Key Features:**
- 🤖 **6 Specialized Agents** - Orchestrator, Copy, Visual, Adapter, Quality, Blog
- 💰 **Tiered LLM Routing** - Reduces costs by ~84% vs. all-Tier-3 approach
- 📱 **Cross-Platform** - Facebook, Instagram, LinkedIn, WhatsApp, Blog
- 🎨 **AI Image Generation** - Ideogram integration with placeholder fallback
- 📊 **RAG-Powered** - ChromaDB for product and brand context
- 👤 **Human-in-the-Loop** - Review and approve before publishing
- 🎯 **Bangla-Optimized** - Natural Bangla/English mixing per platform

## 📊 LLM Cost Architecture

Every LLM call is routed to the appropriate tier:

| Tier | Model | Use Case | % of Calls | Target Cost |
|------|-------|----------|------------|-------------|
| **TIER 1** | Groq Llama 3.3 70B (Free) | Routing, classification, formatting | 70-80% | $0/call |
| **TIER 2** | DeepSeek V3 ($0.28/MTok) | Content generation, drafts | 15-25% | <$0.01/call |
| **TIER 3** | Claude Sonnet 4 ($3-15/MTok) | Final polish (rare) | ≤5% | <$0.05/call |

**Cost Optimization:**
- All platform copy generated in **ONE** Tier 2 call
- Prompt caching for system prompts
- Fallback chain: Tier 1 → Tier 2 → Tier 3
- Cost tracking on every call with campaign reports

## 🏗️ Architecture

```
Brief → Orchestrator → Copy Agent → [Blog Agent?] → Visual Agent
                              → Adapter Agent → Quality Agent
                              → Human Review (INTERRUPT)
                              → [Approve/Reject]
                              → Save Campaign
```

### Agents

1. **Orchestrator (TIER 1)** - Parse brief, classify campaign, retrieve RAG context
2. **Copy Agent (TIER 2)** - Generate ALL platform copy in one call
3. **Visual Agent (TIER 1)** - Generate image prompts + Ideogram images
4. **Adapter Agent (TIER 1)** - Format, validate, add metadata
5. **Quality Agent (TIER 1)** - Brand compliance validation
6. **Blog Agent (TIER 2)** - SEO blog post generation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd contentcued-agent

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` with your API keys:

```bash
# Tier 1 (Free) - Required
GROQ_API_KEY=gsk_your_key_here

# Tier 2 (Cheap) - Optional (falls back to Tier 1)
DEEPSEEK_API_KEY=sk_your_key_here

# Tier 3 (Quality) - Optional (falls back to Tier 2)
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Image Generation - Optional
IDEOGRAM_API_KEY=your_key_here
```

**Minimum Required:** Only `GROQ_API_KEY` is needed to run the system (free mode).

### 3. Index Data

```bash
python scripts/index_data.py
```

This indexes products and brand guidelines into ChromaDB.

### 4. Run Campaigns

**CLI Mode:**
```bash
python scripts/run_campaign.py
```

**Dashboard:**
```bash
streamlit run dashboard/app.py
```

**API:**
```bash
uvicorn api.main:app --reload
```

## 📁 Project Structure

```
contentcued-agent/
├── data/
│   ├── products.json              # 10 products
│   └── brand_guidelines.md        # Brand voice & rules
├── src/
│   ├── llm_router.py              # ⭐ Tiered routing + cost tracking
│   ├── state.py                   # CampaignState schema
│   ├── agents/                    # All 6 agents
│   ├── tools/                     # RAG, images, files
│   ├── graph/                     # LangGraph workflow
│   └── rag/                       # ChromaDB indexer/retriever
├── dashboard/                     # Streamlit UI
├── api/                           # FastAPI backend
├── scripts/                       # CLI tools
└── outputs/                       # Generated campaigns
```

## 💡 Usage Examples

### Create Campaign Brief

```python
brief = {
    "product_slug": "chatgpt-plus",
    "audience": "Developers and content creators",
    "platforms": ["facebook", "instagram", "linkedin", "whatsapp"],
    "tone": "exciting",
    "instructions": "Focus on instant activation benefit"
}
```

### Run via Python

```python
from src.state import initial_state
from src.graph.workflow import create_campaign_app

state = initial_state(brief)
app = create_campaign_app()

config = {"configurable": {"thread_id": "my_campaign"}}
result = app.invoke(state, config=config)
```

## 🧪 Testing

```bash
# Test individual agents
python scripts/test_agents.py

# Test specific components
pytest tests/test_llm_router.py
pytest tests/test_copy_agent.py
pytest tests/test_graph.py
```

## 📊 Cost Tracking

Every campaign generates a cost report:

```
╔══════════════════════════════════════════╗
║      CAMPAIGN COST REPORT                 ║
╚══════════════════════════════════════════╝

┌─────────────────────────────────────┐
│        Cost Summary by Tier          │
├──────────┬───────┬─────────┬────────┤
│ Tier     │ Calls │ Tokens  │ Cost   │
├──────────┼───────┼─────────┼────────┤
│ TIER 1   │ 15    │ 45,230  │ $0.00  │
│ TIER 2   │ 3     │ 8,450   │ $0.28  │
│ TIER 3   │ 0     │ 0       │ $0.00  │
└──────────┴───────┴─────────┴────────┘

Total Cost: $0.28
✓ Used 15 free Tier 1 calls
```

## 🎨 Platform-Specific Content

The system generates platform-appropriate content:

- **Facebook:** Bangla-heavy (60-70%), emojis, <300 chars, WhatsApp CTA
- **Instagram:** 50-50 Bangla/English, 10-15 hashtags, aesthetic tone
- **LinkedIn:** Professional English, <1300 chars, website CTA
- **WhatsApp:** Bangla-first, brief, bKash payment info

## 🛠️ Development

### Docker Development

**Start development environment with automatic port selection:**
```bash
./dev.sh
```

This script automatically detects if the default ports (8000, 3000) are in use and finds available alternatives. It will display which ports are being used before starting the containers.

**Manual port control:**
```bash
# Set custom ports manually
BACKEND_PORT=8080 FRONTEND_PORT=3001 docker-compose -f docker-compose.dev.yml up --build
```

**Stop containers:**
```bash
docker-compose -f docker-compose.dev.yml down
```

### Add New Product

Edit `data/products.json`:

```json
{
  "slug": "new-product",
  "name": "New Product",
  "category": "AI Tools",
  "price_bdt": 3000,
  "description": "...",
  "features": [...],
  "target_audience": "...",
  "whatsapp_number": "8801XXXXXXXXX"
}
```

Re-index: `python scripts/index_data.py`

### Add New Agent

1. Create agent in `src/agents/`
2. Follow pattern: use `get_tracked_llm(task_type)`
3. Add node to `src/graph/workflow.py`
4. Update routing in `src/graph/routing.py`

## 📝 API Endpoints

```bash
# Create campaign
POST /api/v1/campaigns
Body: {brief: {...}}

# List campaigns
GET /api/v1/campaigns

# Get campaign details
GET /api/v1/campaigns/{id}

# Submit review
PUT /api/v1/campaigns/{id}/review
Body: {decisions: {...}}

# Get cost breakdown
GET /api/v1/campaigns/{id}/cost
```

## ⚠️ Brand Safety Rules

The system enforces:
- ✅ BDT pricing prominently displayed
- ✅ WhatsApp CTA on FB/IG posts
- ✅ Bangla/English mixing per platform
- ❌ NEVER mentions G2A, reselling, keys, cracks

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Ensure cost tracking is maintained
5. Submit PR

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LangGraph** - Multi-agent orchestration framework
- **Groq** - Free Tier 1 LLM hosting
- **DeepSeek** - Cost-effective Tier 2 model
- **ChromaDB** - Vector database for RAG

---

**Built with ❤️ by ContentCued**

*Global AI, Local Access*
