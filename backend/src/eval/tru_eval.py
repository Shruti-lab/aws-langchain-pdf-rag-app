from typing import Dict, Any, List, Optional
from trulens_eval import Tru, TruLlama
from trulens_eval.feedback import Feedback, Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as OpenAIProvider
from trulens_eval.app import App
from rag.indexing import indexing_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TruLensEvaluator:
    """TruLens evaluation for different indexing strategies"""
    
    def __init__(self):
        self.tru = Tru()
        self.tru.reset_database()
        self.openai_provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        self.feedback_functions = self._create_feedback_functions()
        self.recorders = {}
    
    def _create_feedback_functions(self) -> List[Feedback]:
        """Create feedback functions for evaluation"""
        # Groundedness feedback
        grounded = Groundedness(groundedness_provider=self.openai_provider)
        f_groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(TruLlama.select_source_nodes().node.text.collect())
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )
        
        # Answer relevance feedback
        f_answer_relevance = (
            Feedback(self.openai_provider.relevance_with_cot_reasons, name="Answer Relevance")
            .on_input_output()
        )
        
        # Context relevance feedback
        f_context_relevance = (
            Feedback(self.openai_provider.context_relevance_with_cot_reasons, name="Context Relevance")
            .on_input()
            .on(TruLlama.select_source_nodes().node.text)
            .aggregate(lambda x: sum(x) / len(x))
        )
        
        return [f_groundedness, f_answer_relevance, f_context_relevance]
    
    def create_recorder(self, strategy_name: str) -> TruLlama:
        """Create TruLens recorder for a specific indexing strategy"""
        try:
            query_engine = indexing_manager.get_query_engine()
            
            app_id = f"{strategy_name}_query_engine"
            
            recorder = TruLlama(
                query_engine,
                app_id=app_id,
                feedbacks=self.feedback_functions
            )
            
            self.recorders[strategy_name] = recorder
            logger.info(f"Created TruLens recorder for {strategy_name} strategy")
            
            return recorder
            
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
    
    def _create_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary comparing different strategies"""
        summary = {
            "best_groundedness": {"strategy": None, "score": -1},
            "best_answer_relevance": {"strategy": None, "score": -1},
            "best_context_relevance": {"strategy": None, "score": -1}
        }
        
        for strategy, result in results.items():
            metrics = result.get("metrics", {})
            
            # Check Groundedness
            if "Groundedness" in metrics:
                score = metrics["Groundedness"].get("score", 0)
                if score > summary["best_groundedness"]["score"]:
                    summary["best_groundedness"] = {"strategy": strategy, "score": score}
            
            # Check Answer Relevance
            if "Answer Relevance" in metrics:
                score = metrics["Answer Relevance"].get("score", 0)
                if score > summary["best_answer_relevance"]["score"]:
                    summary["best_answer_relevance"] = {"strategy": strategy, "score": score}
            
            # Check Context Relevance
            if "Context Relevance" in metrics:
                score = metrics["Context Relevance"].get("score", 0)
                if score > summary["best_context_relevance"]["score"]:
                    summary["best_context_relevance"] = {"strategy": strategy, "score": score}
        
        return summary
    
    def reset_database(self):
        """Reset TruLens database"""
        self.tru.reset_database()
        logger.info("TruLens database reset")
    
    def get_leaderboard(self) -> Dict[str, Any]:
        """Get TruLens leaderboard data"""
        try:
            leaderboard = self.tru.get_leaderboard()
            return leaderboard.to_dict() if hasattr(leaderboard, 'to_dict') else {}
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return {}

# Global evaluator instance
trulens_evaluator = TruLensEvaluator()