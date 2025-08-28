import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # Load environment variables from .env file

class Settings(BaseSettings):   
    # API Settings
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = os.environ.get("API_PORT", 8080)
    DEBUG: bool = os.environ.get("DEBUG", "True") == "True"

    # OpenAI
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")
    LITELLM_API_KEY: str = os.environ.get("LITELLM_API_KEY", "your_litellm_api_key_here")   

    # MongoDB
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.environ.get("DATABASE_NAME", "mydatabase")
    
    # Collections for different indexing strategies
    VECTOR_STORE_COLLECTION_NAME: str = os.environ.get("VECTOR_STORE_COLLECTION_NAME", "vector_store_docs")
    SENTENCE_WINDOW_COLLECTION: str = os.environ.get("SENTENCE_WINDOW_COLLECTION", "sentence_window_docs")
    
    # Vector Search Indexes
    VECTOR_STORE_INDEX: str = os.getenv("VECTOR_STORE_INDEX", "vector_store_index")
    SENTENCE_WINDOW_INDEX: str = os.getenv("SENTENCE_WINDOW_INDEX", "sentence_window_index")
    

    # File upload
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "./uploads")
    ALLOWED_FILE_TYPES: str = os.environ.get("ALLOWED_FILE_TYPES", ".txt,.pdf,.docx")   
    MAX_FILE_SIZE_MB: int = int(os.environ.get("MAX_FILE_SIZE_MB", 52428800))

    # CORS
    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

    # Document processing
    CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", 1024))
    CHUNK_OVERLAP: int = int(os.environ.get("CHUNK_OVERLAP", 200))
    SENTENCE_WINDOW_SIZE: int = int(os.getenv("SENTENCE_WINDOW_SIZE", 3))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

