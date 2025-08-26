import motor.motor_asyncio
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
class DatabaseManager:
    def __initi__(self):
        self.client = None
        self.database = None

        # Collections for different strategies
        self.vector_store_collection = None
        self.sentence_window_collection = None
        self.metadata_collection = None
        

    async def connect(self):
        """Connect to MongoDB and initialize the vector store and index."""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
            self.database = self.client[settings.DATABASE_NAME]
            
            # Initialize collections
            self.vector_store_collection = self.database[settings.VECTOR_STORE_COLLECTION]
            self.sentence_window_collection = self.database[settings.SENTENCE_WINDOW_COLLECTION]
            
            logger.info("Connected to MongoDB collections")


            # To Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            

            # Initialize the vector store
            self.vector_store = MongoDBAtlasVectorSearch(
                mongo_client=self.client,
                index_name=settings.INDEX_NAME,
                database_name=settings.DATABASE_NAME,
                collection_name=settings.COLLECTION_NAME,
            )
            
            logger.info("Initialized MongoDB Atlas Vector Search")

            # Create storage context and index
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.index = VectorStoreIndex([], storage_context=storage_context)
            logger.info("Vector Store Index created")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise