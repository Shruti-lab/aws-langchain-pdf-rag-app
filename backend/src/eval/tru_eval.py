from typing import Dict, Any, List, Optional
from trulens_eval import (
    Feedback,
    TruLlama,
    Tru
)
from trulens_eval.feedback import Groundedness

# from trulens_eval.feedback import Feedback, Groundedness
from trulens_eval.feedback.provider.openai import OpenAI
from trulens_eval.feedback.provider.litellm import LiteLLM
from trulens_eval.feedback.provider.google import Gemini

from trulens_eval.app import App
from rag.indexing import indexing_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TruLensEvaluator:
    """TruLens evaluation for different indexing strategies"""
    
    def __init__(self):
        self.tru = Tru()
        self.provider = None
        # self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)
        # self.litellm = LiteLLM(model_engine="gemini-pro", api_key=settings.LITELLM_API_KEY)
        self.initialize_provider("gemini")
        # self.feedback_functions = self._create_feedback_functions()
        self.recorders = {}
    
    def initialize_provider(self, provider: str = "gemini"):
        """Initialize feedback provider"""
        try: 
            if provider == "litellm":
                self.provider = LiteLLM(model_engine="gemini-pro", api_key=settings.LITELLM_API_KEY)
            elif provider == "openai":
                self.provider = OpenAI(api_key=settings.OPENAI_API_KEY)
            elif provider == "gemini":
                    # Direct Gemini integration if TruLens adds it
                    self.provider = Gemini(
                        api_key=settings.GEMINI_API_KEY,
                        model=settings.GEMINI_MODEL
                    )
                    logger.info(f"Initialized Gemini provider with model: {settings.GEMINI_MODEL}")
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        # Create feedback functions after provider is initialized
            self.feedback_functions = self._create_feedback_functions()
        except Exception as e:
            logger.error(f"Error initializing provider {provider}: {str(e)}")
            raise
        
        # self.openai_provider = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _create_feedback_functions(self) -> List[Feedback]:
        """Create feedback functions for evaluation"""
        # Groundedness feedback
        grounded = Groundedness(groundedness_provider=self.provider)
        qa_groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(TruLlama.select_source_nodes().node.text)
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )
        
        # Answer relevance feedback
        qa_relevance = (
            Feedback(self.provider.relevance_with_cot_reasons, name="Answer Relevance")
            .on_input_output()
        )
        
        # Context relevance feedback
        qs_relevance = (
            Feedback(self.provider.relevance_with_cot_reasons, name="Context Relevance")
            .on_input()
            .on(TruLlama.select_source_nodes().node.text)
            .aggregate(lambda x: sum(x) / len(x))
        )
        
        return [qa_groundedness, qa_relevance, qs_relevance]
    
    def create_recorder(self, strategy_name: str) -> TruLlama:
        """Create TruLens recorder for a specific indexing strategy"""
        try:
            query_engine = indexing_manager.get_query_engine()
            
            app_id = f"{strategy_name}_query_engine"
            
            tru_recorder = TruLlama(
                query_engine,
                app_id=app_id,
                feedbacks=self.feedback_functions
            )
            
            self.recorders[strategy_name] = tru_recorder
            logger.info(f"Created TruLens recorder for {strategy_name} strategy")
            
            return tru_recorder
            
        except Exception as e:
            logger.error(f"Error creating TruLens recorder: {str(e)}")
            raise

    
    async def evaluate_query(self, query: str, strategy_name: str) -> Dict[str, Any]:
        """Evaluate a single query with TruLens"""
        try:
            if strategy_name not in self.recorders:
                self.create_recorder(strategy_name)
            
            recorder = self.recorders[strategy_name]
            
            # Execute query with recording
            with recorder as recording:
                response = recorder.app.query(query)
            
            # Get the record
            record = recording.get()
            
            # Extract evaluation metrics
            metrics = {
                "query": query,
                "response": str(response),
                "strategy": strategy_name,
                "metrics": {}
            }
            
            # Get feedback scores
            for feedback in self.feedback_functions:
                feedback_name = feedback.name
                if hasattr(record, 'feedback_results'):
                    for fb_result in record.feedback_results:
                        if fb_result.name == feedback_name:
                            metrics["metrics"][feedback_name] = {
                                "score": fb_result.result,
                                "reason": getattr(fb_result, 'reason', None)
                            }
            
            logger.info(f"Evaluated query with {strategy_name} strategy")
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating query: {str(e)}")
            raise

    
    async def compare_strategies(self, query: str, strategies: List[str]) -> Dict[str, Any]:
        """Compare multiple indexing strategies for the same query"""
        try:
            results = {}
            
            for strategy in strategies:
                # Ensure we have the right index for this strategy
                if indexing_manager.get_current_strategy() != strategy:
                    logger.warning(f"Current strategy {indexing_manager.get_current_strategy()} doesn't match {strategy}")
                    continue
                
                result = await self.evaluate_query(query, strategy)
                results[strategy] = result
            
            # Calculate comparison metrics
            comparison = {
                "query": query,
                "strategies_compared": strategies,
                "results": results,
                "summary": self._create_comparison_summary(results)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing strategies: {str(e)}")
            raise
    
    # def _create_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
    #     """Create summary comparing different strategies"""
    #     summary = {
    #         "best_groundedness": {"strategy": None, "score": -1},
    #         "best_answer_relevance": {"strategy": None, "score": -1},
    #         "best_context_relevance": {"strategy": None, "score": -1}
    #     }
        
    #     for strategy, result in results.items():
    #         metrics = result.get("metrics", {})
            
    #         # Check Groundedness
    #         if "Groundedness" in metrics:
    #             score = metrics["Groundedness"].get("score", 0)
    #             if score > summary["best_groundedness"]["score"]:
    #                 summary["best_groundedness"] = {"strategy": strategy, "score": score}
            
    #         # Check Answer Relevance
    #         if "Answer Relevance" in metrics:
    #             score = metrics["Answer Relevance"].get("score", 0)
    #             if score > summary["best_answer_relevance"]["score"]:
    #                 summary["best_answer_relevance"] = {"strategy": strategy, "score": score}
            
    #         # Check Context Relevance
    #         if "Context Relevance" in metrics:
    #             score = metrics["Context Relevance"].get("score", 0)
    #             if score > summary["best_context_relevance"]["score"]:
    #                 summary["best_context_relevance"] = {"strategy": strategy, "score": score}
        
    #     return summary
    
    def reset_database(self):
        """Reset TruLens database"""
        self.tru.reset_database()
        logger.info("TruLens database reset")
    
    # def get_leaderboard(self) -> Dict[str, Any]:
    #     """Get TruLens leaderboard data"""
    #     try:
    #         leaderboard = self.tru.get_leaderboard()
    #         return leaderboard.to_dict() if hasattr(leaderboard, 'to_dict') else {}
    #     except Exception as e:
    #         logger.error(f"Error getting leaderboard: {str(e)}")
    #         return {}

# Global evaluator instance
trulens_evaluator = TruLensEvaluator()