from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.core.node_parser import SentenceSplitter, SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import Document
from backend.database import db_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class IndexingStrategy:
    """Base class for different indexing strategies"""
    
    def __init__(self):
        # self.llm = OpenAI(
        #     model="gpt-3.5-turbo", 
        #     temperature=0.1,
        #     api_key=settings.OPENAI_API_KEY
        # )
        self.llm = Gemini(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            temperature=0.1
        )
        # self.embed_model = OpenAIEmbedding(
        #     model="text-embedding-ada-002",
        #     api_key=settings.OPENAI_API_KEY
        # )

        self.embed_model = GeminiEmbedding(
            api_key=settings.GEMINI_API_KEY,
            model_name="models/embedding-001"
        )
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embed_model
        )

class VectorStoreIndexing(IndexingStrategy):
    """Standard vector store indexing"""
    
    def __init__(self):
        super().__init__()
        self.strategy_name = "vector_store"
        self.node_parser = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
    
    async def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create vector store index from documents"""
        try:
            # Parse documents into nodes
            nodes = self.node_parser.get_nodes_from_documents(documents)
            
            # Get vector store for this strategy
            vector_store = db_manager.get_vector_store(self.strategy_name)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index
            index = VectorStoreIndex(
                nodes,
                storage_context=storage_context,
                service_context=self.service_context
            )
            
            logger.info(f"Created VectorStoreIndex with {len(nodes)} nodes in collection: {settings.VECTOR_STORE_COLLECTION}")
            return index
            
        except Exception as e:
            logger.error(f"Error creating vector store index: {str(e)}")
            raise

class SentenceWindowIndexing(IndexingStrategy):
    """Sentence window indexing for better context retrieval"""
    
    def __init__(self, window_size: int = None, window_metadata_key: str = "window"):
        super().__init__()
        self.strategy_name = "sentence_window"
        self.window_size = window_size or settings.SENTENCE_WINDOW_SIZE
        self.window_metadata_key = window_metadata_key
        self.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=self.window_size,
            window_metadata_key=window_metadata_key,
        )
    
    async def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create sentence window index from documents"""
        try:
            # Parse documents into sentence window nodes
            nodes = self.node_parser.get_nodes_from_documents(documents)
            
            # Get vector store for this strategy
            vector_store = db_manager.get_vector_store(self.strategy_name)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index
            index = VectorStoreIndex(
                nodes,
                storage_context=storage_context,
                service_context=self.service_context
            )
            
            logger.info(f"Created SentenceWindowIndex with {len(nodes)} nodes in collection: {settings.SENTENCE_WINDOW_COLLECTION}")
            return index
            
        except Exception as e:
            logger.error(f"Error creating sentence window index: {str(e)}")
            raise
    
    def get_postprocessor(self):
        """Get metadata replacement post-processor for sentence windows"""
        return MetadataReplacementPostProcessor(
            target_metadata_key=self.window_metadata_key
        )

class IndexingManager:
    """Manager class to handle different indexing strategies"""
    
    def __init__(self):
        self.strategies = {
            "vector_store": VectorStoreIndexing(),
            "sentence_window": SentenceWindowIndexing()
        }
        self.indexes = {}  # Store indexes for each strategy
        self.current_strategy = None
    
    async def create_index(self, documents: List[Document], strategy: str = "vector_store") -> VectorStoreIndex:
        """Create index using specified strategy"""
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")
        
        indexing_strategy = self.strategies[strategy]
        index = await indexing_strategy.create_index(documents)
        
        # Store the index
        self.indexes[strategy] = index
        self.current_strategy = strategy
        
        logger.info(f"Created and stored index using {strategy} strategy")
        return index
    
    def get_query_engine(self, strategy: str = None, similarity_top_k: int = 5):
        """Get query engine for specified strategy"""
        strategy_to_use = strategy or self.current_strategy
        
        if strategy_to_use not in self.indexes:
            raise ValueError(f"No index found for strategy: {strategy_to_use}. Available: {list(self.indexes.keys())}")
        
        index = self.indexes[strategy_to_use]
        
        if strategy_to_use == "sentence_window":
            # Add post-processor for sentence window strategy
            postprocessor = self.strategies["sentence_window"].get_postprocessor()
            return index.as_query_engine(
                similarity_top_k=similarity_top_k,
                node_postprocessors=[postprocessor]
            )
        else:
            return index.as_query_engine(similarity_top_k=similarity_top_k)
    
    def get_current_strategy(self) -> Optional[str]:
        """Get current indexing strategy"""
        return self.current_strategy
    
    def get_available_strategies(self) -> List[str]:
        """Get available indexing strategies"""
        return list(self.strategies.keys())
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about strategies and their collections"""
        return {
            "available_strategies": self.get_available_strategies(),
            "current_strategy": self.current_strategy,
            "created_indexes": list(self.indexes.keys()),
            "collections": db_manager.get_collection_info()
        }

# Global indexing manager
indexing_manager = IndexingManager()