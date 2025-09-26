from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.qa_service import qa_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    strategy: str = "vector_store"
    similarity_top_k: int = 5
    enable_evaluation: bool = False

class CompareStrategiesRequest(BaseModel):
    question: str
    strategies: List[str] = ["vector_store", "sentence_window"]
    similarity_top_k: int = 5

@router.post("/query")
async def query_documents(query_request: QueryRequest):
    """Query documents with specified strategy"""
    try:
        result = await qa_service.query(
            question=query_request.question,
            strategy=query_request.strategy,
            similarity_top_k=query_request.similarity_top_k,
            enable_evaluation=query_request.enable_evaluation
        )
        return result
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_strategies(compare_request: CompareStrategiesRequest):
    """Compare query results across different strategies"""
    try:
        result = await qa_service.compare_strategies_query(
            question=compare_request.question,
            strategies=compare_request.strategies,
            similarity_top_k=compare_request.similarity_top_k
        )
        return result
    except Exception as e:
        logger.error(f"Error comparing strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_available_strategies():
    """Get list of available indexing strategies"""
    try:
        strategies = qa_service.get_available_strategies()
        return {"strategies": strategies, "current": qa_service.get_current_strategy()}
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))