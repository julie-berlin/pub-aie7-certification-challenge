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
- Simplified assessment format with severity color-coding
- Expandable detailed analysis (6 structured aspects)
- Direct answer identification and actionable next steps
- Document upload capability for custom policies
- Step-by-step ethical reasoning with citations
- Specific penalty and consequence information
- Downloadable comprehensive assessment reports

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
- ✅ Full-stack application (FastAPI + Next.js)
- ✅ Document upload and management system
- ✅ Simplified assessment UI with expandable detailed sections
- ✅ Severity color-coding and actionable guidance
- ✅ Docker deployment with proper service integration
- ✅ Production-ready document loading and vector store connectivity
- ✅ RAGAS evaluation framework with comprehensive test dataset
- ✅ Structured logging with FastAPI best practices
- 🔄 Advanced retrieval optimization (planned)

## Known Issues
- Web search requires Tavily API key configuration
- In-memory Qdrant loses data on restart (production needs persistent storage)
- No user authentication or session management yet
- Document deletion from vector store requires additional Qdrant cleanup

## Pending Improvements
- Include original scenario and user context in downloadable reports
- Use comprehensive traditional response format for detailed downloadable reports
- Enhanced mobile responsiveness for assessment cards
- Improved report formatting and organization

## Performance Notes
- Current chunking: 750 characters with tiktoken counting
- Retrieval: Top-5 similarity search
- Response time: ~10-15 seconds for complex scenarios
- Context window: Efficiently managed with targeted retrieval
- Assessment generation: Structured JSON parsing with fallback handling
- UI responsiveness: Real-time expandable sections and color-coded severity

## Evaluation Metrics (Implemented)
- **RAGAS**: Faithfulness, answer relevancy, context precision, context recall, answer correctness, answer similarity
- **Test Dataset**: 12 comprehensive federal ethics scenarios with ground truth
- **Automated Evaluation**: Full pipeline with structured reporting
- **Performance Tracking**: Integration with LangSmith for monitoring
- **Custom Metrics (Planned)**: Legal accuracy, actionability, citation quality
- **User Metrics (Planned)**: Response time, satisfaction, task completion

## RAGAS Evaluation
```bash
# Run comprehensive evaluation
python3 eval/scripts/run_ragas_evaluation.py

# Results saved to timestamped files:
# - eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.json
# - eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.csv
```

## Security Considerations
- No storage of sensitive user information
- Government domain filtering for reliable sources
- Citation verification for legal accuracy
- Disclaimer: Not a substitute for legal counsel