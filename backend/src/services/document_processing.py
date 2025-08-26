import uuid
import os
from typing import List, Dict, Any
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.node_parser import SentenceSplitter, SentenceWindowNodeParser

from rag.indexing import indexing_manager
# from llama_index.readers.file import PyMuPDFReader
from backend.database import db_manager
from config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.processed_documents = []

    async def process_multiple_documents(self, file_paths: List[str], filenames: List[str], indexing_strategy: str = "vector_store") -> Dict[str, Any]:
        """Process uploaded PDFs and store in vector database"""
        try:
            all_documents = []
            document_metadata = []

            # Process each file
            for file_path, filename in zip(file_paths, filenames):
                documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
                

                doc_id = str(uuid.uuid4())
                for doc in documents:
                    doc.metadata.update({
                        "filename": filename,
                        "document_id": doc_id,
                        "file_type": os.path.splitext(filename)[1][1:].lower(),
                        "file_path": file_path
                    })

                all_documents.extend(documents)

                # Store metadata
                document_metadata.append({
                    "document_id": doc_id,
                    "filename": filename,
                    "file_path": file_path,
                    "num_pages": len(documents),
                    "status": "processed",
                    "indexing_strategy": indexing_strategy
                })

            document = Document(text='\n\n'.join([doc.text for doc in all_documents]) if all_documents else None)


            # Create index using specified strategy
            index = await indexing_manager.create_index(document, indexing_strategy)

            # Store document metadata in MongoDB
            if document_metadata:
                await db_manager.collection.insert_many(document_metadata)
            

            total_chunks = self._calculate_total_chunks(document, indexing_strategy)

            
            
            logger.info(f"Successfully processed {len(filenames)} documents with {indexing_strategy} strategy")
            
            return {
                "status": "success",
                "processed_documents": len(filenames),
                "total_chunks": total_chunks,
                "indexing_strategy": indexing_strategy,
                "document_ids": [meta["document_id"] for meta in document_metadata]
            }
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise

    def _calculate_total_chunks(self, document: Document, strategy: str) -> int:
        """Calculate total number of chunks based on strategy"""
        if strategy == "vector_store":            
            splitter = SentenceSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            nodes = splitter.get_nodes_from_documents(document)
            return len(nodes)
        
        elif strategy == "sentence_window":
            # Use sentence window parser to estimate chunks
            parser = SentenceWindowNodeParser.from_defaults(window_size=3)
            nodes = parser.get_nodes_from_documents(document)
            return len(nodes)
        return 0
    
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