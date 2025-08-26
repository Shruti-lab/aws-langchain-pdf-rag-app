from typing import Dict, Any, List, Optional
from rag.indexing import indexing_manager
from eval.trulens_evaluator import trulens_evaluator
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class QAService:
    """Question-Answering service with multiple indexing strategies and evaluation"""
    
    def __init__(self):
        self.current_strategy = None
    
    async def query(
        self, 
        question: str, 
        strategy: str = "vector_store",
        similarity_top_k: int = 5,
        enable_evaluation: bool = False
    ) -> Dict[str, Any]:
        """Query documents with specified strategy"""
        try:
            # Check if we need to switch strategy
            if indexing_manager.get_current_strategy() != strategy:
                raise ValueError(f"Index not available for strategy: {strategy}. Current: {indexing_manager.get_current_strategy()}")
            
            # Get query engine
            query_engine = indexing_manager.get_query_engine(similarity_top_k)
            
            if enable_evaluation:
                # Use TruLens evaluation
                evaluation_result = await trulens_evaluator.evaluate_query(question, strategy)
                return evaluation_result
            else:
                # Direct query without evaluation
                response = query_engine.query(question)
                
                # Extract source information
                sources = []
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    sources = [
                        {
                            "filename": node.metadata.get("filename", "Unknown"),
                            "document_id": node.metadata.get("document_id", "Unknown"),
                            "score": getattr(node, 'score', 0.0),
                            "text_snippet": node.text[:200] + "..." if len(node.text) > 200 else node.text
                        }
                        for node in response.source_nodes
                    ]
                
                return {
                    "answer": str(response),
                    "sources": sources,
                    "strategy": strategy,
                    "evaluation_enabled": False
                }
                
        except Exception as e:
            logger.error(f"Error during query: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "strategy": strategy,
                "error": str(e)
            }
    
    async def compare_strategies_query(
        self, 
        question: str, 
        strategies: List[str],
        similarity_top_k: int = 5
    ) -> Dict[str, Any]:
        """Compare query results across different strategies"""
        try:
            comparison_result = await trulens_evaluator.compare_strategies(question, strategies)
            return comparison_result
            
        except Exception as e:
            logger.error(f"Error comparing strategies: {str(e)}")
            return {
                "error": str(e),
                "query": question,
                "strategies": strategies
            }
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available indexing strategies"""
        return list(indexing_manager.strategies.keys())
    
    def get_current_strategy(self) -> Optional[str]:
        """Get current active strategy"""
        return indexing_manager.get_current_strategy()

qa_service = QAService()