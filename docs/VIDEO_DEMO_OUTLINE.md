# 5-Minute Video Demo Outline - Federal Ethics Chatbot

## Demo Structure (5 minutes max)

### **Opening (30 seconds)**
- **Introduction**: "Hi, I'm [Your Name] presenting IntegriBot, a Federal Ethics Compliance Chatbot"
- **Problem Statement**: "Federal employees need guidance on ethics violations with real-time penalties and reporting procedures"
- **Solution Overview**: "An agentic RAG system combining federal law knowledge with advanced retrieval strategies"

### **Architecture Overview (45 seconds)**
**Screen: Architecture diagram or code structure**
- **Tech Stack**: "Built with GPT-4o, FastAPI backend, Next.js frontend, and Qdrant vector database"
- **Key Innovation**: "Multi-strategy retrieval system with similarity, MMR, and hybrid approaches"
- **Data Sources**: "190-page federal ethics compilation plus real-time web search"

### **Live Application Demo (2.5 minutes)**

#### **Demo Scenario 1: Gift Acceptance (60 seconds)**
**Screen: Frontend chat interface**
- **User Context Setup**: Show role selection (Federal Employee, DOD, GS-14)
- **Query**: "Can I accept a $25 gift from a contractor my agency works with?"
- **Highlight Features**:
  - Real-time agentic processing
  - Simplified assessment with color-coded severity (RED - violation)
  - Expandable detailed analysis sections
  - Direct answer: "No, violates 5 CFR 2635.202"
  - Actionable next steps

#### **Demo Scenario 2: Document Upload (60 seconds)**
**Screen: Document management interface**
- **Upload Feature**: Upload a sample policy document
- **Show Processing**: Document parsing and vector indexing
- **Query with Context**: "Based on my company policy, what are the reporting requirements?"
- **Demonstrate**: How uploaded documents integrate with federal law retrieval

#### **Advanced Retrieval Showcase (30 seconds)**
**Screen: Backend logs or comparison results**
- **Show Strategy Selection**: Backend switching between similarity, MMR, Cohere rerank
- **Performance Highlight**: "MMR strategy achieves 7.98% better overall performance with 33% faithfulness improvement"
- **Explain Benefit**: "Balances relevance with diversity for comprehensive ethics coverage"

### **Technical Deep Dive (1 minute)**

#### **Retrieval Strategy Comparison (30 seconds)**
**Screen: RAGAS evaluation results table**
- **Performance Results**: 
  - Similarity (Baseline): 0.7234 overall score
  - MMR: 0.7811 overall score (+7.98% improvement)
  - Cohere Rerank: 0.7194 overall score (-0.55%)
- **Production Choice**: "MMR strategy deployed for optimal balance of relevance and faithfulness"

#### **Agentic Architecture (30 seconds)**
**Screen: LangGraph workflow or code**
- **Multi-Step Process**: Context collection → Planning → Retrieval → Web search → Assessment
- **Parallel Processing**: "3 concurrent web searches for current guidance"
- **Smart Context**: "User role and agency tailor the ethical guidance"

### **Impact & Future (45 seconds)**

#### **Value Proposition (25 seconds)**
- **Target Users**: "3+ million federal employees need ethics guidance"
- **Key Benefits**: 
  - Instant access to complex regulatory guidance
  - Severity assessment with clear penalties
  - Actionable reporting procedures
- **Demo Result**: "Comprehensive assessment in under 15 seconds"

#### **Future Enhancements (20 seconds)**
- **Hybrid Strategies**: "Combining MMR with semantic reranking for optimal performance"
- **Real-time Updates**: "Integration with government regulatory feeds"
- **Expert Review**: "Golden dataset enhancement with expert-curated Q&A"

### **Closing (30 seconds)**
- **Summary**: "Production-ready agentic RAG system with advanced retrieval strategies"
- **Certification Highlights**: "All 7 tasks completed with RAGAS evaluation and comprehensive documentation"
- **Call to Action**: "Ready for deployment to help federal employees maintain ethical standards"
- **GitHub**: "Complete code and documentation available in the repository"

---

## Demo Script Key Points

### **Technical Depth to Highlight**
1. **Advanced Retrieval**: 3 different strategies with performance metrics
2. **Agentic Architecture**: Multi-step reasoning with LangGraph
3. **Production Features**: Document upload, user context, severity assessment
4. **Evaluation Framework**: RAGAS metrics with quantified improvements

### **Use Case Scenarios**
1. **Gift Acceptance**: Clear violation with severity and penalties
2. **Conflicts of Interest**: Nuanced situation requiring comprehensive guidance
3. **Document Integration**: Show how custom policies enhance federal law

### **Performance Highlights**
- **7.98% overall improvement** with MMR retrieval strategy
- **33% faithfulness improvement** showing better grounding in source material
- **Sub-15 second** response times for complex queries with streaming UI
- **Production deployment** ready with Docker and document upload

### **Visual Elements to Show**
1. **Chat Interface**: Clean, professional federal design theme with streaming indicators
2. **Assessment Cards**: Color-coded severity with expandable sections and download feature
3. **Document Upload**: Drag-and-drop with processing visualization (fixed upload functionality)
4. **Performance Tables**: RAGAS comparison results showing MMR superiority
5. **Architecture Diagram**: System components and data flow (PNG version available)

### **Demo Environment Setup**
```bash
# Start the application
docker-compose up -d

# Verify services
curl http://localhost:8000/health
curl http://localhost:3000

# Have sample documents ready for upload
# Prepare 2-3 test scenarios with different complexities
```

### **Fallback Content**
- Screenshots of key features if live demo fails
- Pre-recorded snippets of complex agentic processing
- Performance comparison tables as backup slides

### **Success Metrics for Demo**
- ✅ Shows complete end-to-end functionality
- ✅ Demonstrates advanced retrieval strategies
- ✅ Highlights agentic multi-step reasoning
- ✅ Proves production readiness
- ✅ Explains technical architecture clearly
- ✅ Shows quantified performance improvements
- ✅ Stays within 5-minute limit