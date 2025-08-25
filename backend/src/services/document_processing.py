import uuid
from typing import List, Dict, Any
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PyMuPDFReader
from backend.database import db_manager
from config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.node_parser = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    async def process_pdf(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process uploaded PDF and store in vector database"""
        try:
            # Read PDF
            reader = PyMuPDFReader()
            documents = reader.load_data(file_path)
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "filename": filename,
                    "document_id": str(uuid.uuid4()),
                    "file_type": "pdf"
                })
            
            # Parse into nodes
            nodes = self.node_parser.get_nodes_from_documents(documents)
            
            # Insert into vector store
            await db_manager.index.insert_nodes(nodes)
            
            # Store document metadata in MongoDB
            doc_metadata = {
                "document_id": documents[0].metadata["document_id"],
                "filename": filename,
                "file_path": file_path,
                "num_pages": len(documents),
                "num_chunks": len(nodes),
                "status": "processed"
            }
            
            await db_manager.collection.insert_one(doc_metadata)
            
            logger.info(f"Successfully processed document: {filename}")
            
            return {
                "document_id": documents[0].metadata["document_id"],
                "filename": filename,
                "num_chunks": len(nodes),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get list of all processed documents"""
        try:
            cursor = db_manager.collection.find({}, {"_id": 0})
            documents = await cursor.to_list(length=None)
            return documents
        except Exception as e:
            logger.error(f"Error fetching documents: {str(e)}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from vector store and metadata"""
        try:
            # Delete from metadata collection
            result = await db_manager.collection.delete_one({"document_id": document_id})
            
            if result.deleted_count > 0:
                logger.info(f"Successfully deleted document: {document_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False

document_processor = DocumentProcessor()