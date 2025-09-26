import motor.motor_asyncio
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from config import settings
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
class DatabaseManager:
    def __init__(self):  # Fixed typo from __initi__
        self.client = None
        self.database = None

        # Collections for different strategies
        self.vector_store_collection = None
        self.sentence_window_collection = None
        self.metadata_collection = None
        
        # Vector stores for different strategies
        self.vector_stores = {}

    async def connect(self):
        """Connect to MongoDB and initialize the vector store and index."""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
            self.database = self.client[settings.DATABASE_NAME]
            
            # Initialize collections
            self.vector_store_collection = self.database[settings.VECTOR_STORE_COLLECTION]
            self.sentence_window_collection = self.database[settings.SENTENCE_WINDOW_COLLECTION]
            self.metadata_collection = self.database[settings.METADATA_COLLECTION]
            
            logger.info("Connected to MongoDB collections")

            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Initialize vector stores for different strategies
            await self._initialize_vector_stores()
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    async def _initialize_vector_stores(self):
        """Initialize vector stores for different indexing strategies"""
        try:
            # Vector Store strategy
            self.vector_stores["vector_store"] = MongoDBAtlasVectorSearch(
                mongo_client=self.client,
                database_name=settings.DATABASE_NAME,
                collection_name=settings.VECTOR_STORE_COLLECTION,
                index_name=settings.VECTOR_STORE_INDEX,
            )
            logger.info("Initialized Vector Store collection")
            
            # Sentence Window strategy
            self.vector_stores["sentence_window"] = MongoDBAtlasVectorSearch(
                mongo_client=self.client,
                database_name=settings.DATABASE_NAME,
                collection_name=settings.SENTENCE_WINDOW_COLLECTION,
                index_name=settings.SENTENCE_WINDOW_INDEX,
            )
            logger.info("Initialized Sentence Window collection")
            
        except Exception as e:
            logger.error(f"Error initializing vector stores: {e}")
            raise
    
    def get_vector_store(self, strategy: str) -> MongoDBAtlasVectorSearch:
        """Get vector store for specific strategy"""
        if strategy not in self.vector_stores:
            raise ValueError(f"Unknown strategy: {strategy}")
        return self.vector_stores[strategy]
    
    def get_collection_info(self) -> Dict[str, Dict[str, str]]:
        """Get collection information for different strategies"""
        return {
            "vector_store": {
                "collection": settings.VECTOR_STORE_COLLECTION,
                "index": settings.VECTOR_STORE_INDEX
            },
            "sentence_window": {
                "collection": settings.SENTENCE_WINDOW_COLLECTION,
                "index": settings.SENTENCE_WINDOW_INDEX
            },
            "metadata": {
                "collection": settings.METADATA_COLLECTION
            }
        }

    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    async def clear_collection(self, strategy: str):
        """Clear specific strategy collection"""
        try:
            if strategy == "vector_store":
                await self.vector_store_collection.delete_many({})
            elif strategy == "sentence_window":
                await self.sentence_window_collection.delete_many({})
            
            logger.info(f"Cleared {strategy} collection")
        except Exception as e:
            logger.error(f"Error clearing {strategy} collection: {e}")
            raise

# Global database instance
db_manager = DatabaseManager()