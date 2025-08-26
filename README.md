## System Architecture Overview
The system follows a microservices architecture with clear separation between frontend, backend, and database layers, implementing a RAG (Retrieval-Augmented Generation) pattern.



### Core Components & Their Roles
1. Document Processing Pipeline (LlamaIndex)
```
PDF Upload → Text Extraction → Chunking → Embedding → Vector Storage
```

2. Vector Database (MongoDB Atlas)
Vector Store: Stores document embeddings for semantic search
Metadata Collection: Stores document metadata and processing status
Search Index: Enables fast similarity search

3. RAG Pipeline (LangChain + LlamaIndex)
```
Query → Vector Search → Context Retrieval → LLM Response → Final Answer
```

Detailed Data Flow
Document Upload Flow
Frontend: User uploads PDF via React interface

API Gateway: FastAPI receives file upload at /api/documents/upload

Document Processing:


