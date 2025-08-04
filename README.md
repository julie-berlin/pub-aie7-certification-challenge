# IntegriBot - Federal Ethics Compliance Chatbot

**An intelligent agentic RAG system that provides federal employees with instant, comprehensive ethics compliance guidance.**

STAGE: Proof of Concept

## 🎯 What It Does

IntegriBot helps federal employees navigate complex ethics regulations by:
- **Analyzing ethics scenarios** with multi-step AI reasoning
- **Providing instant guidance** on violations, penalties, and reporting procedures
- **Combining federal law knowledge** with real-time web search for current guidance
- **Offering structured assessments** with severity ratings and actionable next steps
- **Supporting document uploads** to integrate agency-specific policies

## 🚀 Key Features

- **Advanced Retrieval Strategies**: MMR and semantic search for comprehensive coverage
- **Real-time Processing**: Streaming responses with live processing indicators
- **Professional Interface**: Clean, government-appropriate design with role-based context
- **Document Management**: Upload and integrate custom policy documents
- **Performance Optimized**: 7.98% improvement over baseline with RAGAS evaluation
- **Production Ready**: Containerized deployment with comprehensive monitoring

## 🛠️ Tech Stack

- **LLM**: GPT-4o for reasoning, GPT-4o-mini for lightweight tasks
- **Frontend**: Next.js React with TypeScript and Tailwind CSS
- **Backend**: FastAPI with structured logging and streaming endpoints
- **Orchestration**: LangGraph for multi-step agentic workflows
- **Vector Database**: Qdrant with advanced retrieval strategies
- **Web Search**: Tavily API for real-time government source information
- **Monitoring**: LangSmith for tracing and performance evaluation
- **Deployment**: Docker Compose for local development

## 📊 Performance

**RAGAS Evaluation Results:**
- **MMR Strategy**: 0.7811 overall score (+7.98% over baseline)
- **Faithfulness**: 33% improvement in grounding accuracy
- **Response Time**: Sub-15 seconds for complex ethics scenarios
- **Context Precision**: Excellent (0.98+) regulatory document retrieval

## 🏃‍♂️ Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/pub-aie7-certification-challenge.git
cd pub-aie7-certification-challenge

# Set up environment variables
cp .env .env.local
# Edit .env.local with your API keys (OpenAI, Tavily, LangSmith)

# Start the application
docker-compose up -d

# Access the application
open http://localhost:3000
```

## 💡 Use Cases

- **Gift Acceptance**: "Can I accept this $25 gift from a contractor?"
- **Conflicts of Interest**: "Is my spouse's consulting work a conflict?"
- **Post-Employment**: "When can I work for this company after leaving government?"
- **Financial Disclosure**: "What investments must I report?"

## 📋 Project Status

✅ **Completed Tasks:**
- Multi-step agentic reasoning with LangGraph
- Advanced retrieval strategies (similarity, MMR, Cohere rerank)
- Real-time web search integration
- Document upload and processing
- Comprehensive RAGAS evaluation
- Production-ready deployment
- Performance optimization

## 📁 Repository Structure

```
├── api/                 # FastAPI backend
├── frontend/           # Next.js React frontend
├── data/              # Federal ethics documents
├── eval/              # RAGAS evaluation scripts
├── docs/              # Documentation and notebooks
├── docker-compose.yaml # Container orchestration
└── Certification_Challenge.md # Complete project documentation
```

## 🎥 Demo

A 5-minute video demonstration showcasing the complete system is available, covering:
- Live ethics scenario analysis
- Advanced retrieval strategy comparison
- Agentic workflow processing
- Performance metrics and evaluation

## 📚 Documentation

- **Complete Project Details**: [Certification_Challenge.md](./Certification_Challenge.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Architecture Diagram**: [architecture-diagram.png](./architecture-diagram.png)
- **Setup Instructions**: Follow Quick Start above or see Docker documentation

---

**Target Audience**: 3+ million federal employees requiring ethics compliance guidance
**Development Time**: ~24 hours over 5 days
**Performance**: Production-ready with quantified improvements via RAGAS evaluation
