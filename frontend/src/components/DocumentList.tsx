import { useState, useEffect } from 'react';
import { documentService, type Document } from '../services/api';

interface DocumentListProps {
  onDelete: () => void;
  refresh: boolean;
}

export const DocumentList = ({ onDelete, refresh }: DocumentListProps) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await documentService.listDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setError('Failed to load documents.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refresh]);

  const handleDelete = async (documentId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await documentService.deleteDocument(documentId);
        fetchDocuments();
        onDelete();
      } catch (error) {
        console.error('Failed to delete document:', error);
        setError('Failed to delete document.');
      }
    }
  };

  if (isLoading) {
    return <div className="p-4 text-center">Loading documents...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">{error}</div>;
  }

  if (documents.length === 0) {
    return <div className="p-4 text-center">No documents uploaded yet.</div>;
  }

  return (
    <div className="document-list">
      <h2 className="text-xl font-semibold mb-4">Uploaded Documents</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filename</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.document_id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.filename}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {doc.indexing_strategy === 'vector_store' ? 'Vector Store' : 'Sentence Window'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    doc.status === 'processed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {doc.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => handleDelete(doc.document_id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};