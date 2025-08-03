import time
from typing import Dict, Any, List
from langgraph.graph import START, StateGraph

from ..models.state_models import ParallelEthicsState
from ..models.chat_models import UserContext, ChatRequest, ChatResponse, SearchResult
from .document_loader_service import DocumentLoaderService
from .vector_store_service import VectorStoreService
from .web_search_service import WebSearchService
from .planning_agent_service import PlanningAgentService
from .ethics_assessment_service import EthicsAssessmentService
from ..core.logging_config import get_logger

logger = get_logger("app.services.agentic_workflow")


class AgenticWorkflowService:
    """Orchestrates the parallel agentic workflow for ethics consultation"""
    
    def __init__(self):
        # Initialize all services
        self.document_loader = DocumentLoaderService()
        self.vector_store = VectorStoreService()
        self.web_search = WebSearchService()
        self.planning_agent = PlanningAgentService()
        self.ethics_assessor = EthicsAssessmentService()
        
        # Initialize vector store and load documents
        self._initialize_knowledge_base()
        
        # Build workflow graph
        self.workflow_graph = self._build_workflow_graph()
    
    def _initialize_knowledge_base(self):
        """Load ethics documents into vector store collections"""
        try:
            from ..core.settings import settings
            
            # Load base documents
            base_documents = self.document_loader.load_ethics_documents()
            
            if not base_documents:
                logger.warning("No documents loaded - using empty knowledge base")
                return
            
            # Initialize collections based on settings
            if settings.generate_both_collections:
                logger.info("Initializing both character and semantic collections")
                
                # Character-based collection
                char_chunks = self.document_loader.split_documents(base_documents)
                self.vector_store.create_collection(settings.collection_name)
                self.vector_store.index_documents(char_chunks, settings.collection_name)
                logger.info("Character collection initialized", extra={"document_count": len(char_chunks)})
                
                # Semantic collection
                semantic_chunks = self.document_loader.semantic_split_documents(base_documents)
                self.vector_store.create_collection(settings.semantic_collection_name)
                self.vector_store.index_documents(semantic_chunks, settings.semantic_collection_name)
                logger.info("Semantic collection initialized", extra={"document_count": len(semantic_chunks)})
                
            else:
                # Use default strategy
                if settings.default_chunking_strategy == "semantic":
                    chunks = self.document_loader.load_and_semantic_split_documents()
                    collection_name = settings.semantic_collection_name
                else:
                    chunks = self.document_loader.load_and_split_documents()
                    collection_name = settings.collection_name
                
                self.vector_store.create_collection(collection_name)
                self.vector_store.index_documents(chunks, collection_name)
                logger.info(f"Knowledge base initialized with {settings.default_chunking_strategy} chunking", 
                           extra={"document_count": len(chunks), "collection": collection_name})
                
        except Exception as e:
            logger.error("Error initializing knowledge base", extra={"error": str(e)})
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the parallel agentic workflow graph"""
        
        # Create workflow nodes
        def collect_user_context(state: ParallelEthicsState) -> ParallelEthicsState:
            """Process user context (already provided in request)"""
            return state
        
        def create_search_plan(state: ParallelEthicsState) -> ParallelEthicsState:
            """Generate research strategy using planning agent"""
            search_plan = self.planning_agent.create_search_plan(
                state["question"], 
                state.get("user_context", {})
            )
            return {"search_plan": search_plan}
        
        def retrieve_federal_knowledge(state: ParallelEthicsState) -> ParallelEthicsState:
            """Retrieve relevant federal ethics documents from active collection"""
            from ..core.settings import settings
            
            # Use the active collection based on default strategy
            if settings.default_chunking_strategy == "semantic":
                collection_name = settings.semantic_collection_name
            else:
                collection_name = settings.collection_name
                
            documents = self.vector_store.similarity_search(
                state["question"], 
                k=settings.retrieval_top_k,
                collection_name=collection_name
            )
            return {"context": documents}
        
        def search_general_guidance(state: ParallelEthicsState) -> ParallelEthicsState:
            """Search for general ethics guidance (parallel node 1)"""
            results = self.web_search.search_general_guidance(state["question"])
            return {"general_web_results": results}
        
        def search_penalty_information(state: ParallelEthicsState) -> ParallelEthicsState:
            """Search for penalty information (parallel node 2)"""
            results = self.web_search.search_penalty_information(state["question"])
            return {"penalty_web_results": results}
        
        def search_current_guidance(state: ParallelEthicsState) -> ParallelEthicsState:
            """Search for current guidance (parallel node 3)"""
            results = self.web_search.search_current_guidance(state["question"])
            return {"guidance_web_results": results}
        
        def combine_search_results(state: ParallelEthicsState) -> ParallelEthicsState:
            """Combine all parallel search results"""
            all_results = (
                state.get("general_web_results", []) +
                state.get("penalty_web_results", []) +
                state.get("guidance_web_results", [])
            )
            return {"web_results": all_results}
        
        def assess_ethics_violation(state: ParallelEthicsState) -> ParallelEthicsState:
            """Generate comprehensive ethics assessment"""
            # Prepare context strings
            federal_context = "\\n\\n".join([doc.page_content for doc in state.get("context", [])])
            general_results = str(state.get("general_web_results", []))
            penalty_results = str(state.get("penalty_web_results", []))
            guidance_results = str(state.get("guidance_web_results", []))
            
            # Generate markdown assessment
            logger.info("Generating markdown assessment", extra={"question_length": len(state["question"])})
            assessment = self.ethics_assessor.assess_ethics_scenario(
                question=state["question"],
                search_plan=state.get("search_plan", ""),
                user_context=state.get("user_context", {}),
                federal_context=federal_context,
                general_results=general_results,
                penalty_results=penalty_results,
                guidance_results=guidance_results
            )
            logger.info("Assessment generated successfully", extra={"assessment_length": len(assessment)})
            
            return {"response": assessment}
        
        def finalize_response(state: ParallelEthicsState) -> ParallelEthicsState:
            """Finalize response and calculate processing time"""
            # Calculate processing time
            start_time = state.get("processing_start_time", time.time())
            processing_time = time.time() - start_time
            
            return {
                "processing_time_seconds": processing_time
            }
        
        # Build the graph
        graph_builder = StateGraph(ParallelEthicsState)
        
        # Add nodes
        graph_builder.add_node("collect_context", collect_user_context)
        graph_builder.add_node("create_plan", create_search_plan)
        graph_builder.add_node("retrieve_knowledge", retrieve_federal_knowledge)
        graph_builder.add_node("search_general", search_general_guidance)
        graph_builder.add_node("search_penalties", search_penalty_information)
        graph_builder.add_node("search_guidance", search_current_guidance)
        graph_builder.add_node("combine_results", combine_search_results)
        graph_builder.add_node("assess_violation", assess_ethics_violation)
        graph_builder.add_node("finalize", finalize_response)
        
        # Define workflow edges
        graph_builder.add_edge(START, "collect_context")
        graph_builder.add_edge("collect_context", "create_plan")
        graph_builder.add_edge("create_plan", "retrieve_knowledge")
        
        # Parallel search phase
        graph_builder.add_edge("retrieve_knowledge", "search_general")
        graph_builder.add_edge("retrieve_knowledge", "search_penalties")
        graph_builder.add_edge("retrieve_knowledge", "search_guidance")
        
        # Synchronization point
        graph_builder.add_edge("search_general", "combine_results")
        graph_builder.add_edge("search_penalties", "combine_results")
        graph_builder.add_edge("search_guidance", "combine_results")
        
        # Final assessment and finalization
        graph_builder.add_edge("combine_results", "assess_violation")
        graph_builder.add_edge("assess_violation", "finalize")
        
        return graph_builder.compile()
    
    def process_ethics_consultation(self, request: ChatRequest) -> ChatResponse:
        """Process ethics consultation request through agentic workflow"""
        start_time = time.time()
        
        try:
            # Prepare initial state
            initial_state: ParallelEthicsState = {
                "question": request.question,
                "user_context": request.user_context.dict() if request.user_context else {},
                "search_plan": None,
                "context": [],
                "general_web_results": [],
                "penalty_web_results": [],
                "guidance_web_results": [],
                "web_results": [],
                "response": "",
                "processing_start_time": start_time,
                "processing_time_seconds": None
            }
            
            # Execute workflow
            final_state = self.workflow_graph.invoke(initial_state)
            
            # Convert search results to response format
            search_results = [
                SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    score=result.get("score")
                )
                for result in final_state.get("web_results", [])
            ]
            
            # Build response
            response = ChatResponse(
                question=request.question,
                response=final_state.get("response", ""),
                federal_law_sources=len(final_state.get("context", [])),
                web_sources=len(final_state.get("web_results", [])),
                search_results=search_results,
                processing_time_seconds=final_state.get("processing_time_seconds"),
                search_plan=final_state.get("search_plan")
            )
            
            return response
            
        except Exception as e:
            logger.error("Error in agentic workflow", extra={"error": str(e), "question": request.question})
            return ChatResponse(
                question=request.question,
                response=f"I apologize, but I encountered an error processing your ethics consultation: {str(e)}",
                processing_time_seconds=time.time() - start_time
            )