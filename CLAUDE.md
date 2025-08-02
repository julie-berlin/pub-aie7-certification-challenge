# Federal Ethics Compliance Chatbot - Project Memory

## Project Overview

**Problem**: Federal employees and contractors need guidance on ethics violations they may have witnessed or committed, including potential penalties, corrective actions, and reporting procedures.

**Solution**: An agentic RAG chatbot that combines federal ethics law knowledge with real-time web search to provide comprehensive ethics compliance guidance.

## Architecture

### Tech Stack
- **LLM**: GPT-4o (primary reasoning), GPT-4o-mini (lightweight tasks)
- **Embedding Model**: text-embedding-3-small (cost-effective, 1536 dimensions)
- **Orchestration**: LangGraph (multi-step agent workflows)
- **Vector Database**: Qdrant (local development, scalable to cloud)
- **Web Search**: Tavily (government domain filtering, citations)
- **Monitoring**: LangSmith (tracing, evaluation, debugging)
- **Frontend**: React (planned)
- **Backend**: FastAPI (planned)
- **Deployment**: Docker Compose

### Data Sources
- **Primary**: Compilation of Federal Ethics Laws (2025).pdf (190 pages)
- **Secondary**: Real-time web search for current guidance and precedents
- **Domains**: osg.gov, oge.gov, ethics.gov, gsa.gov (filtered for reliability)

### Agentic Workflow
1. **User Context Collection** - Role, industry, seniority level
2. **Question Analysis** - Ethics violation identification
3. **Knowledge Retrieval** - Federal law RAG search
4. **Search Planning** - Targeted web query formulation
5. **Web Research** - Current guidance and cases
6. **Violation Analysis** - Specific law identification and factors
7. **Severity Assessment** - Minor/moderate/serious classification
8. **Penalty Research** - Criminal, civil, administrative consequences
9. **Final Guidance** - Actionable steps and reporting requirements

## Key Features
- Multi-source knowledge synthesis (federal law + web)
- Context-aware guidance based on user role
- Step-by-step ethical reasoning with citations
- Specific penalty and consequence information
- Actionable corrective guidance

## Development Commands

### Setup
```bash
uv sync  # Install dependencies
docker-compose up  # Start services (when implemented)
```

### Testing
```bash
python3 -m pytest tests/  # Unit tests (when implemented)
jupyter notebook docs/poc_app.ipynb  # Run POC
```

### Evaluation
```bash
# RAGAS evaluation (when implemented)
python3 scripts/evaluate_ragas.py

# LangSmith testing (when implemented)
python3 scripts/langsmith_eval.py
```

## Current Status
- ✅ POC notebook with basic and advanced agentic reasoning
- ✅ Federal ethics law RAG pipeline
- ✅ Web search integration
- ✅ Multi-step violation assessment
- 🔄 Full-stack application (planned)
- 🔄 RAGAS evaluation framework (planned)
- 🔄 Advanced retrieval optimization (planned)

## Known Issues
- Web search requires Tavily API key configuration
- In-memory Qdrant loses data on restart (production needs persistent storage)
- No user authentication or session management yet

## Performance Notes
- Current chunking: 750 characters with tiktoken counting
- Retrieval: Top-5 similarity search
- Response time: ~10-15 seconds for complex scenarios
- Context window: Efficiently managed with targeted retrieval

## Evaluation Metrics (Planned)
- **RAGAS**: Faithfulness, answer relevance, context precision, context recall
- **Custom**: Legal accuracy, actionability, citation quality
- **User**: Response time, satisfaction, task completion

## Security Considerations
- No storage of sensitive user information
- Government domain filtering for reliable sources
- Citation verification for legal accuracy
- Disclaimer: Not a substitute for legal counsel