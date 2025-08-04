# FastAPI Backend Setup & Documentation

## ✅ Current Status

**COMPLETED**: Full FastAPI backend with parallel agentic workflow

### 🏗️ Architecture

**Modular Service Design** (no global instances):
- `PlanningAgentService` - Research strategy with GPT-4o-mini
- `EthicsAssessmentService` - Comprehensive analysis with GPT-4o
- `DocumentLoaderService` - PDF loading with tiktoken chunking
- `VectorStoreService` - Qdrant vector database operations
- `WebSearchService` - Parallel Tavily web searches
- `AgenticWorkflowService` - LangGraph workflow orchestration

**Configuration Management**:
- YAML config files in `api/config/`
- Environment variable override support
- Path-aware configuration loading

**Parallel Agentic Workflow**:
```
collect_context → create_plan → retrieve_knowledge
                                        ↓
        🔥 PARALLEL: search_general | search_penalties | search_guidance
                                        ↓
        combine_results → assess_violation → finalize
```

### 📁 Project Structure

```
api/
├── config/                   # YAML configuration files
│   ├── agentic_workflow.yaml # Workflow parameters
│   ├── ai_models.yaml        # LLM configuration
│   ├── application.yaml      # API and security settings
│   ├── data_processing.yaml  # Document processing
│   ├── golden_dataset.yaml   # Test dataset settings
│   └── vector_database.yaml  # Qdrant settings
├── app/
│   ├── core/
│   │   ├── config_loader.py  # YAML config loading
│   │   └── settings.py       # Centralized settings
│   ├── models/
│   │   ├── chat_models.py    # Pydantic request/response models
│   │   └── state_models.py   # LangGraph state definitions
│   ├── services/             # Business logic services
│   │   ├── advanced_retriever_service.py
│   │   ├── agentic_workflow_service.py
│   │   ├── document_loader_service.py
│   │   ├── document_upload_service.py
│   │   ├── ethics_assessment_service.py
│   │   ├── planning_agent_service.py
│   │   ├── startup_service.py
│   │   ├── vector_store_service.py
│   │   └── web_search_service.py
│   ├── routers/
│   │   ├── chat_router.py    # API endpoints
|   |   └── document_router.py
│   ├── utils/
│   │   └── startup_utils.py  # Environment validation
│   └── main.py               # FastAPI application
├── run_server.py             # Server startup script
└── test_api.py               # API test suite
```

### 🔌 API Endpoints

**Main Endpoints**:
- `POST /api/chat` - Ethics consultation with full agentic workflow
- `POST /api/documents/upload` - Add user document
- `GET /api/documents/list` - Get list of uploaded documents
- `GET /api/documents/{id}` - Get uploaded document with {id}
- `DELETE /api/documents/{id}` - Delete a user added document with {id}
- `GET /api/health` - Service health check with component status
- `GET /api/ping` - Simple connectivity test

**Request Format**:
```json
{
  "question": "Ethics question or scenario",
  "user_context": {
    "role": "federal_employee",
    "agency": "GSA",
    "seniority": "GS-14",
    "clearance": "secret"
  },
}
```

**Response Format**:
```json
{
  "question": "Original question",
  "response": "Comprehensive ethics guidance",
  "federal_law_sources": 5,
  "web_sources": 9,
  "search_results": [...],
  "processing_time_seconds": 8.5,
  "search_plan": "Research strategy used"
}
```

### ⚡ Performance Features

**Parallel Web Search**: 3x speed improvement
- `search_general`: OGE guidance and general ethics
- `search_penalties`: Criminal, civil, administrative penalties
- `search_guidance`: Current guidance and precedent cases

**Multi-Model Approach**:
- GPT-4o-mini for planning (cost-effective, fast)
- GPT-4o for assessment (high quality)

**Smart Configuration**:
- Path-aware config loading (works from any directory)
- Environment variable overrides
- Validation and error handling

### 🚀 Setup Instructions

**1. Install Dependencies**:
```bash
uv sync
```

**2. Environment Variables** (create `.env.local`):
```bash
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
LANGCHAIN_API_KEY=your_langsmith_key
```

**3. Start Server** (from project root):
```bash
python3 start_backend.py
```

**4. Test API**:
```bash
python3 api/test_api.py
```

**5. Access Documentation**:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### 🔧 Configuration

**Key Configuration Files**:
- `application.yaml` - API settings, CORS, environment
- `ai_models.yaml` - Model selection, parameters
- `vector_database.yaml` - Qdrant configuration
- `agentic_workflow.yaml` - Timeout settings, parallel config

**Environment Override Example**:
```bash
export OPENAI_MODEL="gpt-4o-mini"  # Override default model
export QDRANT_URL="http://production-qdrant:6333"
```
