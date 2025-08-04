from typing import List, Optional, Literal
from langchain_core.documents import Document
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
try:
    from langchain_cohere import CohereRerank
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    CohereRerank = None
from langchain_qdrant import QdrantVectorStore

from .vector_store_service import VectorStoreService
from ..core.settings import settings
from ..core.logging_config import get_logger

logger = get_logger("app.services.advanced_retriever")

RetrievalStrategy = Literal["similarity", "cohere_rerank", "mmr", "hybrid"]


class AdvancedRetrieverService:
    """Service providing multiple retrieval strategies for ethics documents"""

    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service

        # Initialize Cohere reranker if available
        if COHERE_AVAILABLE and hasattr(settings, 'cohere_api_key'):
            try:
                self.cohere_rerank = CohereRerank(
                    model="rerank-v3.5",
                    cohere_api_key=settings.cohere_api_key,
                    top_k=settings.retrieval_top_k
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere reranker: {e}")
                self.cohere_rerank = None
        else:
            self.cohere_rerank = None

    def get_similarity_retriever(self, collection_name: str, top_k: int = 5):
        """Get basic similarity search retriever (current baseline strategy)"""
        try:
            if not self.vector_store_service.client:
                self.vector_store_service.initialize_client()

            vector_store = QdrantVectorStore(
                client=self.vector_store_service.client,
                collection_name=collection_name,
                embeddings=self.vector_store_service.embedding_model
            )

            return vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )

        except Exception as e:
            logger.error("Error creating similarity retriever", extra={"error": str(e)})
            raise

    def get_cohere_rerank_retriever(self, collection_name: str, top_k: int = 5, fetch_k: int = 20):
        """Get Cohere rerank retriever for improved relevance scoring"""
        if not COHERE_AVAILABLE or self.cohere_rerank is None:
            logger.warning("Cohere rerank not available, falling back to similarity search")
            return self.get_similarity_retriever(collection_name, top_k)

        try:
            # Get base similarity retriever that fetches more candidates
            base_retriever = self.get_similarity_retriever(collection_name, fetch_k)

            # Create Cohere rerank compressor
            cohere_compressor = CohereRerank(
                model="rerank-v3.5",
                cohere_api_key=settings.cohere_api_key,
                top_k=top_k
            )

            # Create rerank retriever
            rerank_retriever = ContextualCompressionRetriever(
                base_compressor=cohere_compressor,
                base_retriever=base_retriever
            )

            logger.info("Created Cohere rerank retriever", extra={
                "collection_name": collection_name,
                "fetch_k": fetch_k,
                "rerank_top_k": top_k
            })

            return rerank_retriever

        except Exception as e:
            logger.error("Error creating Cohere rerank retriever", extra={"error": str(e)})
            logger.warning("Falling back to similarity search")
            return self.get_similarity_retriever(collection_name, top_k)

    def get_mmr_retriever(self, collection_name: str, top_k: int = 5, diversity_lambda: float = 0.7):
        """Get MMR (Maximum Marginal Relevance) retriever for diversity"""
        try:
            if not self.vector_store_service.client:
                self.vector_store_service.initialize_client()

            vector_store = QdrantVectorStore(
                client=self.vector_store_service.client,
                collection_name=collection_name,
                embeddings=self.vector_store_service.embedding_model
            )

            return vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": top_k,
                    "lambda_mult": diversity_lambda,  # 0 = max diversity, 1 = max relevance
                    "fetch_k": min(top_k * 3, 20)  # Fetch more candidates for MMR selection
                }
            )

        except Exception as e:
            logger.error("Error creating MMR retriever", extra={"error": str(e)})
            raise

    def get_hybrid_retriever(self, collection_name: str, top_k: int = 5):
        """Get hybrid retriever combining similarity and MMR results"""
        try:
            # Get both retrievers
            similarity_retriever = self.get_similarity_retriever(collection_name, top_k)
            mmr_retriever = self.get_mmr_retriever(collection_name, top_k, diversity_lambda=0.6)

            # Create a custom hybrid retriever class
            class HybridRetriever:
                def __init__(self, sim_retriever, mmr_retriever, blend_ratio=0.6):
                    self.sim_retriever = sim_retriever
                    self.mmr_retriever = mmr_retriever
                    self.blend_ratio = blend_ratio  # Weight for similarity results

                def invoke(self, query: str):
                    # Get results from both retrievers
                    sim_docs = self.sim_retriever.invoke(query)
                    mmr_docs = self.mmr_retriever.invoke(query)

                    # Combine and deduplicate based on content
                    seen_content = set()
                    hybrid_docs = []

                    # First, add similarity results (weighted by blend_ratio)
                    sim_count = int(top_k * self.blend_ratio)
                    for doc in sim_docs[:sim_count]:
                        content_hash = hash(doc.page_content[:100])
                        if content_hash not in seen_content:
                            seen_content.add(content_hash)
                            hybrid_docs.append(doc)

                    # Then add MMR results to fill remaining slots
                    remaining_slots = top_k - len(hybrid_docs)
                    for doc in mmr_docs[:remaining_slots + 2]:  # Get a few extra in case of duplicates
                        content_hash = hash(doc.page_content[:100])
                        if content_hash not in seen_content and len(hybrid_docs) < top_k:
                            seen_content.add(content_hash)
                            hybrid_docs.append(doc)

                    return hybrid_docs[:top_k]

            hybrid_retriever = HybridRetriever(similarity_retriever, mmr_retriever)

            logger.info("Created hybrid retriever", extra={
                "collection_name": collection_name,
                "top_k": top_k,
                "blend_ratio": 0.6
            })

            return hybrid_retriever

        except Exception as e:
            logger.error("Error creating hybrid retriever", extra={"error": str(e)})
            raise

    def retrieve_documents(
        self,
        query: str,
        strategy: RetrievalStrategy = "hybrid",
        collection_name: Optional[str] = None,
        top_k: int = 5,
        **strategy_kwargs
    ) -> List[Document]:
        """Retrieve documents using specified strategy"""

        if collection_name is None:
            # Use default collection based on chunking strategy
            if settings.default_chunking_strategy == "semantic":
                collection_name = settings.semantic_collection_name
            else:
                collection_name = settings.collection_name

        try:
            if strategy == "similarity":
                retriever = self.get_similarity_retriever(collection_name, top_k)

            elif strategy == "cohere_rerank":
                # Fetch more candidates for reranking
                fetch_k = strategy_kwargs.get("fetch_k", top_k * 4)
                retriever = self.get_cohere_rerank_retriever(collection_name, top_k, fetch_k)

            elif strategy == "mmr":
                diversity_lambda = strategy_kwargs.get("diversity_lambda", 0.7)
                retriever = self.get_mmr_retriever(collection_name, top_k, diversity_lambda)

            elif strategy == "hybrid":
                retriever = self.get_hybrid_retriever(collection_name, top_k)

            else:
                raise ValueError(f"Unknown retrieval strategy: {strategy}")

            # Execute retrieval
            documents = retriever.invoke(query)

            logger.info("Document retrieval completed", extra={
                "strategy": strategy,
                "query": query[:100],  # Truncate long queries for logging
                "collection": collection_name,
                "documents_retrieved": len(documents),
                "requested_top_k": top_k
            })

            return documents

        except Exception as e:
            logger.error("Error in document retrieval", extra={
                "error": str(e),
                "strategy": strategy,
                "query": query[:100],
                "collection": collection_name
            })
            return []

    def compare_retrieval_strategies(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 5
    ) -> dict:
        """Compare both retrieval strategies for the same query"""

        results = {}
        strategies = ["similarity", "mmr"]

        for strategy in strategies:
            try:
                documents = self.retrieve_documents(
                    query=query,
                    strategy=strategy,
                    collection_name=collection_name,
                    top_k=top_k
                )

                # Calculate document metrics
                total_tokens = sum(len(doc.page_content.split()) for doc in documents)
                avg_doc_length = sum(len(doc.page_content) for doc in documents) / len(documents) if documents else 0

                # Extract sources for comparison
                sources = [doc.metadata.get('source', 'unknown') for doc in documents]
                unique_sources = len(set(sources))

                results[strategy] = {
                    "documents": documents,
                    "count": len(documents),
                    "total_tokens": total_tokens,
                    "avg_doc_length": round(avg_doc_length, 2),
                    "unique_sources": unique_sources,
                    "sources": sources
                }

            except Exception as e:
                logger.error(f"Error testing {strategy} strategy", extra={"error": str(e)})
                results[strategy] = {
                    "documents": [],
                    "count": 0,
                    "error": str(e)
                }

        # Log comparison summary
        logger.info("Retrieval strategy comparison completed", extra={
            "query": query[:100],
            "strategies_tested": len(results),
            "similarity_docs": results.get("similarity", {}).get("count", 0),
            "cohere_rerank_docs": results.get("cohere_rerank", {}).get("count", 0),
            "mmr_docs": results.get("mmr", {}).get("count", 0)
        })

        return results
