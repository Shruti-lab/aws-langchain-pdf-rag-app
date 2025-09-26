from fastapi import APIRouter, UploadFile, Form, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from services.document_processing import document_processor
import os
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    indexing_strategy: str = Form("vector_store")
):
    """Upload multiple documents and process them with the specified indexing strategy"""
    try:
        # Validate indexing strategy
        if indexing_strategy not in ["vector_store", "sentence_window"]:
            raise HTTPException(status_code=400, detail=f"Unsupported indexing strategy: {indexing_strategy}")
        
        # Check if files are provided
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")
            
        # Check file types (only allow PDFs for now)
        for file in files:
            if not file.filename.lower().endswith(('.pdf', '.txt')):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save files to disk
        file_paths = []
        for file in files:
            file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            file_paths.append(file_path)
        
        # Process documents
        result = await document_processor.process_multiple_documents(
            file_paths=file_paths,
            filenames=[file.filename for file in files],
            indexing_strategy=indexing_strategy
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error during document upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents():
    """Get list of all processed documents"""
    try:
        documents = await document_processor.get_all_documents()
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete document by ID"""
    try:
        success = await document_processor.delete_document(document_id)
        if success:
            return {"status": "success", "message": f"Document {document_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_indexing_strategies():
    """Get available indexing strategies"""
    try:
        strategies = ["vector_store", "sentence_window"]
        return {"strategies": strategies}
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))