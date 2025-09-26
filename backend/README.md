These route files provide all the necessary endpoints for your frontend to interact with your RAG system:

Document Endpoints:

POST /api/documents/upload - Upload and process documents
GET /api/documents/list - List all processed documents
DELETE /api/documents/{document_id} - Delete a document
GET /api/documents/strategies - Get available indexing strategies
QA Endpoints:

POST /api/qa/query - Ask questions about documents
POST /api/qa/compare - Compare results across strategies
GET /api/qa/strategies - Get available QA strategies