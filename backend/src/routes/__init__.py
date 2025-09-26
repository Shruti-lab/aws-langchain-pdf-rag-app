from fastapi import APIRouter
from routes import documents, qa

# Create main router
api_router = APIRouter()

# Include all route modules
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])